import pandas as pd
import numpy as np
import yfinance as yf
import joblib

# ======================================================
# LOAD TRAINED MODEL ARTIFACTS
# ======================================================
model = joblib.load("market_state_model.pkl")
scaler = joblib.load("scaler.pkl")
encoder = joblib.load("label_encoder.pkl")

# ======================================================
# CONFIG
# ======================================================
VOL_WINDOW = 20
SHORT_MA = 20
LONG_MA = 50

FEATURES = [
    "return",
    "volatility",
    "ma_short",
    "ma_long",
    "drawdown"
]

# ======================================================
# LIVE DATA INGESTION (ROBUST)
# ======================================================
def fetch_live_data(symbol, period="6mo"):
    try:
        df = yf.download(
            symbol,
            period=period,
            progress=False,
            auto_adjust=False
        )

        # 🔥 CRITICAL: flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()

        # Ensure required columns exist
        required = {"Date", "Close", "Volume"}
        if not required.issubset(df.columns):
            return pd.DataFrame()

        return df[["Date", "Close", "Volume"]]

    except Exception as e:
        print("⚠️ FETCH ERROR:", e)
        return pd.DataFrame()

# ======================================================
# FEATURE ENGINEERING (NO LEAKAGE, LIVE SAFE)
# ======================================================
def compute_features(df):
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.sort_values("Date").copy()

    # 🔥 FORCE SERIES (prevents DataFrame assignment bugs)
    close = df["Close"].astype(float)

    df["return"] = close.pct_change()

    df["volatility"] = (
        df["return"].rolling(VOL_WINDOW).std() * np.sqrt(252)
    )

    df["ma_short"] = close.rolling(SHORT_MA).mean()
    df["ma_long"] = close.rolling(LONG_MA).mean()

    rolling_max = close.cummax()
    df["drawdown"] = (close - rolling_max) / rolling_max

    df.dropna(inplace=True)
    return df

# ======================================================
# ML REGIME DETECTION (BULLETPROOF)
# ======================================================
def predict_regime(df):
    if df is None or df.empty:
        return df

    X = df[FEATURES].copy()

    # 🔥 SAFE FEATURE ALIGNMENT (NO ASSERTS)
    expected = list(scaler.feature_names_in_)
    for col in expected:
        if col not in X.columns:
            return df

    X = X[expected]
    X_scaled = scaler.transform(X)

    preds = model.predict(X_scaled)

    # 🔥 STANDARD COLUMN NAME (USED EVERYWHERE)
    df["market_state"] = encoder.inverse_transform(preds)

    return df

# ======================================================
# ALLOCATION ENGINE
# ======================================================
def allocate(df):
    allocation_map = {
        "Crash": 0.0,
        "High Volatility": 0.3,
        "Calm Bear": 0.5,
        "Calm Bull": 1.0
    }

    latest = df.iloc[-1]
    regime = latest["market_state"]

    equity = allocation_map.get(regime, 0.0)

    return {
        "Detected Regime": regime,
        "Equity Allocation": f"{equity * 100:.0f}%",
        "Cash Allocation": f"{(1 - equity) * 100:.0f}%"
    }

# ======================================================
# BEST STOCK SELECTION (FAIL-SAFE)
# ======================================================
def pick_best_stock(stock_dfs, market_regime):
    scores = []

    for symbol, df in stock_dfs.items():
        if df is None or df.empty:
            continue

        latest = df.iloc[-1]

        momentum = df["return"].rolling(20).mean().iloc[-1]
        volatility = df["volatility"].iloc[-1]
        trend = latest["ma_short"] - latest["ma_long"]

        if market_regime == "Crash":
            continue

        score = (
            0.6 * momentum
            - 0.3 * volatility
            + 0.1 * trend
        )

        scores.append({
            "symbol": symbol,
            "score": score
        })

    # 🔥 HARD FALLBACK (NEVER FAILS)
    if not scores:
        fallback = list(stock_dfs.keys())[0]
        return fallback, pd.DataFrame()

    score_df = pd.DataFrame(scores).sort_values(
        "score", ascending=False
    )

    return score_df.iloc[0]["symbol"], score_df
