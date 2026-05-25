"""
Crop Recommendation Data Preparation Script.
Performs Exploratory Data Analysis (EDA) and preprocesses the dataset
for machine learning model training.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Configuration
DATASET_PATH = '../datasets/Crop_recommendation.csv'
OUTPUT_DIR = '../datasets'
MODELS_DIR = '../models'

def create_mock_dataset(path):
    """Creates a mock dataset if the actual one is not found."""
    print(f"Dataset not found at {path}. Generating a mock dataset for demonstration...")
    np.random.seed(42)
    
    crops = ['rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas',
             'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate',
             'banana', 'mango', 'grapes', 'watermelon', 'muskmelon', 'apple',
             'orange', 'papaya', 'coconut', 'cotton', 'jute', 'coffee']
    
    n_samples = 2200
    
    data = {
        'N': np.random.randint(0, 140, n_samples),
        'P': np.random.randint(5, 145, n_samples),
        'K': np.random.randint(5, 205, n_samples),
        'temperature': np.random.uniform(8.8, 43.6, n_samples),
        'humidity': np.random.uniform(14.2, 99.9, n_samples),
        'ph': np.random.uniform(3.5, 9.9, n_samples),
        'rainfall': np.random.uniform(20.2, 298.5, n_samples),
        'label': np.random.choice(crops, n_samples)
    }
    
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)
    print(f"Mock dataset saved to {path}\n")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_full_path = os.path.join(script_dir, DATASET_PATH)

    if not os.path.exists(dataset_full_path):
        create_mock_dataset(dataset_full_path)

    # 1. Load Dataset
    print("--- 1. Loading Dataset ---")
    df = pd.read_csv(dataset_full_path)
    print("Dataset loaded successfully.\n")

    # 2. Exploratory Data Analysis (EDA)
    print("--- 2. Exploratory Data Analysis (EDA) ---")
    print(f"Shape of dataset: {df.shape}")
    print("\nDataset Info:")
    df.info()
    print("\nDataset Description:")
    print(df.describe())

    # Check for nulls and duplicates
    null_counts = df.isnull().sum()
    print(f"\nNull values in each column:\n{null_counts}")
    if null_counts.sum() > 0:
        print("Dropping rows with null values...")
        df.dropna(inplace=True)

    duplicate_count = df.duplicated().sum()
    print(f"\nNumber of duplicate rows: {duplicate_count}")
    if duplicate_count > 0:
        print("Dropping duplicate rows...")
        df.drop_duplicates(inplace=True)

    # Plot Class Distribution
    print("\nGenerating class distribution plot...")
    plt.figure(figsize=(15, 6))
    sns.countplot(data=df, x='label', order=df['label'].value_counts().index, palette='viridis')
    plt.xticks(rotation=45, ha='right')
    plt.title('Distribution of Crop Types')
    plt.tight_layout()
    dist_plot_path = os.path.join(script_dir, OUTPUT_DIR, 'crop_distribution.png')
    plt.savefig(dist_plot_path)
    plt.close()
    print(f"Class distribution plot saved to {dist_plot_path}")

    # Plot Correlation Heatmap
    print("\nGenerating correlation heatmap...")
    plt.figure(figsize=(10, 8))
    # Exclude the label column for correlation
    corr_matrix = df.drop('label', axis=1).corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title('Feature Correlation Heatmap')
    plt.tight_layout()
    corr_plot_path = os.path.join(script_dir, OUTPUT_DIR, 'crop_correlation.png')
    plt.savefig(corr_plot_path)
    plt.close()
    print(f"Correlation heatmap saved to {corr_plot_path}\n")

    # 3. Preprocessing
    print("--- 3. Preprocessing ---")
    
    # Separate features and target
    X = df.drop('label', axis=1)
    y = df['label']

    # Label Encoding
    print("Encoding target labels...")
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Train/Test Split (80/20)
    print("Splitting dataset (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)
    
    # Scaling
    print("Scaling features using StandardScaler...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 4. Save Objects and Datasets
    print("\n--- 4. Saving Artifacts ---")
    
    # Convert back to DataFrame to save as CSV
    train_df = pd.DataFrame(X_train_scaled, columns=X.columns)
    train_df['label_encoded'] = y_train
    test_df = pd.DataFrame(X_test_scaled, columns=X.columns)
    test_df['label_encoded'] = y_test

    train_csv_path = os.path.join(script_dir, OUTPUT_DIR, 'train_crop.csv')
    test_csv_path = os.path.join(script_dir, OUTPUT_DIR, 'test_crop.csv')
    
    train_df.to_csv(train_csv_path, index=False)
    test_df.to_csv(test_csv_path, index=False)
    print(f"Preprocessed train dataset saved to {train_csv_path}")
    print(f"Preprocessed test dataset saved to {test_csv_path}")

    scaler_path = os.path.join(script_dir, MODELS_DIR, 'scaler_crop.pkl')
    le_path = os.path.join(script_dir, MODELS_DIR, 'label_encoder_crop.pkl')
    
    joblib.dump(scaler, scaler_path)
    joblib.dump(label_encoder, le_path)
    print(f"Scaler saved to {scaler_path}")
    print(f"Label Encoder saved to {le_path}\n")

    # 5. Baseline Model Evaluation
    print("--- 5. Baseline Model Potential Estimate ---")
    print("Training a quick Logistic Regression model as a baseline...")
    
    baseline_model = LogisticRegression(max_iter=1000, random_state=42)
    baseline_model.fit(X_train_scaled, y_train)
    
    y_pred = baseline_model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    
    print(f"Baseline Accuracy: {acc * 100:.2f}%")
    print("\nClassification Report (Baseline):")
    # To prevent extremely long output in the console, we just print the accuracy.
    # The full report is useful for debugging.
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

if __name__ == "__main__":
    main()
