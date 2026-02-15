import pandas as pd
import matplotlib.pyplot as plt


class PortfolioStressor:
    """
    PURPOSE:
    Stress-test the portfolio under extreme synthetic scenarios
    to verify capital protection by the Risk Engine.
    """

    def __init__(self, processed_df):
        """
        processed_df must contain:
        - 'return'
        - 'volatility'
        - 'market_state'
        """
        self.original_df = processed_df.copy()
        self.results = {}
        self.equity_curves = {}

    # ======================================================
    # INTERNAL: SHOCK GENERATOR
    # ======================================================
    def _generate_shock(self, scenario_type):
        stressed_df = self.original_df.copy()
        mid = len(stressed_df) // 2
        window = slice(mid, mid + 30)

        if scenario_type == "black_swan":
            # 5 consecutive days of -5% crash
            stressed_df.iloc[mid:mid+5,
                stressed_df.columns.get_loc("return")] = -0.05

        elif scenario_type == "vol_regime_shift":
            # Volatility explodes
            stressed_df.iloc[window,
                stressed_df.columns.get_loc("volatility")] *= 4

        elif scenario_type == "systemic_collapse":
            # Correlated losses across assets
            stressed_df.iloc[window,
                stressed_df.columns.get_loc("return")] = -0.03

        return stressed_df

    # ======================================================
    # MAIN STRESS TEST RUNNER
    # ======================================================
    def run_test(self, allocation_engine_callback):
        """
        allocation_engine_callback(df) → returns managed daily returns
        """

        scenarios = {
            "Black Swan Shock": "black_swan",
            "Volatility Explosion": "vol_regime_shift",
            "Systemic Collapse": "systemic_collapse"
        }

        print("\n" + "=" * 55)
        print("🔍 STRESS TEST – EXPLAINABILITY LOGS")
        print("=" * 55)

        for name, scenario in scenarios.items():
            test_df = self._generate_shock(scenario)

            # -----------------------------
            # Unmanaged (Buy & Hold)
            # -----------------------------
            unmanaged_returns = test_df["return"]
            unmanaged_equity = (1 + unmanaged_returns).cumprod()
            unmanaged_final = unmanaged_equity.iloc[-1]

            # -----------------------------
            # Managed (Risk Engine)
            # -----------------------------
            managed_returns = allocation_engine_callback(test_df)
            managed_equity = (1 + managed_returns).cumprod()
            managed_final = managed_equity.iloc[-1]

            # -----------------------------
            # Store results
            # -----------------------------
            self.results[name] = {
                "Unmanaged": unmanaged_final,
                "Managed": managed_final
            }

            self.equity_curves[name] = {
                "Unmanaged": unmanaged_equity,
                "Managed": managed_equity
            }

            print(f"[{name}]")
            print(f" > Unmanaged Wealth : {unmanaged_final:.4f}")
            print(f" > Managed Wealth   : {managed_final:.4f}")
            print(f" > Capital Saved    : {(managed_final - unmanaged_final):.2%}")
            print("-" * 30)

    # ======================================================
    # VISUALIZATION (BAR + CURVES)
    # ======================================================
    def plot_results(self):
        if not self.results:
            return

        # -----------------------------
        # BAR CHART
        # -----------------------------
        df_plot = pd.DataFrame(self.results).T
        df_plot.plot(
            kind="bar",
            figsize=(10, 6),
            color=["#ff6666", "#44bb44"]
        )

        plt.title("Portfolio Resilience: Risk Engine vs Passive Market")
        plt.ylabel("Terminal Wealth (Initial = 1.0)")
        plt.xticks(rotation=30)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.show()

        # -----------------------------
        # EQUITY CURVES
        # -----------------------------
        for scenario, curves in self.equity_curves.items():
            plt.figure(figsize=(10, 5))
            plt.plot(curves["Unmanaged"], label="Passive Market", color="#ff6666")
            plt.plot(curves["Managed"], label="Risk Engine", color="#44bb44")

            plt.title(f"Equity Curve Under Stress: {scenario}")
            plt.xlabel("Time")
            plt.ylabel("Portfolio Value")
            plt.legend()
            plt.grid(linestyle="--", alpha=0.7)
            plt.tight_layout()
            plt.show()

    # ======================================================
    # DASHBOARD-FRIENDLY OUTPUT
    # ======================================================
    def get_results_for_dashboard(self):
        return {
            scenario: {
                "Unmanaged": round(v["Unmanaged"], 2),
                "Managed": round(v["Managed"], 2),
                "Capital Saved (%)": round(
                    (v["Managed"] - v["Unmanaged"]) / v["Unmanaged"] * 100, 2
                )
            }
            for scenario, v in self.results.items()
        }
