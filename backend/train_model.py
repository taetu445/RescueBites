#!/usr/bin/env python3
import json
import os
import argparse
import pandas as pd
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder

# ── Paths ───────────────────────────────────────────────────────────────────────
BASE_DIR               = os.path.dirname(__file__)
DATA_PATH              = os.path.join(BASE_DIR, 'data', 'dataformodel.json')
SUMMARY_PATH           = os.path.join(BASE_DIR, 'data', 'predicted.json')
FRONTEND_SUMMARY_PATH  = os.path.abspath(
    os.path.join(BASE_DIR, '..', 'frontend', 'public', 'data', 'predicted.json')
)

# ── Load history ────────────────────────────────────────────────────────────────
def load_history(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        # no data yet: empty DataFrame
        return pd.DataFrame(columns=['name','totalEarning'])
    raw = json.load(open(path, 'r'))
    rows = []
    for day in raw:
        for it in day.get('items', []):
            rows.append({
                'name':         it.get('name'),
                'totalEarning': it.get('totalEarning', 0)
            })
    return pd.DataFrame(rows)

# ── Train & summarize ──────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--episodes', type=int, default=1,
                        help="Ignored for regression model")
    args = parser.parse_args()

    df = load_history(DATA_PATH)
    if df.empty:
        print("No historical data to train on. Exiting.")
        return

    # One‑hot encode dish names
    enc = OneHotEncoder(sparse_output=False)
    X = enc.fit_transform(df[['name']])
    y = df['totalEarning'].values.reshape(-1,1)

    # Fit linear regression
    model = LinearRegression()
    model.fit(X, y)

    # Predict expected earning for each dish
    dishes = enc.categories_[0].tolist()
    X_all  = enc.transform(pd.DataFrame({'name': dishes}))
    preds  = model.predict(X_all).flatten().round(2)

    # Build summary
    summary = {
        'trainedAt':       datetime.now().isoformat(),
        'modelType':       'LinearRegression',
        'dishes':          dishes,
        'predictedEarning': preds.tolist(),
        'bestAction': {
            'dish': dishes[int(preds.argmax())],
            'value': float(preds.max())
        }
    }

    # Write out JSON
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    with open(SUMMARY_PATH, 'w') as f:
        json.dump(summary, f, indent=2)
    os.makedirs(os.path.dirname(FRONTEND_SUMMARY_PATH), exist_ok=True)
    with open(FRONTEND_SUMMARY_PATH, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"[{datetime.now()}] Regression model trained & summary saved.")

if __name__ == '__main__':
    main()
