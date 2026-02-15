def explain_decision(regime, risk, allocation):
    explanation = []

    explanation.append(f"Market regime detected: {regime}.")

    if regime == "High Volatility":
        explanation.append("Volatility spike detected, reducing exposure.")

    if risk["max_drawdown"] < -0.2:
        explanation.append("Drawdown threshold breached, capital protection activated.")

    explanation.append(
        f"Final equity allocation adjusted to {allocation * 100:.0f}%."
    )

    return " ".join(explanation)
