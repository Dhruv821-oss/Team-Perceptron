import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class PortfolioStressor:
    """
    PURPOSE: This class artificially 'breaks' the market data to see if 
    the Risk Management Engine actually protects capital during a crash. [cite: 19, 20]
    """
    def __init__(self, processed_df):
        # We need 'return', 'volatility', and 'market_state' columns from the detection module.
        self.original_df = processed_df.copy()
        self.results = {}

    def _generate_shock(self, df, scenario_type):
        """
        TEAMMATE NOTE: This function creates synthetic 'Black Swan' events 
        by manually overwriting a 30-day window in the middle of the dataset. [cite: 20]
        """
        stressed_df = df.copy()
        mid = len(stressed_df) // 2
        window = slice(mid, mid + 30)

        if scenario_type == "black_swan":
            # Simulation: 5 days of massive institutional sell-offs (-5% daily). [cite: 20]
            # This should trigger 'Crash' or 'Drawdown Protection' logic. [cite: 9, 16]
            stressed_df.iloc[mid:mid+5, stressed_df.columns.get_loc('return')] = -0.05
            
        elif scenario_type == "vol_regime_shift":
            # Simulation: Volatility quadruples. [cite: 20]
            # This should trigger 'Volatility Targeting' to reduce position sizes. [cite: 15]
            stressed_df.iloc[window, stressed_df.columns.get_loc('volatility')] *= 4
            
        elif scenario_type == "systemic_collapse":
            # Simulation: Correlation spike. Everything drops at once. [cite: 20]
            # Teammate: Test if your engine moves capital to cash or defensive assets here. [cite: 21]
            stressed_df.iloc[window, stressed_df.columns.get_loc('return')] = -0.03
            
        return stressed_df

    def run_test(self, allocation_engine_callback):
        """
        MANDATORY REQUIREMENT: Compare 'With Risk Engine' vs 'Without Risk Engine'. [cite: 17]
        'allocation_engine_callback' is the function your teammate is writing.
        """
        scenarios = {
            "Black Swan Shock": "black_swan",
            "Volatility Explosion": "vol_regime_shift",
            "Systemic Collapse": "systemic_collapse"
        }

        print("\n" + "="*50)
        print("🔍 EXPLAINABILITY LAYER: STRESS TEST LOGS") # Mandatory for marks [cite: 21, 22]
        print("="*50)

        for name, s_type in scenarios.items():
            # 1. Inject the anomaly into the data
            test_data = self._generate_shock(self.original_df, s_type)
            
            # 2. Baseline: What happens if we do nothing (Buy & Hold)?
            unmanaged_final_wealth = (1 + test_data['return']).prod()
            
            # 3. Managed: What happens when your teammate's engine is active?
            # TEAMMATE: Your function must take 'test_data' and return weighted returns. [cite: 12]
            managed_returns = allocation_engine_callback(test_data)
            managed_final_wealth = (1 + managed_returns).prod()
            
            # 4. Calculate Alpha (The value added by the Risk Engine) [cite: 18]
            alpha = managed_final_wealth - unmanaged_final_wealth
            
            # Explainability output: This is what judges look for. [cite: 21, 22]
            print(f"[{name}] Monitoring Engine Response...")
            print(f" > Managed Wealth: {managed_final_wealth:.4f}")
            print(f" > Unmanaged Wealth: {unmanaged_final_wealth:.4f}")
            print(f" > Capital Saved: {alpha:.2%}")
            print("-" * 30)

            self.results[name] = {
                "Unmanaged": unmanaged_final_wealth,
                "Managed": managed_final_wealth
            }

    def plot_results(self):
        """
        Final Visual Proof for the Demo. [cite: 35, 40]
        Green bars should ideally be higher than Red bars in all crisis scenarios.
        """
        if not self.results:
            return
            
        df_plot = pd.DataFrame(self.results).T
        ax = df_plot.plot(kind='bar', figsize=(10, 6), color=['#ff6666', '#44bb44'])
        plt.title("Portfolio Resilience: Risk Engine vs. Passive Market")
        plt.ylabel("Terminal Wealth (Initial = 1.0)")
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show() # Show this during the 3-minute live demo [cite: 38]