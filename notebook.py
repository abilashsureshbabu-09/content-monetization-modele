"""Content Monetization Modeler - notebook-style runnable script.

This script covers:
- Data loading
- EDA (basic)
- Preprocessing & feature engineering
- Training 5 regression models
- Evaluation & saving best model
Usage:
    python notebook.py --data path/to/dataset.csv
"""
import argparse, os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.data_processing import load_data, basic_cleaning, feature_engineering, preprocess_for_model
from src.modeling import train_and_evaluate, save_model
import joblib

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--data', type=str, default='data/youtube_monetization.csv', help='Path to CSV dataset')
    p.add_argument('--model-out', type=str, default='models/best_model.joblib', help='Path to save best model')
    return p.parse_args()

def main():
    args = parse_args()
    os.makedirs('models', exist_ok=True)

    print('Loading data...', args.data)
    df = load_data(args.data)
    print('Initial shape:', df.shape)

    df = basic_cleaning(df)
    df = feature_engineering(df)
    print('After feature engineering shape:', df.shape)

    # Quick EDA prints
    print('\n--- EDA ---')
    print(df.describe().T.head(15))
    print('\nMissing values percent:')
    print((df.isna().mean()*100).sort_values(ascending=False).head(10))

    # Simple correlation plot for numeric columns
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    if 'ad_revenue_usd' in num_cols:
        plt.figure(figsize=(10,8))
        sns.heatmap(df[num_cols].corr(), annot=True, fmt='.2f', cmap='vlag')
        plt.title('Numeric correlation matrix')
        plt.tight_layout()
        plt.savefig('assets/correlation_matrix.png')
        print('Saved correlation matrix to assets/correlation_matrix.png')

    # Preprocess & split
    X_train, X_test, y_train, y_test, artifacts = preprocess_for_model(df)
    print('Train size:', X_train.shape, 'Test size:', X_test.shape)

    # Train and evaluate
    results, best_name, best_model = train_and_evaluate(X_train, y_train, X_test, y_test)
    print('\nModel results:')
    for name, info in results.items():
        print(name, info['metrics'])

    print('\nBest model:', best_name)
    save_model({'model': best_model, 'artifacts': artifacts}, args.model_out)
    print('Saved best model bundle to', args.model_out)

if __name__ == '__main__':
    main()
