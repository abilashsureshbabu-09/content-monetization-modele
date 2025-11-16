import numpy as np
import joblib
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

def get_models(random_state=42):
    models = {
        'LinearRegression': LinearRegression(),
        'Ridge': Ridge(random_state=random_state),
        'Lasso': Lasso(random_state=random_state),
        'RandomForest': RandomForestRegressor(n_estimators=100, random_state=random_state),
        'XGBoost': XGBRegressor(n_estimators=100, random_state=random_state, verbosity=0)
    }
    return models

def evaluate_model(model, X_test, y_test):
    preds = model.predict(X_test)
    r2 = r2_score(y_test, preds)
    rmse = mean_squared_error(y_test, preds, squared=False)
    mae = mean_absolute_error(y_test, preds)
    return {'r2': r2, 'rmse': rmse, 'mae': mae}

def train_and_evaluate(X_train, y_train, X_test, y_test):
    models = get_models()
    results = {}
    for name, m in models.items():
        m.fit(X_train, y_train)
        results[name] = {'model': m, 'metrics': evaluate_model(m, X_test, y_test)}
    # Select best by RMSE
    best_name = min(results.keys(), key=lambda k: results[k]['metrics']['rmse'])
    best_model = results[best_name]['model']
    return results, best_name, best_model

def save_model(model, path):
    joblib.dump(model, path)

def load_model(path):
    return joblib.load(path)
