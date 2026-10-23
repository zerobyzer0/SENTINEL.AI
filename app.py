from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "ids_real_model.joblib"
METRICS_PATH = ROOT / "model_metrics.json"
RESULTS_PATH = ROOT / "last_scan_results.csv"
app = Flask(__name__)
app.secret_key = "sentinelai-local-development-key"
app.config["MAX_CONTENT_LENGTH"] = 1000 * 1024 * 1024
model_bundle = None
model_error = None

def load_model():
    global model_bundle, model_error
    model_bundle = None
    model_error = None
    if not MODEL_PATH.exists():
        model_error = (
            f"Model file not found: {MODEL_PATH.name}. "
            "Run python train_model.py to create it."
        )
        return
    try:
        obj = joblib.load(MODEL_PATH)
        if not isinstance(obj, dict) or "model" not in obj or "features" not in obj:
            model_error = f"Model file is invalid: {MODEL_PATH.name}. Run python train_model.py again."
            return
        model_bundle = obj
    except Exception as exc:
        model_error = f"Could not load {MODEL_PATH.name}: {exc}"
        print("Model load error:", exc)

load_model()

def read_metrics():
    try:
        return json.loads(METRICS_PATH.read_text(encoding="utf-8")) if METRICS_PATH.exists() else {}
    except (OSError, json.JSONDecodeError):
        return {}

def predict_frame(frame):
    if model_bundle is None:
        raise ValueError(model_error or "Model is not available. Run python train_model.py.")
    frame = frame.copy()
    frame.columns = [str(c).strip() for c in frame.columns]
    features = model_bundle["features"]
    missing = [c for c in features if c not in frame.columns]
    if missing:
        raise ValueError("CSV is missing required features: " + ", ".join(missing[:8]) + (" ..." if len(missing) > 8 else ""))
    X = frame[features].copy()
    for col in X.columns:
        X[col] = pd.to_numeric(X[col], errors="coerce")
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(pd.Series(model_bundle.get("medians", {}))).fillna(0)
    predictions = model_bundle["model"].predict(X)
    output = frame.copy()
    output["prediction"] = predictions
    output["verdict"] = ["BENIGN" if str(p).strip().upper() in {"BENIGN", "NORMAL", "0"} else "ATTACK" for p in predictions]
    if hasattr(model_bundle["model"], "predict_proba"):
        output["confidence_percent"] = (model_bundle["model"].predict_proba(X).max(axis=1) * 100).round(2)
    else:
        output["confidence_percent"] = ""
    return output

@app.route("/")
def index():
    metrics = read_metrics()
    return render_template("index.html", model_ready=model_bundle is not None,
                           model_error=model_error, metrics=metrics)

@app.route("/api/status")
def status():
    return jsonify({"model_ready": model_bundle is not None, "model_file": MODEL_PATH.name,
                    "model_error": model_error,
                    "classes": model_bundle.get("classes", []) if model_bundle else []})

@app.route("/scan", methods=["POST"])
def scan():
    upload = request.files.get("file")
    if not upload or not upload.filename:
        flash("Choose a CSV file first.", "error")
        return redirect(url_for("index"))
    if not upload.filename.lower().endswith(".csv"):
        flash("Only CSV files are supported.", "error")
        return redirect(url_for("index"))
    try:
        frame = pd.read_csv(upload, low_memory=False)
        if frame.empty:
            raise ValueError("CSV has no data rows.")
        results = predict_frame(frame)
        results.to_csv(RESULTS_PATH, index=False)
        benign = int((results["verdict"] == "BENIGN").sum())
        attacks = int((results["verdict"] == "ATTACK").sum())
        rows = results.head(100).fillna("").to_dict(orient="records")
        return render_template("results.html", rows=rows, total=len(results), benign=benign,
                               attacks=attacks, columns=list(results.columns), truncated=len(results) > 100)
    except Exception as exc:
        flash("Could not scan CSV: " + str(exc), "error")
        return redirect(url_for("index"))

@app.route("/download-results")
def download_results():
    if not RESULTS_PATH.exists():
        flash("Run a CSV scan before downloading results.", "error")
        return redirect(url_for("index"))
    return send_file(RESULTS_PATH, as_attachment=True, download_name="sentinelai_scan_results.csv", mimetype="text/csv")

@app.errorhandler(413)
def too_large(_error):
    flash("Upload exceeds the 1 GB limit.", "error")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
