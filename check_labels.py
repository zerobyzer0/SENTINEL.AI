from pathlib import Path
import pandas as pd

folder = Path(__file__).resolve().parent / "dataset"
files = sorted(folder.glob("*.csv"))
if not files:
    print("No CSV files found in dataset folder.")
for path in files:
    print("\n" + "=" * 45)
    print("File:", path.name)
    counts = {}
    try:
        for chunk in pd.read_csv(path, chunksize=100000, low_memory=False):
            chunk.columns = chunk.columns.astype(str).str.strip()
            col = next((c for c in chunk.columns if c.lower() == "label"), None)
            if col is None:
                print("Label column not found.")
                break
            for label, count in chunk[col].astype(str).str.strip().value_counts().items():
                counts[label] = counts.get(label, 0) + int(count)
        for label, count in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"{label}: {count:,}")
    except Exception as exc:
        print("Could not read file:", exc)
