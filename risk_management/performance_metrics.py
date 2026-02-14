import numpy as np


def calculate_all_metrics(portfolio_value):

    returns = portfolio_value.pct_change().dropna()

    sharpe = np.sqrt(252) * returns.mean() / returns.std()

    cumulative_return = portfolio_value.iloc[-1] / portfolio_value.iloc[0] - 1
    years = len(portfolio_value) / 252
    cagr = (1 + cumulative_return) ** (1 / years) - 1

    running_max = portfolio_value.cummax()
    drawdown = (portfolio_value - running_max) / running_max
    max_drawdown = drawdown.min()

    volatility = returns.std() * np.sqrt(252)

    calmar = cagr / abs(max_drawdown) if max_drawdown != 0 else 0

    return {
        "Sharpe Ratio": sharpe,
        "CAGR": cagr,
        "Max Drawdown": max_drawdown,
        "Volatility": volatility,
        "Calmar Ratio": calmar
    }
