"""Train and evaluate a Random Forest on a supported CICIDS2017 CSV."""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "dataset"
PREFERRED_DATASETS = (
    "Tuesday-WorkingHours.pcap_ISCX.csv",
    "Friday-WorkingHours-Morning.pcap_ISCX.csv",
)
DATA = next((DATA_DIR / name for name in PREFERRED_DATASETS if (DATA_DIR / name).exists()), None)
MODEL = ROOT / "ids_real_model.joblib"
METRICS = ROOT / "model_metrics.json"
MAX_PER_CLASS = 30000

def main():
    if DATA is None:
        expected = "\n".join(str(DATA_DIR / name) for name in PREFERRED_DATASETS)
        raise SystemExit(
            "No supported labeled dataset found. Add Tuesday-WorkingHours.pcap_ISCX.csv "
            "or Friday-WorkingHours-Morning.pcap_ISCX.csv to the dataset folder.\n"
            "Monday is not suitable because it contains only BENIGN records.\nExpected paths:\n" + expected
        )
    print("Reading dataset; this may take a few minutes...")
    df = pd.read_csv(DATA, low_memory=False)
    df.columns = [str(c).strip() for c in df.columns]
    label_col = next((c for c in df.columns if c.lower() == "label"), None)
    if label_col is None:
        raise SystemExit("No Label column found. Check that this is a supported CICIDS2017 CSV.")
    df = df.dropna(subset=[label_col]).copy()
    df[label_col] = df[label_col].astype(str).str.strip()
    original_counts = df[label_col].value_counts()
    if len(original_counts) < 2:
        raise SystemExit("Only one label found. Use Tuesday-WorkingHours.pcap_ISCX.csv, not Monday.")
    # Cap each class to make training feasible on a typical student laptop.
    parts = []
    for _, group in df.groupby(label_col, sort=True):
        parts.append(group.sample(n=MAX_PER_CLASS, random_state=42) if len(group) > MAX_PER_CLASS else group)
    data = pd.concat(parts, ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
    y = data[label_col].astype(str)
    X = data.drop(columns=[label_col]).copy()
    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce")
    X = X.replace([np.inf, -np.inf], np.nan).dropna(axis=1, how="all")
    medians = X.median(numeric_only=True).fillna(0)
    X = X.fillna(medians).fillna(0)
    X = X.loc[:, X.nunique(dropna=False) > 1]
    if X.empty:
        raise SystemExit("No usable numeric features found.")
    if y.value_counts().min() < 2:
        raise SystemExit("Every class needs at least two rows.")
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=120, class_weight="balanced_subsample", n_jobs=-1, random_state=42)
    print(f"Source rows: {len(df):,}; sampled rows: {len(data):,}; features: {X.shape[1]}")
    print(f"Training {len(Xtr):,} rows; testing {len(Xte):,} rows...")
    model.fit(Xtr, ytr)
    pred = model.predict(Xte)
    metrics = {
        "dataset": DATA.name, "source_rows": int(len(df)), "sampled_rows": int(len(data)),
        "features": int(X.shape[1]), "classes": sorted(y.unique().tolist()),
        "class_counts_before_sampling": {str(k): int(v) for k, v in original_counts.items()},
        "accuracy": float(accuracy_score(yte, pred)),
        "precision_weighted": float(precision_score(yte, pred, average="weighted", zero_division=0)),
        "recall_weighted": float(recall_score(yte, pred, average="weighted", zero_division=0)),
        "f1_weighted": float(f1_score(yte, pred, average="weighted", zero_division=0)),
        "classification_report": classification_report(yte, pred, output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(yte, pred, labels=model.classes_).tolist(),
        "class_labels_for_confusion_matrix": model.classes_.tolist(),
        "sampling_note": f"Maximum {MAX_PER_CLASS} records per class; stratified 80/20 test split."
    }
    bundle = {"model": model, "features": X.columns.tolist(),
              "medians": {str(k): float(v) for k, v in medians.items() if pd.notna(v)},
              "classes": model.classes_.tolist(), "dataset": DATA.name}
    joblib.dump(bundle, MODEL)
    METRICS.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("\nTRAINING COMPLETE")
    print("Model:", MODEL.name, "| Metrics:", METRICS.name)
    print(f"Accuracy: {metrics['accuracy']:.2%}")
    print(f"Weighted precision: {metrics['precision_weighted']:.2%}")
    print(f"Weighted recall: {metrics['recall_weighted']:.2%}")
    print(f"Weighted F1: {metrics['f1_weighted']:.2%}")
    print("\nPer-class report:\n", classification_report(yte, pred, zero_division=0))
    print(f"Note: these results describe the held-out {DATA.name} sample, not every network.")
if __name__ == "__main__":
    main()
