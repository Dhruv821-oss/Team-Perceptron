🧠 Team Perceptron — Autonomous AI Trading & Risk Intelligence Platform

Team Perceptron is a full-stack, AI-driven automated trading and risk-analysis platform designed to simulate institutional-grade trading workflows.
The system combines machine learning, real-time market data, risk management, explainability, and live analytics dashboards into a single coherent architecture.

This project goes beyond basic algorithmic trading by focusing on decision justification, capital protection, regime awareness, and continuous risk diagnostics, making it suitable for research, hackathons, and production-grade experimentation.


<img width="1753" height="868" alt="Screenshot 2026-02-16 002848" src="https://github.com/user-attachments/assets/6de9d879-137d-4a99-ab95-401403550470" />
<img width="1855" height="827" alt="Screenshot 2026-02-16 002833" src="https://github.com/user-attachments/assets/e5bba9a1-9941-4d7a-82e0-efa0c3eb5461" />
<img width="1867" height="830" alt="Screenshot 2026-02-16 002821" src="https://github.com/user-attachments/assets/ddf10f03-2730-4e21-a824-abd8fd4f98fc" />
<img width="1835" height="978" alt="Screenshot 2026-02-16 002749" src="https://github.com/user-attachments/assets/74bd0448-1544-4aad-8ebd-4ef58fd396c0" />
<img width="1889" height="896" alt="Screenshot 2026-02-16 002712" src="https://github.com/user-attachments/assets/ba3ca284-bc0a-4c89-83d9-4e697650a663" />
<img width="860" height="554" alt="Screenshot 2026-02-16 002639" src="https://github.com/user-attachments/assets/4cbef7f1-a59a-467d-9c15-e326c2370b47" />
<img width="1891" height="904" alt="Screenshot 2026-02-16 002629" src="https://github.com/user-attachments/assets/d4ac2538-1be3-44e5-aff5-3a32a65ab287" />
<img width="1808" height="924" alt="Screenshot 2026-02-16 002903" src="https://github.com/user-attachments/assets/2ca375c7-b170-4f66-8fc4-cbe92f5e14ce" />


🚀 Core Vision

Most retail trading bots focus only on buy/sell signals.
Team Perceptron instead answers four critical questions simultaneously:

What is the current market regime?

Which asset is optimal right now?

How much capital should be risked safely?

Why did the AI take this action?

Every trade is:

Risk-adjusted

Logged

Explained in plain English

Visualized live

🏗 System Architecture Overview

The platform is built as a modular AI pipeline, enabling both batch analysis and continuous live trading.

🔹 High-Level Flow
Live Market Data
      ↓
Feature Engineering (No Data Leakage)
      ↓
ML Market Regime Detection
      ↓
Best Stock Selection Engine
      ↓
Risk Controls & Capital Allocation
      ↓
Paper Trade Execution
      ↓
Live Dashboards + Explainability + Logs

📊 Data Ingestion & Feature Engineering

The system ingests live data from Yahoo Finance (yfinance) and constructs a leakage-free feature space.

Features Computed

Daily returns

Rolling volatility

Short & long moving averages

Drawdown metrics

Momentum & trend signals

Cross-asset comparisons

⚠ No data leakage:
All rolling features strictly use past information only, matching real-world trading constraints.

🤖 Machine Learning: Market Regime Detection

A trained ML model classifies the market into regimes such as:

Calm Bull

Calm Bear

High Volatility

Crash

This regime acts as a global control signal, influencing:

Asset selection

Capital exposure

Risk thresholds

🎯 Best Stock Selection Engine

When multiple assets are provided, the system:

Scores each asset using momentum, volatility, and trend

Filters based on market regime

Dynamically selects the highest risk-adjusted opportunity

This mimics institutional portfolio rotation logic rather than static strategies.

⚠️ Risk Management Engine (First-Class Citizen)

Risk is not an afterthought.

Live Risk Controls Include:

Volatility-based exposure reduction

Drawdown-aware position sizing

Regime-adaptive capital limits

Dynamic Risk Metrics:

Volatility

Max Drawdown

Risk Level Classification (NORMAL / HIGH)

📈 Backtesting & Stress Testing

Every live decision is accompanied by:

🔹 Backtest Simulation

Strategy equity curve

Final capital multiple

Leakage-free historical evaluation

🔹 Stress Testing

Synthetic crash injection

Capital survival checks

Managed vs unmanaged comparison

This ensures the AI doesn’t just perform in calm markets.

💼 Paper Trading Engine

The platform executes realistic paper trades:

Integer share enforcement

Cash & position tracking

Portfolio valuation updated in real time

Each trade records:

BUY / SELL / HOLD

Price

Shares traded

Portfolio impact

🧠 Explainable AI (XAI)

Every decision includes a plain-English explanation, answering:

“Why did the AI do this?”

Example:

“RELIANCE.NS selected under Calm Bull regime.
Risk-adjusted allocation set to 60% due to controlled volatility and positive momentum.”

This makes the system auditable, debuggable, and human-aligned.

📊 Live Dashboards
🔹 Live Trading Dashboard

Market regime

Selected stock

Allocation %

Portfolio value (real-time chart)

Risk metrics

Backtest & stress results

Transaction log

AI decision log

🔹 Live Graph Analytics Page

Displays only high-activity periods, including:

Price spikes

Volatility bursts

Allocation reactions

Market randomness (entropy proxy)

🔹 Risk Intelligence Page

Institutional-style risk metrics:

CAGR

Sharpe Ratio

Sortino Ratio

Max Drawdown

Calmar Ratio

Capital risk alerts

🧾 Logging & Transparency

All trades are:

Persisted to CSV logs

Timestamped

Regime-aware

Replayable for research

🛡 Capital Protection Alerts

The system actively monitors capital health and raises alerts when:

Drawdowns exceed thresholds

Volatility spikes dangerously

Risk-adjusted returns degrade

🧪 Research & Extension Ready

Designed for:

Multi-agent RL extensions

CTDE experiments

Portfolio-level learning

Stress-scenario research

🧩 Tech Stack

Backend: Python, Flask

ML: Scikit-learn, NumPy, Pandas

Data: yFinance

Frontend: HTML, CSS, JavaScript

Charts: Chart.js

Persistence: CSV logs

Auth: Session-based (extensible)

⚠ Disclaimer

This project is for educational and research purposes only.
It performs paper trading only and does not execute real trades.
