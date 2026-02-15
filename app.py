from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    jsonify
)
import threading
import time
import datetime
import numpy as np

from trading_engine import AITradingEngine

# ======================================
# APP INIT
# ======================================
app = Flask(__name__)
app.secret_key = "ai_trading_secret"

# ======================================
# GLOBAL LIVE STATE
# ======================================
live_engines = {}
live_results = {}

# ======================================
# JSON SAFE CONVERTER (CRITICAL)
# ======================================
def make_json_safe(obj):
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [make_json_safe(v) for v in obj]

    if isinstance(obj, (np.bool_,)):
        return bool(obj)

    if isinstance(obj, (np.integer,)):
        return int(obj)

    if isinstance(obj, (np.floating,)):
        return float(obj)

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()

    return obj

# ======================================
# AUTH GUARD
# ======================================
@app.before_request
def require_login():
    if request.path.startswith("/static"):
        return
    if request.path in ["/", "/login", "/register"]:
        return

    protected = [
        "/dashboard",
        "/live",
        "/live/start",
        "/live/status",
        "/live/stop",
        "/logout"
    ]

    if request.path in protected and "user" not in session:
        return redirect("/login")

# ======================================
# LANDING
# ======================================
@app.route("/")
def landing():
    return render_template("landing.html")

# ======================================
# REGISTER
# ======================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        session["user"] = request.form["username"]
        return redirect("/dashboard")
    return render_template("register.html")

# ======================================
# LOGIN
# ======================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user"] = request.form["username"]
        return redirect("/dashboard")
    return render_template("login.html")

# ======================================
# DASHBOARD (ANALYSIS MODE)
# ======================================
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        symbol = request.form["symbol"].strip()

        try:
            engine = AITradingEngine([symbol])
            result = engine.run_cycle()
        except Exception as e:
            result = {
                "best_stock": "-",
                "regime": "Error",
                "allocation": 0.0,
                "portfolio": {},
                "risk": {},
                "backtest": {},
                "stress": {},
                "explanation": f"Engine error: {e}"
            }

        return render_template("dashboard.html", result=result)

    return render_template("dashboard.html", result=None)

# ======================================
# LIVE PAGE
# ======================================
@app.route("/live")
def live():
    return render_template("live_trading.html")

# ======================================
# START LIVE TRADING
# ======================================
@app.route("/live/start", methods=["POST"])
def start_live():
    raw = request.form["symbol"]
    symbols = raw.split("|")
    key = "|".join(symbols)

    if key in live_engines:
        return jsonify({"status": "already_running"})

    engine = AITradingEngine(symbols)
    live_engines[key] = engine

    def run():
        while key in live_engines:
            try:
                live_results[key] = engine.run_cycle()
                print("🔁 LIVE UPDATE:", live_results[key])
                time.sleep(8)
            except Exception as e:
                print("⚠️ LIVE ERROR:", e)
                time.sleep(5)

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"status": "started"})

# ======================================
# LIVE STATUS (SAFE JSON)
# ======================================
@app.route("/live/status/<key>")
def live_status(key):
    if key not in live_engines:
        return jsonify({"running": False, "data": None})

    if key not in live_results:
        return jsonify({
            "running": True,
            "data": {
                "best_stock": "-",
                "regime": "Initializing...",
                "allocation": 0.0,
                "portfolio": {
                    "cash": "-",
                    "position": "-",
                    "portfolio_value": "-"
                },
                "risk": {
                    "volatility": 0.0,
                    "max_drawdown": 0.0,
                    "risk_level": "NORMAL"
                },
                "backtest": {"final_value": 1.0},
                "stress": {"final_value": 1.0, "survived": True},
                "explanation": "AI engine starting..."
            }
        })

    safe_data = make_json_safe(live_results[key])

    return jsonify({
        "running": True,
        "data": safe_data
    })

# ======================================
# STOP LIVE TRADING
# ======================================
@app.route("/live/stop", methods=["POST"])
def stop_live():
    key = request.form["symbol"]
    live_engines.pop(key, None)
    live_results.pop(key, None)
    return jsonify({"status": "stopped"})

# ======================================
# LOGOUT
# ======================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/graphs")
def live_graphs():
    return render_template("live_graphs.html")

@app.route("/graphs/data/<key>")
def graph_data(key):
    if key not in live_results:
        return jsonify({"active": False, "stocks": []})

    data = live_results[key]

    return jsonify({
        "active": True,
        "best_stock": data["best_stock"],
        "price": data["portfolio"].get("price"),
        "volatility": data["risk"]["volatility"],
        "drawdown": data["risk"]["max_drawdown"],
        "allocation": data["allocation"]
    })

@app.route("/risk")
def risk_page():
    return render_template("risk.html")

@app.route("/risk/status/<key>")
def risk_status(key):
    if key not in live_results:
        return jsonify({"running": False})

    data = live_results[key]

    # Safe extraction
    risk = data.get("risk", {})
    backtest = data.get("backtest", {})

    # Derived metrics
    cagr = backtest.get("CAGR", None)
    sharpe = backtest.get("Sharpe", None)
    sortino = backtest.get("Sortino", None)
    max_dd = risk.get("max_drawdown", None)

    # Calmar = CAGR / |Max DD|
    calmar = None
    if cagr is not None and max_dd not in (None, 0):
        calmar = round(cagr / abs(max_dd), 2)

    return jsonify({
        "running": True,
        "risk": {
            "CAGR": cagr,
            "Sharpe": sharpe,
            "Sortino": sortino,
            "MaxDrawdown": max_dd,
            "Calmar": calmar
        }
    })
@app.route("/portfolio-health")
def portfolio_health():
    return render_template("portfolio_health.html")


# ======================================
# RUN
# ======================================
if __name__ == "__main__":
    app.run(debug=True, threaded=True)
