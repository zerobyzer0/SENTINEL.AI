# Dataset setup
Official source: https://www.unb.ca/cic/datasets/ids-2017.html

1. Prefer `Tuesday-WorkingHours.pcap_ISCX.csv`; `Friday-WorkingHours-Morning.pcap_ISCX.csv` is also supported. Do not use Monday as the only training file: it contains BENIGN traffic only, so the model cannot learn to identify attacks.
2. Copy the selected CSV into this project's `dataset` folder. If both supported files are present, training uses Tuesday.
3. Run `python check_labels.py`, then `python train_model.py`.

Training samples up to 30,000 records per class to limit memory use while retaining each class. The generated `ids_real_model.joblib` model and `model_metrics.json` are local files. Keep dataset CSVs out of GitHub.
