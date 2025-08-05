#!/usr/bin/env python3
import json
import os
import argparse
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_squared_error, r2_score

# ── Paths ───────────────────────────────────────────────────────────────────────
BASE_DIR               = os.path.dirname(__file__)
DATA_PATH              = os.path.join(BASE_DIR, 'data', 'dataformodel.json')
SUMMARY_PATH           = os.path.join(BASE_DIR, 'data', 'predicted.json')
FRONTEND_SUMMARY_PATH  = os.path.abspath(
    os.path.join(BASE_DIR, '..', 'frontend', 'public', 'data', 'predicted.json')
)

# ── Load history ────────────────────────────────────────────────────────────────
def load_history(path: str) -> pd.DataFrame:
    """Loads historical data from a JSON file into a pandas DataFrame."""
    if not os.path.exists(path):
        # no data yet: empty DataFrame
        return pd.DataFrame(columns=['name', 'costPerPlate', 'totalIngredientsCost', 'totalPlates', 'platesWasted', 'totalEarning'])
    
    raw = json.load(open(path, 'r'))
    rows = []
    for day in raw:
        for it in day.get('items', []):
            rows.append({
                'name': it.get('name'),
                'costPerPlate': it.get('costPerPlate', 0),
                'totalIngredientsCost': it.get('totalIngredientsCost', 0),
                'totalPlates': it.get('totalPlates', 0),
                'platesWasted': it.get('platesWasted', 0),
                'totalEarning': it.get('totalEarning', 0)
            })
    return pd.DataFrame(rows)

# ── Train & summarize ──────────────────────────────────────────────────────────
def main():
    """
    Main function to load data, train a linear regression model, and save predictions.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--episodes', type=int, default=1,
                        help="Ignored for regression model")
    args = parser.parse_args()

    df = load_history(DATA_PATH)
    
    # Filter for valid data points to prevent errors
    df = df.dropna(subset=['name', 'totalEarning'])
    if df.empty:
        print("No historical data to train on. Exiting.")
        return
        
    # Aggregate data by dish name to avoid duplicate entries for the same dish on the same day
    # and to get a more stable average for features.
    df_agg = df.groupby('name').agg({
        'costPerPlate': 'mean',
        'totalIngredientsCost': 'mean',
        'totalPlates': 'sum',
        'platesWasted': 'sum',
        'totalEarning': 'sum'
    }).reset_index()

    # Define features and target variable
    features = ['name', 'costPerPlate', 'totalIngredientsCost', 'totalPlates', 'platesWasted']
    target = 'totalEarning'

    # Filter out dishes with very little data points to avoid unstable predictions
    dish_counts = df['name'].value_counts()
    dishes_to_keep = dish_counts[dish_counts >= 1].index
    df = df[df['name'].isin(dishes_to_keep)]

    if df.empty:
        print("Not enough data per dish to train a reliable model. Exiting.")
        return

    # One-hot encode dish names
    enc = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    X_dish = enc.fit_transform(df[['name']])
    
    # Select other features
    X_numeric = df[['costPerPlate', 'totalIngredientsCost', 'totalPlates', 'platesWasted']].values
    
    # Combine features
    X = np.hstack((X_dish, X_numeric))
    y = df['totalEarning'].values.reshape(-1, 1)

    # Fit linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Evaluate the model on the training data
    y_pred_train = model.predict(X)
    mse = mean_squared_error(y, y_pred_train)
    r2 = r2_score(y, y_pred_train)
    
    print(f"Model trained. Metrics: MSE={mse:.2f}, R-squared={r2:.2f}")

    # Predict expected earning for each dish for a best-case scenario
    dishes = df_agg['name'].tolist()
    
    predicted_earnings = []
    # Create feature dataframe for prediction
    for dish in dishes:
        # Get historical data for the current dish
        dish_df = df[df['name'] == dish]

        # Use average values for the dish to predict a realistic earning
        # Set platesWasted to a low value (e.g., the minimum or 1) for a "best action" prediction
        avg_cost_per_plate = dish_df['costPerPlate'].mean()
        avg_total_ingredients_cost = dish_df['totalIngredientsCost'].mean()
        avg_total_plates = dish_df['totalPlates'].mean()
        
        # We assume a "best case" scenario for the prediction, so we set wasted plates to a low value.
        plates_wasted_for_prediction = 1
        
        predict_df = pd.DataFrame([{
            'name': dish,
            'costPerPlate': avg_cost_per_plate,
            'totalIngredientsCost': avg_total_ingredients_cost,
            'totalPlates': avg_total_plates,
            'platesWasted': plates_wasted_for_prediction
        }])

        X_predict_dish = enc.transform(predict_df[['name']])
        X_predict_numeric = predict_df[['costPerPlate', 'totalIngredientsCost', 'totalPlates', 'platesWasted']].values
        X_predict = np.hstack((X_predict_dish, X_predict_numeric))
        
        pred = model.predict(X_predict).flatten()[0].round(2)
        predicted_earnings.append(pred)

    # Enforce non-negativity and replace negative predictions with 0
    predictions_non_negative = [max(0, p) for p in predicted_earnings]
    
    # Find the best action based on the original predictions (before capping at 0)
    # This is to ensure we recommend the dish that the model believes has the highest earning potential,
    # even if its predicted value is negative due to a historical outlier.
    best_action_index = np.argmax(predicted_earnings)
    best_dish = dishes[best_action_index]
    best_value = float(predicted_earnings[best_action_index])

    # Build summary
    summary = {
        'trainedAt':        datetime.now().isoformat(),
        'modelType':        'LinearRegression',
        'features':         ['dish_one-hot'] + ['costPerPlate', 'totalIngredientsCost', 'totalPlates', 'platesWasted'],
        'dishes':           dishes,
        'predictedEarning': predictions_non_negative,
        'bestAction': {
            'dish':  best_dish,
            'value': float(best_value)
        },
        'metrics': {
            'mse': mse,
            'r2': r2
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