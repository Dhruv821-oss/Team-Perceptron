import pandas as pd
import numpy as np
import os

# ======================================================
# CONFIGURATION
# ======================================================
# Folder containing all NIFTY50 CSV files (one CSV per stock)
DATA_FOLDER = "data"

# Rolling window sizes
VOL_WINDOW = 20          # window for volatility calculation
SHORT_MA = 20            # short-term moving average
LONG_MA = 50             # long-term moving average

# Thresholds (can be tuned later)
HIGH_VOL_THRESHOLD = 0.20    # 20% annualized volatility
CRASH_DRAWDOWN = -0.20       # -20% drawdown from peak

# ======================================================
# MARKET STATE LOGIC (RULE-BASED)
# ======================================================
def detect_market_state(row):
    """
    Classifies market state for a single day based on
    drawdown, volatility, and trend.
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
# PROCESS A SINGLE STOCK FILE
# ======================================================
def process_stock(csv_path):
    """
    Reads a single stock CSV and computes market state
    for each trading day.
    """
    stock_name = os.path.basename(csv_path).replace(".csv", "")

    # Load and sort data
    df = pd.read_csv(csv_path, parse_dates=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    # ----------------------
    # Feature Engineering
    # ----------------------

    # Daily returns
    df["return"] = df["Adj Close"].pct_change()

    # Annualized rolling volatility
    df["volatility"] = (
        df["return"].rolling(VOL_WINDOW).std() * np.sqrt(252)
    )

    # Moving averages
    df["ma_short"] = df["Adj Close"].rolling(SHORT_MA).mean()
    df["ma_long"] = df["Adj Close"].rolling(LONG_MA).mean()

    # Drawdown calculation
    df["rolling_max"] = df["Adj Close"].cummax()
    df["drawdown"] = (
        df["Adj Close"] - df["rolling_max"]
    ) / df["rolling_max"]

    # Drop initial rows with NaN values
    df.dropna(inplace=True)

    # Market state classification
    df["market_state"] = df.apply(detect_market_state, axis=1)

    # Add stock identifier
    df["stock"] = stock_name

    return df

# ======================================================
# MAIN PIPELINE (MULTI-STOCK)
# ======================================================
all_stocks = []

for file in os.listdir(DATA_FOLDER):
    if file.endswith(".csv"):
        try:
            print(f"Processing {file}...")
            file_path = os.path.join(DATA_FOLDER, file)
            stock_df = process_stock(file_path)
            all_stocks.append(stock_df)
        except Exception as e:
            print(f"Skipping {file} due to error: {e}")

# Combine all stocks into one DataFrame
final_df = pd.concat(all_stocks, ignore_index=True)

# ======================================================
# OUTPUT
# ======================================================
print("\nSample output:")
print(
    final_df[
        ["Date", "stock", "Adj Close", "market_state"]
    ].tail(20)
)

# Save output for downstream modules (allocation, risk, backtesting)
final_df.to_csv("nifty50_with_market_state.csv", index=False)

print("\nSaved combined file as: nifty50_with_market_state.csv")
