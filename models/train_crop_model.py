"""
Crop Recommendation Model Training Script.
Trains Decision Tree, Random Forest, and KNN models, compares them,
saves the best model, and provides a prediction function.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Configuration
DATASETS_DIR = '../datasets'
MODELS_DIR = '../models'

def train_and_evaluate_models(X_train, y_train, X_test, y_test, class_names):
    """Trains models, evaluates them, and returns the best model."""
    models = {
        'Decision Tree': DecisionTreeClassifier(max_depth=10, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'KNN': KNeighborsClassifier(n_neighbors=5)
    }

    best_model = None
    best_acc = 0
    best_model_name = ""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("\n--- Model Training and Evaluation ---")
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        
        print(f"{name} Accuracy: {acc * 100:.2f}%")
        print(f"\nClassification Report ({name}):")
        # Print a short version of the report if there are many classes to avoid spam
        report = classification_report(y_test, y_pred, target_names=class_names, output_dict=True)
        print(f"Macro Avg F1-Score: {report['macro avg']['f1-score']:.4f}")
        
        # Save Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(12, 10))
        sns.heatmap(cm, annot=False, cmap='Blues', xticklabels=class_names, yticklabels=class_names)
        plt.title(f'Confusion Matrix - {name}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        
        cm_path = os.path.join(script_dir, DATASETS_DIR, f'cm_{name.replace(" ", "_").lower()}.png')
        plt.savefig(cm_path)
        plt.close()
        print(f"Confusion Matrix saved to {cm_path}")
        
        if acc > best_acc:
            best_acc = acc
            best_model = model
            best_model_name = name

    print(f"\nBest Model Selected: {best_model_name} with {best_acc * 100:.2f}% Accuracy")
    return best_model

def predict_crop(N, P, K, temperature, humidity, ph, rainfall):
    """
    Predicts the recommended crop given soil and weather parameters.
    Returns the predicted crop name and confidence percentage.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    scaler_path = os.path.join(script_dir, 'scaler_crop.pkl')
    le_path = os.path.join(script_dir, 'label_encoder_crop.pkl')
    model_path = os.path.join(script_dir, 'crop_model.pkl')
    
    # Load artifacts
    if not all(os.path.exists(p) for p in [scaler_path, le_path, model_path]):
        return "Error: Missing ML artifacts", 0.0
        
    scaler = joblib.load(scaler_path)
    label_encoder = joblib.load(le_path)
    model = joblib.load(model_path)
    
    # Prepare input array
    features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
    
    # Scale features
    features_scaled = scaler.transform(features)
    
    # Predict
    predicted_idx = model.predict(features_scaled)[0]
    predicted_crop = label_encoder.inverse_transform([predicted_idx])[0]
    
    # Calculate confidence
    confidence = 0.0
    if hasattr(model, 'predict_proba'):
        probabilities = model.predict_proba(features_scaled)[0]
        confidence = probabilities[predicted_idx] * 100
    
    return predicted_crop, confidence

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    train_path = os.path.join(script_dir, DATASETS_DIR, 'train_crop.csv')
    test_path = os.path.join(script_dir, DATASETS_DIR, 'test_crop.csv')
    le_path = os.path.join(script_dir, 'label_encoder_crop.pkl')
    model_save_path = os.path.join(script_dir, 'crop_model.pkl')

    if not os.path.exists(train_path) or not os.path.exists(test_path):
        print("Error: train_crop.csv or test_crop.csv not found. Run data_prep_crop.py first.")
        sys.exit(1)
        
    print("--- 1. Loading Preprocessed Data ---")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    X_train = train_df.drop('label_encoded', axis=1)
    y_train = train_df['label_encoded']
    
    X_test = test_df.drop('label_encoded', axis=1)
    y_test = test_df['label_encoded']
    
    print(f"Train set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Load Label Encoder to get class names
    label_encoder = joblib.load(le_path)
    class_names = label_encoder.classes_

    # 2 & 3. Train, Evaluate, and Compare
    best_model = train_and_evaluate_models(X_train, y_train, X_test, y_test, class_names)
    
    # 4 & 5. Save the best model
    joblib.dump(best_model, model_save_path)
    print(f"Best model saved to {model_save_path}")
    
    # 6. Test the predict_crop function
    print("\n--- Testing predict_crop function ---")
    sample_inputs = [
        {"N": 90, "P": 42, "K": 43, "temperature": 20.8, "humidity": 82.0, "ph": 6.5, "rainfall": 202.9},
        {"N": 104, "P": 18, "K": 30, "temperature": 23.6, "humidity": 60.3, "ph": 6.7, "rainfall": 140.9},
        {"N": 20, "P": 30, "K": 10, "temperature": 15.0, "humidity": 40.0, "ph": 5.5, "rainfall": 50.0}
    ]
    
    for i, sample in enumerate(sample_inputs):
        crop, conf = predict_crop(**sample)
        print(f"Sample {i+1} Output: Predicted Crop = {crop}, Confidence = {conf:.2f}%")

if __name__ == "__main__":
    main()
