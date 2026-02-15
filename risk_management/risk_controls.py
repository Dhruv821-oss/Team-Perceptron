import numpy as np


def apply_all_risk_controls(
    current_weight,
    daily_return,
    portfolio_volatility,
    portfolio_drawdown,
    asset_volatility,
    config
):
    """
    Returns TARGET portfolio weight after applying all risk rules.
    Does NOT directly multiply current weight.
    Portfolio simulator will smoothly adjust toward this target.
    """

    # ---------------------------------
    # START WITH FULL EXPOSURE
    # ---------------------------------
    target_weight = 1.0

    # ---------------------------------
    # 1. BLACK SWAN PROTECTION
    # ---------------------------------
    if abs(daily_return) > config["black_swan_threshold"]:
        target_weight = 0.10
        return target_weight   # immediate defensive mode

    # ---------------------------------
    # 2. DRAWDOWN PROTECTION
    # ---------------------------------
    if portfolio_drawdown <= config["max_drawdown"]:
        target_weight = 0.40

    # ---------------------------------
    # 3. VOLATILITY TARGETING
    # ---------------------------------
    if portfolio_volatility > config["target_volatility"]:
        target_weight = min(target_weight, 0.60)

    # ---------------------------------
    # 4. POSITION SIZING (LOW RISK → HIGH WEIGHT)
    # ---------------------------------
    vol_adjustment = 0.02 / asset_volatility
    vol_adjustment = min(vol_adjustment, 1.0)
    target_weight *= vol_adjustment

    # ---------------------------------
    # 5. STOP LOSS
    # ---------------------------------
    if daily_return < config["stop_loss"]:
        target_weight *= 0.5

    return target_weight
