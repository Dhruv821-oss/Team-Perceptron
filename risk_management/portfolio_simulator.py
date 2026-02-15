import numpy as np
import pandas as pd

from risk_controls import apply_all_risk_controls
from config import RISK_CONFIG


def run_portfolio_simulation(returns, use_risk_management=True):

    portfolio_value = 1.0
    portfolio_history = []

    weight = 1.0
    peak_value = 1.0
    rolling_returns = []

    for r in returns:

        rolling_returns.append(r)

        # -------------------------------
        # 1. ROLLING VOLATILITY
        # -------------------------------
        if len(rolling_returns) >= 20:
            vol = np.std(rolling_returns[-20:]) * np.sqrt(252)
        else:
            vol = 0.0

        # -------------------------------
        # 2. DRAWDOWN
        # -------------------------------
        peak_value = max(peak_value, portfolio_value)
        drawdown = (portfolio_value - peak_value) / peak_value

        # -------------------------------
        # 3. ASSET VOL (for position sizing)
        # -------------------------------
        asset_vol = max(abs(r), 0.01)

        # -------------------------------
        # 4. RISK MANAGEMENT
        # -------------------------------
        if use_risk_management:

            # risk engine suggests TARGET weight
            target_weight = apply_all_risk_controls(
                current_weight=weight,
                daily_return=r,
                portfolio_volatility=vol,
                portfolio_drawdown=drawdown,
                asset_volatility=asset_vol,
                config=RISK_CONFIG
            )

            # ⭐ SMOOTH TRANSITION (critical fix)
            adjustment_speed = 0.10
            weight = (1 - adjustment_speed) * weight + adjustment_speed * target_weight

            # ⭐ MINIMUM EXPOSURE (never fully out)
            weight = max(weight, RISK_CONFIG["min_weight"])

            # ⭐ MAX LIMIT
            weight = min(weight, 1.0)

        # -------------------------------
        # 5. UPDATE PORTFOLIO
        # -------------------------------
        portfolio_value *= (1 + weight * r)
        portfolio_history.append(portfolio_value)

    return pd.Series(portfolio_history)
