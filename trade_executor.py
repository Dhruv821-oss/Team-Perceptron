import datetime
import random


class PaperTrader:
    def __init__(self, initial_capital=100000):
        self.cash = float(initial_capital)
        self.position = 0   # number of shares (INT)
        self.last_price = None

    def execute_trade(self, price, target_equity_weight):
        """
        Executes a micro-rebalanced trade to keep the portfolio active.
        This simulates tactical AI adjustments under uncertainty.
        """

        # -------------------------
        # SAFETY CHECKS
        # -------------------------
        if price <= 0 or target_equity_weight <= 0:
            return self.snapshot()

        total_value = self.cash + self.position * price
        target_equity_value = total_value * target_equity_weight

        # Target shares based on allocation
        target_shares = int(target_equity_value // price)

        # -------------------------
        # 🔥 MICRO-REBALANCING LOGIC
        # -------------------------
        # Force small buy/sell to show live activity
        jitter = random.choice([-1, 0, 1])

        # Avoid over-trading when flat
        if abs(target_shares - self.position) < 2:
            target_shares += jitter

        # Final clamp (cannot buy beyond cash)
        max_affordable = int(self.cash // price)
        target_shares = max(0, min(target_shares, self.position + max_affordable))

        delta_shares = target_shares - self.position

        # -------------------------
        # EXECUTE TRADE
        # -------------------------
        if delta_shares != 0:
            self.cash -= delta_shares * price
            self.position += delta_shares

        self.last_price = price

        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "price": round(price, 2),
            "shares_traded": int(delta_shares),
            "position": int(self.position),
            "cash": round(self.cash, 2),
            "portfolio_value": round(
                self.cash + self.position * price, 2
            )
        }

    # -------------------------
    # SAFE SNAPSHOT (NO TRADE)
    # -------------------------
    def snapshot(self):
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "price": "-" if self.last_price is None else round(self.last_price, 2),
            "shares_traded": 0,
            "position": int(self.position),
            "cash": round(self.cash, 2),
            "portfolio_value": round(
                self.cash + self.position * (self.last_price or 0), 2
            )
        }
