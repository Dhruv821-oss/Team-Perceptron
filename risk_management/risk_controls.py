import numpy as np
from config import (
    BLACK_SWAN_DROP_THRESHOLD,
    BLACK_SWAN_PORTFOLIO_DROP,
    ENABLE_BLACK_SWAN
)

# -------------------------------------------------
# Volatility Targeting
# -------------------------------------------------
def volatility_targeting(current_weight, portfolio_volatility, target_vol):
    if portfolio_volatility > target_vol:
        scale = target_vol / portfolio_volatility
        return current_weight * scale
    return current_weight


# -------------------------------------------------
# Drawdown Protection
# -------------------------------------------------
def drawdown_control(current_weight, portfolio_drawdown, max_dd):
    if portfolio_drawdown <= max_dd:
        return current_weight * 0.5   # cut exposure by 50%
    return current_weight


# -------------------------------------------------
# Stop Loss
# -------------------------------------------------
def stop_loss_control(current_weight, daily_return, stop_loss):
    if daily_return <= stop_loss:
        return current_weight * 0.3   # aggressive reduction
    return current_weight


# -------------------------------------------------
# Risk-Based Position Sizing (safe version)
# -------------------------------------------------
def risk_based_position_size(asset_volatility, base_weight):
    if asset_volatility <= 0:
        return base_weight

    adjusted_weight = base_weight / asset_volatility

    # Prevent extreme leverage
    MAX_WEIGHT = 3.0
    MIN_WEIGHT = 0.0

    adjusted_weight = min(adjusted_weight, MAX_WEIGHT)
    adjusted_weight = max(adjusted_weight, MIN_WEIGHT)

    return adjusted_weight


# -------------------------------------------------
# MASTER RISK CONTROL PIPELINE
# -------------------------------------------------
def apply_all_risk_controls(
        current_weight,
        daily_return,
        portfolio_volatility,
        portfolio_drawdown,
        asset_volatility,
        config
):

    weight = current_weight

    weight = volatility_targeting(
        weight,
        portfolio_volatility,
        config["target_volatility"]
    )

    weight = drawdown_control(
        weight,
        portfolio_drawdown,
        config["max_drawdown_limit"]
    )

    weight = stop_loss_control(
        weight,
        daily_return,
        config["stop_loss_threshold"]
    )

    weight = risk_based_position_size(
        asset_volatility,
        weight
    )

    return weight


def detect_black_swan_event(daily_return, portfolio_drawdown):
    """
    Detect extreme market crash conditions.

    Triggers if:
    1. Single day crash is too large
    OR
    2. Portfolio drawdown becomes extreme
    """

    if not ENABLE_BLACK_SWAN:
        return False

    # sudden crash
    if daily_return <= BLACK_SWAN_DROP_THRESHOLD:
        print("🚨 BLACK SWAN: Extreme daily crash detected")
        return True

    # extreme cumulative loss
    if portfolio_drawdown <= BLACK_SWAN_PORTFOLIO_DROP:
        print("🚨 BLACK SWAN: Extreme portfolio drawdown detected")
        return True

    return False
