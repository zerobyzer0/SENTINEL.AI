"""Smoke-test the saved model against sample records from its source CSV."""
from pathlib import Path
import joblib
import pandas as pd

root = Path(__file__).resolve().parent
model_path = root / "ids_real_model.joblib"
dataset_dir = root / "dataset"
if not model_path.exists():
    raise SystemExit("Model missing. Run: python train_model.py")
bundle = joblib.load(model_path)
dataset_name = bundle.get("dataset")
if not dataset_name:
    dataset_name = next((name for name in (
        "Tuesday-WorkingHours.pcap_ISCX.csv",
        "Friday-WorkingHours-Morning.pcap_ISCX.csv",
    ) if (dataset_dir / name).exists()), None)
if not dataset_name:
    raise SystemExit("Training dataset missing. Put the dataset used for training in dataset/.")
data_path = dataset_dir / dataset_name
if not data_path.exists():
    raise SystemExit(f"Training dataset missing: {data_path}")
print("Model loaded:", type(bundle["model"]).__name__)
print("Dataset:", data_path.name)
print("Features:", len(bundle["features"]))
print("Classes:", ", ".join(map(str, bundle["classes"])))
sample = pd.read_csv(data_path, nrows=5, low_memory=False)
sample.columns = [str(c).strip() for c in sample.columns]
missing = [c for c in bundle["features"] if c not in sample.columns]
if missing:
    raise SystemExit("Feature mismatch: " + ", ".join(missing[:10]))
X = sample[bundle["features"]].copy()
for col in X.columns:
    X[col] = pd.to_numeric(X[col], errors="coerce")
X = X.replace([float("inf"), float("-inf")], float("nan"))
X = X.fillna(pd.Series(bundle.get("medians", {}))).fillna(0)
for i, value in enumerate(bundle["model"].predict(X), 1):
    verdict = "BENIGN" if str(value).upper() == "BENIGN" else "ATTACK"
    print(f"Row {i}: {value} ({verdict})")
print("Smoke test passed.")
