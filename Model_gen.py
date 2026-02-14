import pandas as pd
import numpy as np
import os
import joblib

from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report

# ======================================================
# CONFIGURATION
# ======================================================
DATA_FOLDER = "data"

VOL_WINDOW = 20
SHORT_MA = 20
LONG_MA = 50

HIGH_VOL_THRESHOLD = 0.20
CRASH_DRAWDOWN = -0.20

REQUIRED_COLUMNS = ["Date", "Close"]

# ======================================================
# RULE-BASED LABEL GENERATOR (GROUND TRUTH)
# ======================================================
def detect_market_state(row):
    if row["drawdown"] <= CRASH_DRAWDOWN:
        return "Crash"
    elif row["volatility"] >= HIGH_VOL_THRESHOLD:
        return "High Volatility"
    elif row["ma_short"] > row["ma_long"]:
        return "Calm Bull"
    else:
        return "Calm Bear"

# ======================================================
# PROCESS SINGLE STOCK FILE
# ======================================================
def process_stock(file_path):
    df = pd.read_csv(file_path, parse_dates=["Date"])

    # Validate schema
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    df = df.sort_values("Date").reset_index(drop=True)

    # ----------------------
    # Feature Engineering
    # ----------------------
    df["return"] = df["Close"].pct_change()
    df["volatility"] = (
        df["return"].rolling(VOL_WINDOW).std() * np.sqrt(252)
    )

    df["ma_short"] = df["Close"].rolling(SHORT_MA).mean()
    df["ma_long"] = df["Close"].rolling(LONG_MA).mean()

    df["rolling_max"] = df["Close"].cummax()
    df["drawdown"] = (
        df["Close"] - df["rolling_max"]
    ) / df["rolling_max"]

    df.dropna(inplace=True)

    # Market state label
    df["market_state"] = df.apply(detect_market_state, axis=1)

    return df

# ======================================================
# LOAD ALL STOCK FILES
# ======================================================
all_data = []

for file in os.listdir(DATA_FOLDER):
    if file.endswith(".csv"):
        try:
            print(f"Processing {file}")
            stock_df = process_stock(os.path.join(DATA_FOLDER, file))
            if not stock_df.empty:
                all_data.append(stock_df)
        except Exception as e:
            print(f"Skipping {file}: {e}")

if len(all_data) == 0:
    raise RuntimeError("❌ No valid stock files processed")

df = pd.concat(all_data, ignore_index=True)
print(f"\n✅ Total samples: {len(df)}")

# ======================================================
# FEATURES & TARGET
# ======================================================
FEATURES = [
    "return",
    "volatility",
    "ma_short",
    "ma_long",
    "drawdown"
]

X = df[FEATURES]
y = df["market_state"]

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ======================================================
# MODEL TRAINING (TIME-SERIES SAFE)
# ======================================================
tscv = TimeSeriesSplit(n_splits=5)

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=6,
    random_state=42,
    class_weight="balanced"
)

labels = np.arange(len(label_encoder.classes_))

for fold, (train_idx, test_idx) in enumerate(tscv.split(X_scaled), 1):
    print(f"\nFold {fold}")

    X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
    y_train, y_test = y_encoded[train_idx], y_encoded[test_idx]

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print(
        classification_report(
            y_test,
            y_pred,
            labels=labels,
            target_names=label_encoder.classes_,
            zero_division=0
        )
    )

# ======================================================
# SAVE MODEL (EXTRACTION)
# ======================================================
joblib.dump(model, "market_state_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(label_encoder, "label_encoder.pkl")

print("\n✅ Model artifacts saved:")
print(" - market_state_model.pkl")
print(" - scaler.pkl")
print(" - label_encoder.pkl")
