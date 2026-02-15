import numpy as np

TARGET_VOL = 0.15
MAX_DRAWDOWN = -0.20

def apply_risk_controls(df, base_equity_weight):
    port_vol = df["return"].std() * np.sqrt(252)

    vol_scale = min(1.0, TARGET_VOL / port_vol) if port_vol > 0 else 1.0

    rolling_max = df["Close"].cummax()
    drawdown = (df["Close"] - rolling_max) / rolling_max
    max_dd = drawdown.min()

    dd_scale = 0.0 if max_dd < MAX_DRAWDOWN else 1.0

    final_weight = base_equity_weight * vol_scale * dd_scale

    return {
        "final_weight": round(final_weight, 2),
        "portfolio_volatility": round(port_vol, 2),
        "max_drawdown": round(max_dd, 2),
        "volatility_scale": round(vol_scale, 2)
    }
