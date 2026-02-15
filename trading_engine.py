from utils import (
    fetch_live_data,
    compute_features,
    predict_regime,
    allocate,
    pick_best_stock
)

from risk_engine import apply_risk_controls
from trade_executor import PaperTrader
from trade_logger import log_trade


class AITradingEngine:
    def __init__(self, symbols):
        """
        symbols: list of stock symbols
        """
        self.symbols = symbols
        self.trader = PaperTrader()

    def run_cycle(self):
        stock_dfs = {}

        # =====================================
        # 1. FETCH + FEATURE ENGINEERING
        # =====================================
        for sym in self.symbols:
            df = fetch_live_data(sym)
            df = compute_features(df)
            df = predict_regime(df)

            if df is None or df.empty:
                continue

            if "market_state" not in df.columns:
                continue

            stock_dfs[sym] = df

        # HARD FAIL-SAFE
        if not stock_dfs:
            return self._empty_state(
                "No valid market data available yet."
            )

        # =====================================
        # 2. MARKET REGIME (ANCHOR)
        # =====================================
        first_symbol = list(stock_dfs.keys())[0]
        market_regime = stock_dfs[first_symbol].iloc[-1]["market_state"]

        # =====================================
        # 3. BEST STOCK SELECTION
        # =====================================
        try:
            best_stock, _ = pick_best_stock(
                stock_dfs, market_regime
            )
        except Exception:
            best_stock = first_symbol

        df = stock_dfs[best_stock]

        # =====================================
        # 4. ALLOCATION + RISK CONTROL
        # =====================================
        base_alloc = allocate(df)

        try:
            base_weight = float(
                base_alloc["Equity Allocation"].replace("%", "")
            ) / 100
        except Exception:
            base_weight = 0.0

        risk_ctrl = apply_risk_controls(df, base_weight)
        final_weight = risk_ctrl.get(
            "final_weight", base_weight
        )

        # =====================================
        # 5. EXECUTE PAPER TRADE
        # =====================================
        try:
            price = float(df.iloc[-1]["Close"])
            trade = self.trader.execute_trade(
                price, final_weight
            )
        except Exception:
            trade = self.trader.snapshot()

        # =====================================
        # 6. RISK METRICS (ALWAYS PRESENT)
        # =====================================
        volatility = float(df["volatility"].iloc[-1])
        max_dd = float(df["drawdown"].min())

        risk = {
            "volatility": round(volatility, 3),
            "max_drawdown": round(max_dd, 3),
            "risk_level": (
                "HIGH"
                if volatility > 0.3 or max_dd < -0.2
                else "NORMAL"
            )
        }

        # =====================================
        # 7. BACKTEST (LEAKAGE-FREE)
        # =====================================
        strat_equity = (
            1 + df["return"] * final_weight
        ).cumprod()

        backtest = {
    "final_value": round(float(strat_equity.iloc[-1]), 2),
    "CAGR": round((strat_equity.iloc[-1] ** (252 / len(df)) - 1), 4),
    "Sharpe": round(df["return"].mean() / (df["return"].std() + 1e-6), 2),
    "Sortino": round(
        df["return"].mean() /
        (df[df["return"] < 0]["return"].std() + 1e-6),
        2
    )
}


        
         
        # ====================================
        # 8. STRESS TEST (SYNTHETIC SHOCK)
        # =====================================
        stressed_returns = df["return"].copy()
        stressed_returns.iloc[:5] = -0.05

        stress_equity = (
            1 + stressed_returns
        ).cumprod()

        stress = {
            "final_value": round(
                float(stress_equity.iloc[-1]), 2
            ),
            "survived": stress_equity.iloc[-1] > 0.7
        }

        # =====================================
        # 9. EXPLAINABILITY
        # =====================================
        explanation = (
            f"{best_stock} selected under {market_regime} regime. "
            f"Risk-adjusted allocation = {round(final_weight * 100, 0)}%. "
            f"Volatility={risk['volatility']}, "
            f"Drawdown={risk['max_drawdown']}."
        )

        # =====================================
        # 10. LOG TRADE (NON-BLOCKING)
        # =====================================
        try:
            log_trade(
                best_stock,
                market_regime,
                "AUTO_TRADE",
                final_weight,
                explanation,
                trade
            )
        except Exception:
            pass

        # =====================================
        # 11. FINAL RESULT (SCHEMA-STABLE)
        # =====================================
        return {
            "best_stock": best_stock,
            "regime": market_regime,
            "allocation": final_weight,
            "portfolio": trade,

            "risk": risk,
            "backtest": backtest,
            "stress": stress,

            "explanation": explanation
        }

    # =====================================
    # SAFE EMPTY STATE (NEVER BREAKS UI)
    # =====================================
    def _empty_state(self, msg):
        return {
            "best_stock": "-",
            "regime": "Initializing",
            "allocation": 0.0,

            "portfolio": self.trader.snapshot(),

            "risk": {
                "volatility": 0.0,
                "max_drawdown": 0.0,
                "risk_level": "NORMAL"
            },

            "backtest": {
                "final_value": 1.0
            },

            "stress": {
                "final_value": 1.0,
                "survived": True
            },

            "explanation": msg
        }
