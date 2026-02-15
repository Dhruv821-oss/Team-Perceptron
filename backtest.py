import numpy as np

def backtest(df, equity_weight):
    df = df.copy()
    df["strategy_return"] = df["return"] * equity_weight
    df["equity_curve"] = (1 + df["strategy_return"]).cumprod()

    cagr = df["equity_curve"].iloc[-1] ** (252 / len(df)) - 1
    sharpe = (
        df["strategy_return"].mean() /
        df["strategy_return"].std()
    ) * np.sqrt(252)

    max_dd = (
        df["equity_curve"] /
        df["equity_curve"].cummax() - 1
    ).min()

    return {
        "CAGR": round(cagr, 2),
        "Sharpe": round(sharpe, 2),
        "Max Drawdown": round(max_dd, 2)
    }
