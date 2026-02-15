import csv
import os
from datetime import datetime

LOG_FILE = "logs/trades.csv"

def log_trade(symbol, regime, action, allocation, explanation, metrics):
    try:
        os.makedirs("logs", exist_ok=True)
        file_exists = os.path.isfile(LOG_FILE)

        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)

            if not file_exists:
                writer.writerow([
                    "Time",
                    "Symbol",
                    "Regime",
                    "Action",
                    "Equity Allocation",
                    "Explanation",
                    "Portfolio Value"
                ])

            writer.writerow([
                datetime.now().isoformat(),   # SAFE STRING
                symbol,
                regime,
                action,
                allocation,
                explanation,
                metrics.get("portfolio_value", "")
            ])

    except Exception as e:
        # Logging should NEVER crash trading
        print("⚠️ LOGGING ERROR:", e)
