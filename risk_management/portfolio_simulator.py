import numpy as np
import pandas as pd

from risk_controls import apply_all_risk_controls, detect_black_swan_event
from config import RISK_CONFIG


def run_portfolio_simulation(returns, use_risk_management=True):
    """
    Simulates portfolio growth over time.

    Includes:
    - Volatility targeting
    - Drawdown protection
    - Position sizing
    - Stop loss
    - Black swan kill switch

    Parameters
    ----------
    returns : pd.Series or list
        Daily asset returns

    use_risk_management : bool
        If True → risk engine applied
        If False → full exposure always

    Returns
    -------
    pd.Series of portfolio value over time
    """

    # -----------------------------
    # INITIAL STATE
    # -----------------------------
    portfolio_value = 1.0
    portfolio_history = []

    weight = 1.0
    peak_value = 1.0
    rolling_returns = []

    # -----------------------------
    # MAIN SIMULATION LOOP
    # -----------------------------
    for step, r in enumerate(returns):

        # convert to float (safety)
        r = float(r)

        # store rolling returns
        rolling_returns.append(r)

        # -----------------------------
        # ROLLING VOLATILITY (20-day)
        # -----------------------------
        if len(rolling_returns) >= 20:
            vol = np.std(rolling_returns[-20:]) * np.sqrt(252)
        else:
            vol = 0.0

        # -----------------------------
        # PORTFOLIO DRAWDOWN
        # -----------------------------
        peak_value = max(peak_value, portfolio_value)
        drawdown = (portfolio_value - peak_value) / peak_value

        # -----------------------------
        # ASSET VOL (avoid divide by zero)
        # -----------------------------
        asset_vol = max(abs(r), 0.01)

        # =====================================================
        # BLACK SWAN KILL SWITCH (FIRST PRIORITY)
        # =====================================================
        if use_risk_management:
            black_swan = detect_black_swan_event(
                daily_return=r,
                portfolio_drawdown=drawdown
            )

            if black_swan:
                print("\n🚨 BLACK SWAN EVENT DETECTED")
                print(f"Step: {step}")
                print(f"Daily return: {r:.4f}")
                print(f"Drawdown: {drawdown:.4f}")
                print("➡ Moving portfolio to CASH (0 exposure)")
                print("-" * 50)

                weight = 0.0

        # =====================================================
        # NORMAL RISK CONTROLS
        # =====================================================
        if use_risk_management and weight > 0:
            weight = apply_all_risk_controls(
                current_weight=weight,
                daily_return=r,
                portfolio_volatility=vol,
                portfolio_drawdown=drawdown,
                asset_volatility=asset_vol,
                config=RISK_CONFIG
            )

        # -----------------------------
        # SAFETY CLAMP
        # -----------------------------
        weight = np.clip(weight, 0.0, 1.0)

        # -----------------------------
        # PORTFOLIO UPDATE
        # -----------------------------
        portfolio_value *= (1 + weight * r)

        # prevent numerical explosion
        if not np.isfinite(portfolio_value):
            print("⚠ Numerical instability detected — stopping simulation")
            break

        portfolio_history.append(portfolio_value)

    # -----------------------------
    # RETURN RESULTS
    # -----------------------------
    return pd.Series(portfolio_history, name="Portfolio Value")
