import pandas as pd
import numpy as np
import os

# ======================================================
# CONFIGURATION
# ======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR,"data")

print("Looking for data in:", DATA_FOLDER)

VOL_WINDOW = 20
SHORT_MA = 20
LONG_MA = 50

HIGH_VOL_THRESHOLD = 0.20   # 20% annualized volatility
CRASH_DRAWDOWN = -0.20     # -20% drawdown from peak

# ======================================================
# MARKET STATE LOGIC (RULE-BASED)
# ======================================================
def detect_market_state(row):
    """
    Rule-based market state classification.
    """
    if row["drawdown"] <= CRASH_DRAWDOWN:
        return "Crash"
    elif row["volatility"] >= HIGH_VOL_THRESHOLD:
        return "High Volatility"
    elif row["ma_short"] > row["ma_long"]:
        return "Calm Bull"
    else:
        return "Calm Bear"

# ======================================================
# PROCESS A SINGLE STOCK
# ======================================================
def process_stock(csv_path):
    stock_name = os.path.basename(csv_path).replace(".csv", "")
    print(f"→ Reading {stock_name}")

    df = pd.read_csv(csv_path, parse_dates=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    # ----------------------
    # Detect price column safely
    # ----------------------
    if "Adj Close" in df.columns:
        price_col = "Adj Close"
    elif "Close" in df.columns:
        price_col = "Close"
    else:
        raise ValueError("No usable price column found")

    # ----------------------
    # Feature Engineering
    # ----------------------
    df["return"] = df[price_col].pct_change()
    df["volatility"] = df["return"].rolling(VOL_WINDOW).std() * np.sqrt(252)

    df["ma_short"] = df[price_col].rolling(SHORT_MA).mean()
    df["ma_long"] = df[price_col].rolling(LONG_MA).mean()

    df["rolling_max"] = df[price_col].cummax()
    df["drawdown"] = (df[price_col] - df["rolling_max"]) / df["rolling_max"]

    # Remove rows with NaNs (initial rolling window)
    df.dropna(inplace=True)

    # Market state classification
    # NOTE: apply() is used for clarity; can be vectorized later
    df["market_state"] = df.apply(detect_market_state, axis=1)

    df["stock"] = stock_name

    print(f"✅ {stock_name} processed ({len(df)} rows)")
    return df

# ======================================================
# MAIN PIPELINE (MULTI-STOCK)
# ======================================================
all_stocks = []

for file in os.listdir(DATA_FOLDER):
    if file.endswith(".csv"):
        try:
            stock_df = process_stock(os.path.join(DATA_FOLDER, file))
            if not stock_df.empty:
                all_stocks.append(stock_df)
        except Exception as e:
            print(f"❌ Skipping {file}: {e}")

# Safety check
if not all_stocks:
    raise RuntimeError("No stock files were processed successfully.")

final_df = pd.concat(all_stocks, ignore_index=True)

# ======================================================
# OUTPUT
# ======================================================
print("\nSample output:")
print(final_df[["Date", "stock", "market_state"]].tail(20))

final_df.to_csv("nifty50_with_market_state.csv", index=False)
print("\n📁 Saved: nifty50_with_market_state.csv")
print(f"📊 Total rows: {len(final_df)}")
print(f"📈 Stocks processed: {final_df['stock'].nunique()}")
