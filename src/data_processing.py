import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

def load_data(path):
    df = pd.read_csv(path, parse_dates=['date'], low_memory=False)
    return df

def basic_cleaning(df):
    df = df.copy()
    # Drop fully empty columns
    df = df.dropna(axis=1, how='all')
    # Remove duplicates (~2% expected)
    df = df.drop_duplicates()
    # Ensure numeric types
    num_cols = ['views','likes','comments','watch_time_minutes','video_length_minutes','subscribers','ad_revenue_usd']
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    return df

def feature_engineering(df):
    df = df.copy()
    # Engagement rate
    df['engagement'] = (df.get('likes',0).fillna(0) + df.get('comments',0).fillna(0)) / df['views'].replace(0,np.nan)
    df['watch_time_per_view'] = df['watch_time_minutes'] / df['views'].replace(0,np.nan)
    # Age of video in days from upload/report date relative to the max date
    if 'date' in df.columns:
        df['video_age_days'] = (df['date'].max() - df['date']).dt.days
    # Length ratio
    df['length_to_watch_ratio'] = df['video_length_minutes'].replace(0,np.nan) / df['watch_time_minutes'].replace(0,np.nan)
    # Fill infs and large values
    df = df.replace([np.inf, -np.inf], np.nan)
    return df

def preprocess_for_model(df, target='ad_revenue_usd', test_size=0.2, random_state=42):
    df = df.copy()
    # Select features
    drop_cols = ['video_id','date']
    X = df.drop(columns=[c for c in drop_cols if c in df.columns] + [target])
    y = df[target]

    # Identify numerical and categorical
    num_cols = X.select_dtypes(include=['number']).columns.tolist()
    cat_cols = X.select_dtypes(include=['object','category']).columns.tolist()

    # Impute numerical
    num_imputer = SimpleImputer(strategy='median')
    X_num = pd.DataFrame(num_imputer.fit_transform(X[num_cols]), columns=num_cols)

    # Impute categorical
    cat_imputer = SimpleImputer(strategy='most_frequent')
    X_cat = pd.DataFrame(cat_imputer.fit_transform(X[cat_cols]), columns=cat_cols)

    # One-hot encode categorical (limit to top categories to avoid explosion)
    enc = OneHotEncoder(handle_unknown='ignore', sparse=False)
    X_cat_enc = pd.DataFrame(enc.fit_transform(X_cat), columns=enc.get_feature_names_out(cat_cols))

    # Combine
    X_combined = pd.concat([X_num.reset_index(drop=True), X_cat_enc.reset_index(drop=True)], axis=1)

    # Scaling
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X_combined), columns=X_combined.columns)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=test_size, random_state=random_state)
    artifacts = {'num_imputer': num_imputer, 'cat_imputer': cat_imputer, 'encoder': enc, 'scaler': scaler, 'feature_columns': X_scaled.columns.tolist()}
    return X_train, X_test, y_train, y_test, artifacts
