import pandas as pd
import numpy as np

# ======================================================
# LOAD INPUT
# ======================================================
df = pd.read_csv("nifty50_with_market_state.csv", parse_dates=["Date"])

# ======================================================
# PARAMETERS
# ======================================================
STATE_ALLOCATION = {
    "Crash": 0.0,
    "High Volatility": 0.3,
    "Calm Bear": 0.5,
    "Calm Bull": 1.0
}

MAX_VOL = 0.40      # cap for volatility scaling
MIN_WEIGHT = 0.0

# ======================================================
# DENSE ALLOCATION ENGINE
# ======================================================
def allocate_capital_dense(daily_df):
    """
    Dense allocation logic using:
    - Market regime
    - Volatility scaling
    - Trend confirmation
    """

    # -------------------------
    # 1. Regime-based exposure
    # -------------------------
    daily_df["base_exposure"] = daily_df["market_state"].map(
        STATE_ALLOCATION
    )

    # -------------------------
    # 2. Volatility-based scaling
    # lower vol → higher weight
    # -------------------------
    vol_scaled = 1 - (daily_df["volatility"] / MAX_VOL)
    daily_df["vol_scaler"] = vol_scaled.clip(0.0, 1.0)

    # -------------------------
    # 3. Trend confirmation
    # -------------------------
    daily_df["trend_signal"] = np.where(
        daily_df["ma_short"] > daily_df["ma_long"], 1.0, 0.5
    )

    # -------------------------
    # 4. Raw allocation score
    # -------------------------
    daily_df["raw_weight"] = (
        daily_df["base_exposure"]
        * daily_df["vol_scaler"]
        * daily_df["trend_signal"]
    )

    # Remove negatives / NaNs
    daily_df["raw_weight"] = daily_df["raw_weight"].clip(
        lower=MIN_WEIGHT
    ).fillna(0.0)

    total_weight = daily_df["raw_weight"].sum()

    # -------------------------
    # 5. Normalize portfolio
    # -------------------------
    if total_weight == 0:
        daily_df["final_weight"] = 0.0
    else:
        daily_df["final_weight"] = (
            daily_df["raw_weight"] / total_weight
        )

    return daily_df

# ======================================================
# APPLY DAY-WISE
# ======================================================
results = []

for date, daily_data in df.groupby("Date"):
    allocated_day = allocate_capital_dense(daily_data.copy())
    results.append(allocated_day)

allocation_df = pd.concat(results, ignore_index=True)

# ======================================================
# OUTPUT
# ======================================================
print("\nDense Allocation Sample:")
print(
    allocation_df[
        ["Date", "stock", "market_state", "final_weight"]
    ].tail(20)
)

allocation_df.to_csv(
    "nifty50_with_dense_allocations.csv", index=False
)

print("\nSaved file: nifty50_with_dense_allocations.csv")
