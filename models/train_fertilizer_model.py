"""
Fertilizer Recommendation Model Training Script.
Trains a RandomForest classifier to predict the best fertilizer
based on soil nutrients, crop type, and environmental conditions.
"""

import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'datasets', 'fertilizer_data.csv')
MODELS_DIR = os.path.join(BASE_DIR, 'models')


def generate_mock_fertilizer_data():
    """Generate a synthetic fertilizer recommendation dataset."""
    if os.path.exists(DATA_PATH):
        print("Dataset found.")
        return pd.read_csv(DATA_PATH)

    print("Generating mock fertilizer dataset...")
    np.random.seed(42)
    n_samples = 1200

    soil_types = ['Sandy', 'Loamy', 'Black', 'Red', 'Clayey', 'Peaty']
    crop_types = ['Rice', 'Wheat', 'Maize', 'Cotton', 'Sugarcane', 'Millets', 'Pulses']
    fertilizers = ['Urea', 'DAP', 'MOP', 'NPK 10-26-26', 'NPK 20-20-20', 'Ammonium Sulphate', 'SSP']

    records = []
    for _ in range(n_samples):
        temp = np.random.uniform(15, 45)
        humidity = np.random.uniform(30, 90)
        moisture = np.random.uniform(20, 80)
        soil = np.random.choice(soil_types)
        crop = np.random.choice(crop_types)
        nitrogen = np.random.uniform(0, 140)
        phosphorus = np.random.uniform(0, 145)
        potassium = np.random.uniform(0, 205)

        # Rule-based fertilizer assignment with some noise
        if nitrogen < 40:
            fert = 'Urea'
        elif phosphorus < 40:
            fert = 'DAP'
        elif potassium < 40:
            fert = 'MOP'
        elif nitrogen < 70 and phosphorus < 70:
            fert = 'NPK 10-26-26'
        elif nitrogen > 100 and potassium > 100:
            fert = 'Ammonium Sulphate'
        elif phosphorus < 60:
            fert = 'SSP'
        else:
            fert = 'NPK 20-20-20'

        # Add 15% noise to make it more realistic
        if np.random.random() < 0.15:
            fert = np.random.choice(fertilizers)

        records.append({
            'temperature': round(temp, 1),
            'humidity': round(humidity, 1),
            'moisture': round(moisture, 1),
            'soil_type': soil,
            'crop_type': crop,
            'nitrogen': round(nitrogen, 1),
            'phosphorus': round(phosphorus, 1),
            'potassium': round(potassium, 1),
            'fertilizer_name': fert
        })

    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    print(f"Saved {n_samples} rows to {DATA_PATH}")
    return df


def main():
    print("==========================================")
    print(" Fertilizer Model Training Pipeline")
    print("==========================================\n")

    df = generate_mock_fertilizer_data()
    print(f"Dataset shape: {df.shape}")
    print(f"Fertilizer distribution:\n{df['fertilizer_name'].value_counts()}\n")

    # Encode categoricals
    encoders = {}
    for col in ['soil_type', 'crop_type']:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    target_encoder = LabelEncoder()
    df['fertilizer_name'] = target_encoder.fit_transform(df['fertilizer_name'])
    encoders['fertilizer_name'] = target_encoder

    # Features and target
    feature_cols = ['temperature', 'humidity', 'moisture', 'soil_type', 'crop_type',
                    'nitrogen', 'phosphorus', 'potassium']
    X = df[feature_cols]
    y = df['fertilizer_name']

    # Scale numeric features
    num_cols = ['temperature', 'humidity', 'moisture', 'nitrogen', 'phosphorus', 'potassium']
    scaler = StandardScaler()
    X[num_cols] = scaler.fit_transform(X[num_cols])

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Train: {X_train.shape}, Test: {X_test.shape}")

    # Train
    model = RandomForestClassifier(n_estimators=150, max_depth=20, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {acc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred,
                                target_names=target_encoder.classes_))

    # Save artifacts
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(MODELS_DIR, 'fertilizer_model.pkl'))
    joblib.dump(scaler, os.path.join(MODELS_DIR, 'scaler_fertilizer.pkl'))
    joblib.dump(encoders, os.path.join(MODELS_DIR, 'encoders_fertilizer.pkl'))
    print("\nAll artifacts saved to models/")

    # Quick smoke test
    print("\n--- Smoke Test ---")
    test_input = pd.DataFrame([{
        'temperature': 30, 'humidity': 60, 'moisture': 40,
        'soil_type': encoders['soil_type'].transform(['Loamy'])[0],
        'crop_type': encoders['crop_type'].transform(['Wheat'])[0],
        'nitrogen': 20, 'phosphorus': 30, 'potassium': 10
    }])
    test_input[num_cols] = scaler.transform(test_input[num_cols])
    pred_idx = model.predict(test_input)[0]
    pred_name = target_encoder.inverse_transform([pred_idx])[0]
    print(f"Input: N=20, P=30, K=10, Loamy, Wheat => {pred_name}")


if __name__ == "__main__":
    main()
