"""
Risk Management Configuration
All system risk parameters defined here
"""

RISK_CONFIG = {
    "target_volatility": 0.20,      # 20% annualized target volatility
    "max_drawdown_limit": -0.15,    # -15% max allowed drawdown
    "stop_loss_threshold": -0.03    # -3% daily stop loss
}

# ==============================
# BLACK SWAN CONFIGURATION
# ==============================

BLACK_SWAN_DROP_THRESHOLD = -0.08   # -8% single day crash
BLACK_SWAN_PORTFOLIO_DROP = -0.15   # -15% cumulative crash
BLACK_SWAN_EXIT_WEIGHT = 0.0        # move fully to cash
ENABLE_BLACK_SWAN = True