# SentinelAI — AI-Powered Network Intrusion Detection System

Educational Flask app using a Random Forest classifier trained on CICIDS2017 flow records.

## Windows PowerShell setup
Run in this folder:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
If activation is blocked:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Dataset
Follow `DATASET.md`. Training supports `dataset/Tuesday-WorkingHours.pcap_ISCX.csv`, or the provided `dataset/Friday-WorkingHours-Morning.pcap_ISCX.csv` as a fallback. Monday alone is not usable for training because it contains only benign records.

## Train and test
```powershell
python check_labels.py
python train_model.py
python test_model.py
```
Training creates the missing `ids_real_model.joblib` model and `model_metrics.json`. The app reports when the model file is absent; it does not train automatically at startup.

## Run website
```powershell
python app.py
```
Open http://127.0.0.1:5000. Status endpoint: http://127.0.0.1:5000/api/status.

Upload a CICIDS-style CSV containing the same feature columns used in training. The optional Label column is ignored for prediction. The browser shows up to 100 rows; download the full result CSV.

## Limitations
This is an educational flow-record classifier. It does not capture live packets or block network traffic. Metrics describe a held-out split from the selected training dataset, not guaranteed performance on other networks.
# SENTINEL.AI
