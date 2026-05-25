"""
Crop Yield Prediction Model Training Script.
Preprocesses yield data, trains regression models, and exports the best one.
"""

import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'datasets', 'yield_data.csv')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

def generate_mock_yield_data():
    """Generates a mock dataset if the real one isn't present."""
    print("Checking for yield dataset...")
    if os.path.exists(DATA_PATH):
        print("Dataset found.")
        return pd.read_csv(DATA_PATH)
        
    print("Dataset not found. Generating mock yield dataset...")
    np.random.seed(42)
    n_samples = 1000
    
    crops = ['Rice', 'Wheat', 'Maize', 'Cotton', 'Sugarcane']
    seasons = ['Kharif', 'Rabi', 'Zaid', 'Whole Year']
    regions = ['North', 'South', 'East', 'West', 'Central']
    
    data = {
        'crop': np.random.choice(crops, n_samples),
        'season': np.random.choice(seasons, n_samples),
        'region': np.random.choice(regions, n_samples),
        'area_ha': np.random.uniform(1, 100, n_samples),
        'annual_rainfall': np.random.uniform(200, 3000, n_samples),
        'fertilizer_kg': np.random.uniform(10, 500, n_samples),
        'pesticide_kg': np.random.uniform(1, 50, n_samples)
    }
    df = pd.DataFrame(data)
    
    # Generate target variable with some logical relationships
    # Base yield + area factor + rain factor + fertilizer factor - pesticide penalty (if too high)
    df['yield_kg_per_ha'] = (
        np.random.normal(3000, 500, n_samples) +
        df['area_ha'] * 10 +
        df['annual_rainfall'] * 0.5 +
        df['fertilizer_kg'] * 2 -
        df['pesticide_kg'] * 5
    )
    # Add some noise and ensure positive
    df['yield_kg_per_ha'] = df['yield_kg_per_ha'] + np.random.normal(0, 200, n_samples)
    df['yield_kg_per_ha'] = df['yield_kg_per_ha'].clip(lower=500)
    
    # Introduce some outliers
    outlier_idx = np.random.choice(n_samples, 50, replace=False)
    df.loc[outlier_idx, 'yield_kg_per_ha'] *= np.random.uniform(2, 5, 50)
    
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    print(f"Mock dataset saved to {DATA_PATH}")
    return df

def remove_outliers_iqr(df, column):
    """Removes outliers using the Interquartile Range method."""
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    initial_shape = df.shape
    df_filtered = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    print(f"Outlier Removal ({column}): Removed {initial_shape[0] - df_filtered.shape[0]} rows.")
    return df_filtered

def preprocess_data(df):
    """Prepares data for training."""
    print("\n--- Preprocessing ---")
    
    # Handle Outliers
    df = remove_outliers_iqr(df, 'yield_kg_per_ha')
    df = remove_outliers_iqr(df, 'area_ha')
    
    # Separate features and target
    X = df.drop('yield_kg_per_ha', axis=1)
    y = df['yield_kg_per_ha']
    
    # Label Encoding for categoricals
    cat_cols = ['crop', 'season', 'region']
    encoders = {}
    
    for col in cat_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        encoders[col] = le
        
    # Scale numeric features
    num_cols = ['area_ha', 'annual_rainfall', 'fertilizer_kg', 'pesticide_kg']
    scaler = StandardScaler()
    X[num_cols] = scaler.fit_transform(X[num_cols])
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training shape: {X_train.shape}, Testing shape: {X_test.shape}")
    
    # Save transformers
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(encoders, os.path.join(MODELS_DIR, 'encoders_yield.pkl'))
    joblib.dump(scaler, os.path.join(MODELS_DIR, 'scaler_yield.pkl'))
    print("Encoders and Scaler saved.")
    
    return X_train, X_test, y_train, y_test, cat_cols, num_cols

def evaluate_model(name, model, X_test, y_test):
    """Evaluates a regression model and prints metrics."""
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"--- {name} ---")
    print(f"  RMSE : {rmse:.2f}")
    print(f"  MAE  : {mae:.2f}")
    print(f"  R²   : {r2:.4f}")
    
    return r2

def predict_yield(crop, season, region, area, rainfall, fertilizer, pesticide):
    """Function to test prediction pipeline end-to-end."""
    # Load artifacts
    encoders = joblib.load(os.path.join(MODELS_DIR, 'encoders_yield.pkl'))
    scaler = joblib.load(os.path.join(MODELS_DIR, 'scaler_yield.pkl'))
    model = joblib.load(os.path.join(MODELS_DIR, 'yield_model.pkl'))
    
    # Format input
    input_df = pd.DataFrame([{
        'crop': crop,
        'season': season,
        'region': region,
        'area_ha': area,
        'annual_rainfall': rainfall,
        'fertilizer_kg': fertilizer,
        'pesticide_kg': pesticide
    }])
    
    # Encode
    for col in ['crop', 'season', 'region']:
        try:
            input_df[col] = encoders[col].transform(input_df[col])
        except ValueError:
            # Handle unseen labels gracefully
            print(f"Warning: Unseen label for {col}. Defaulting to first class.")
            input_df[col] = encoders[col].transform([encoders[col].classes_[0]])

    
    # Scale
    num_cols = ['area_ha', 'annual_rainfall', 'fertilizer_kg', 'pesticide_kg']
    input_df[num_cols] = scaler.transform(input_df[num_cols])
    
    # Predict
    prediction = model.predict(input_df)[0]
    return prediction

def main():
    print("=========================================")
    print(" Crop Yield Model Training Pipeline ")
    print("=========================================\n")
    
    df = generate_mock_yield_data()
    X_train, X_test, y_train, y_test, cat_cols, num_cols = preprocess_data(df)
    
    print("\n--- Training Models ---")
    
    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    }
    
    best_r2 = -float('inf')
    best_model_name = ""
    best_model = None
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        r2 = evaluate_model(name, model, X_test, y_test)
        
        if r2 > best_r2:
            best_r2 = r2
            best_model_name = name
            best_model = model
            
    print(f"\n✅ Best Model Selected: {best_model_name} (R² = {best_r2:.4f})")
    
    # Save best model
    model_path = os.path.join(MODELS_DIR, 'yield_model.pkl')
    joblib.dump(best_model, model_path)
    print(f"Best model saved to {model_path}")
    
    print("\n--- Testing Prediction Function ---")
    samples = [
        ("Rice", "Kharif", "South", 10.5, 1200, 150, 15),
        ("Wheat", "Rabi", "North", 25.0, 400, 200, 25),
        ("Cotton", "Kharif", "West", 5.2, 800, 100, 30)
    ]
    
    for s in samples:
        pred_yield = predict_yield(*s)
        print(f"Input: {s} => Predicted Yield: {pred_yield:.2f} kg/ha")

if __name__ == "__main__":
    main()
