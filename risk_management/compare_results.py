import os
import pandas as pd
import matplotlib.pyplot as plt

from portfolio_simulator import run_portfolio_simulation
from performance_metrics import calculate_all_metrics


# =====================================================
# 1. LOAD DATA
# =====================================================

DATA_FILE = "../data/CIPLA.csv"

if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(
        f"\n❌ Data file not found: {DATA_FILE}\n"
        "Check file path or move dataset into /data folder."
    )

print("\n📥 Loading dataset...\n")

df = pd.read_csv(DATA_FILE, parse_dates=["Date"])
df = df.sort_values("Date").reset_index(drop=True)

# Use Close price (Kaggle dataset standard)
df["return"] = df["Close"].pct_change().fillna(0)


# =====================================================
# 2. SIMULATION WITHOUT RISK MANAGEMENT
# =====================================================

print("\n🚀 Running simulation WITHOUT risk management...\n")

portfolio_no_risk = run_portfolio_simulation(
    returns=df["return"],
    use_risk_management=False
)


# =====================================================
# 3. SIMULATION WITH RISK MANAGEMENT
# =====================================================

print("\n🛡 Running simulation WITH risk management...\n")

portfolio_with_risk = run_portfolio_simulation(
    returns=df["return"],
    use_risk_management=True
)


# =====================================================
# 4. PERFORMANCE METRICS
# =====================================================

print("\n📊 Calculating performance metrics...\n")

metrics_no_risk = calculate_all_metrics(portfolio_no_risk)
metrics_with_risk = calculate_all_metrics(portfolio_with_risk)


# =====================================================
# 5. COMPARISON TABLE
# =====================================================

comparison = pd.DataFrame({
    "Without Risk Management": metrics_no_risk,
    "With Risk Management": metrics_with_risk
})

print("\n==============================")
print(" 📊 PERFORMANCE COMPARISON")
print("==============================\n")
print(comparison)

comparison.to_csv("risk_comparison_results.csv")
print("\n✅ Results saved → risk_comparison_results.csv")


# =====================================================
# 6. VISUAL COMPARISON (IMPORTANT FOR PROJECT)
# =====================================================

print("\n📈 Plotting portfolio performance...\n")

plt.figure(figsize=(12, 6))

plt.plot(df["Date"], portfolio_no_risk, label="Without Risk", alpha=0.7)
plt.plot(df["Date"], portfolio_with_risk, label="With Risk", linewidth=2)

plt.title("Portfolio Value: Risk Management vs No Risk")
plt.xlabel("Date")
plt.ylabel("Portfolio Value")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig("portfolio_comparison.png")
plt.show()

print("✅ Plot saved → portfolio_comparison.png")


# =====================================================
# 7. CAPITAL PRESERVATION ANALYSIS (BONUS)
# =====================================================

final_no_risk = portfolio_no_risk.iloc[-1]
final_with_risk = portfolio_with_risk.iloc[-1]

capital_preserved = (
    (final_with_risk - final_no_risk) / final_no_risk * 100
)

print("\n==============================")
print(" 🧠 CAPITAL PRESERVATION")
print("==============================")
print(f"Final value WITHOUT risk: {final_no_risk:.2f}")
print(f"Final value WITH risk:    {final_with_risk:.2f}")
print(f"Capital difference:       {capital_preserved:.2f}%")
print("==============================\n")
