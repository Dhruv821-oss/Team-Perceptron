from utils import fetch_live_data, compute_features, predict_regime
import pandas as pd

UNIVERSE = [
    "TCS.NS", "INFY.NS", "RELIANCE.NS", "HDFCBANK.NS",
    "ICICIBANK.NS", "ITC.NS", "AXISBANK.NS"
]

def scan_universe():
    rows = []

    for symbol in UNIVERSE:
        df = fetch_live_data(symbol)
        df = compute_features(df)
        df = predict_regime(df)

        if df.empty:
            continue

        last = df.iloc[-1]

        rows.append({
            "symbol": symbol,
            "price": round(last["Close"], 2),
            "regime": last["market_state"],
            "momentum": round(df["return"].rolling(20).mean().iloc[-1], 4),
            "volatility": round(last["volatility"], 4),
            "trend": round(last["ma_short"] - last["ma_long"], 2)
        })

    universe_df = pd.DataFrame(rows)

    universe_df["score"] = (
        0.6 * universe_df["momentum"]
        - 0.3 * universe_df["volatility"]
        + 0.1 * universe_df["trend"]
    )

    universe_df = universe_df.sort_values("score", ascending=False)
    return universe_df
