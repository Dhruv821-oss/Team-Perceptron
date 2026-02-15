import pandas as pd
import matplotlib.pyplot as plt

from portfolio_simulator import run_portfolio_simulation
from performance_metrics import calculate_all_metrics


# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
DATA_FILE = "../data/CIPLA.csv"

df = pd.read_csv(DATA_FILE, parse_dates=["Date"])
df = df.sort_values("Date").reset_index(drop=True)

# use CLOSE price returns
df["return"] = df["Close"].pct_change().fillna(0)


# -------------------------------------------------
# SIMULATION WITHOUT RISK MANAGEMENT
# -------------------------------------------------
print("\nRunning simulation WITHOUT risk management...\n")

portfolio_no_risk = run_portfolio_simulation(
    returns=df["return"],
    use_risk_management=False
)


# -------------------------------------------------
# SIMULATION WITH RISK MANAGEMENT
# -------------------------------------------------
print("Running simulation WITH risk management...\n")

portfolio_with_risk = run_portfolio_simulation(
    returns=df["return"],
    use_risk_management=True
)


# -------------------------------------------------
# PERFORMANCE METRICS
# -------------------------------------------------
metrics_no_risk = calculate_all_metrics(portfolio_no_risk)
metrics_with_risk = calculate_all_metrics(portfolio_with_risk)


# -------------------------------------------------
# COMPARISON TABLE
# -------------------------------------------------
comparison = pd.DataFrame({
    "Without Risk Management": metrics_no_risk,
    "With Risk Management": metrics_with_risk
})

print("\n==============================")
print(" PERFORMANCE COMPARISON")
print("==============================\n")
print(comparison)

comparison.to_csv("risk_comparison_results.csv")
print("\nSaved results to risk_comparison_results.csv")


# -------------------------------------------------
# PLOT PORTFOLIO VALUE
# -------------------------------------------------
plt.figure(figsize=(12, 6))

plt.plot(df["Date"], portfolio_no_risk, label="Without Risk", linewidth=2)
plt.plot(df["Date"], portfolio_with_risk, label="With Risk", linewidth=2)

plt.title("Portfolio Value: Risk Management vs No Risk")
plt.xlabel("Date")
plt.ylabel("Portfolio Value")
plt.legend()
plt.grid(True)

plt.show()
