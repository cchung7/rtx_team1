#!/usr/bin/env python3
"""
Script to train a BALANCED model - not too simple, not too complex
"""
import sys
import os
import pandas as pd
import numpy as np
from datetime import timedelta
from lightgbm import LGBMRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
import pickle
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_balanced_model():
    """Train a balanced model with ~15-20 features"""
    
    logger.info("="*60)
    logger.info("Training BALANCED Model (Sweet Spot)")
    logger.info("="*60)
    
    # Load data
    logger.info("Loading daily_aqi_by_county_2024.csv...")
    df = pd.read_csv('data/daily_aqi_by_county_2024.csv', parse_dates=['Date'])
    logger.info(f"Loaded {len(df)} records")
    
    # Basic cleaning
    df = df.drop_duplicates(subset=['Date', 'State Code', 'County Code']).copy()
    df = df.sort_values(['State Code', 'County Code', 'Date']).reset_index(drop=True)
    logger.info(f"After cleaning: {len(df)} records")
    
    # Add BALANCED feature set (not too many, not too few)
    def add_balanced_features(group):
        group = group.sort_values('Date')
        
        # Core lag features (from prototype - proven to work)
        group['AQI_lag1'] = group['AQI'].shift(1)
        group['AQI_lag3'] = group['AQI'].shift(3)
        group['AQI_lag7'] = group['AQI'].shift(7)
        
        # ONE rolling average (7-day - most important)
        group['AQI_rolling_7'] = group['AQI'].rolling(window=7, min_periods=1).mean()
        
        # Basic temporal features (only the most important)
        group['day_of_week'] = group['Date'].dt.dayofweek
        group['month'] = group['Date'].dt.month
        
        # ONE additional lag (14-day for longer trend)
        group['AQI_lag14'] = group['AQI'].shift(14)
        
        return group
    
    logger.info("Adding balanced features...")
    df = df.groupby(['State Code', 'County Code'], group_keys=False).apply(add_balanced_features)
    
    # Drop rows with NaN (from lag features)
    df = df.dropna(subset=['AQI_lag1', 'AQI_lag3', 'AQI_lag7', 'AQI_lag14']).reset_index(drop=True)
    logger.info(f"After feature engineering: {len(df)} records")
    
    # Define BALANCED feature set (~15 features)
    feature_cols = [
        'State Code', 'County Code',  # Location identifiers
        'AQI_lag1', 'AQI_lag3', 'AQI_lag7', 'AQI_lag14',  # Lag features
        'AQI_rolling_7',  # ONE rolling average
        'day_of_week', 'month',  # Basic temporal
        # Add a few more meaningful features
        'AQI_rolling_3',  # Short-term trend
        'AQI_std_7',  # Volatility measure
    ]
    
    # Add the additional features
    def add_final_features(group):
        group = group.sort_values('Date')
        group['AQI_rolling_3'] = group['AQI'].rolling(window=3, min_periods=1).mean()
        group['AQI_std_7'] = group['AQI'].rolling(window=7, min_periods=1).std().fillna(0)
        return group
    
    df = df.groupby(['State Code', 'County Code'], group_keys=False).apply(add_final_features)
    
    target_col = 'AQI'
    X = df[feature_cols]
    y = df[target_col]
    
    logger.info(f"Final feature set: {len(feature_cols)} features")
    logger.info(f"Features: {feature_cols}")
    
    # Time-based split (like prototype)
    df_sorted = df.sort_values('Date').reset_index(drop=True)
    split_idx = int(len(df_sorted) * 0.8)
    
    X_train = df_sorted[feature_cols].iloc[:split_idx]
    y_train = df_sorted[target_col].iloc[:split_idx]
    X_test = df_sorted[feature_cols].iloc[split_idx:]
    y_test = df_sorted[target_col].iloc[split_idx:]
    
    logger.info(f"Training set: {len(X_train)} samples")
    logger.info(f"Test set: {len(X_test)} samples")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train BALANCED LightGBM with proper regularization
    logger.info("Training balanced LightGBM model...")
    model = LGBMRegressor(
        objective='regression',
        random_state=42,
        n_estimators=200,  # More trees but with regularization
        learning_rate=0.05,  # Lower learning rate
        max_depth=4,  # Shallower trees (less overfitting)
        num_leaves=15,  # Fewer leaves (less complexity)
        subsample=0.8,  # Subsampling
        colsample_bytree=0.8,  # Feature subsampling
        reg_alpha=0.1,  # L1 regularization
        reg_lambda=0.1,  # L2 regularization
        min_child_samples=20,  # Minimum samples per leaf
        min_split_gain=0.01,  # Minimum gain to split
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test_scaled)
    
    # Calculate metrics
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    mae = np.mean(np.abs(y_test - y_pred))
    
    logger.info("="*60)
    logger.info("BALANCED Model Performance:")
    logger.info(f"  MSE:  {mse:.2f}")
    logger.info(f"  RMSE: {rmse:.2f}")
    logger.info(f"  MAE:  {mae:.2f}")
    logger.info(f"  R²:   {r2:.4f}")
    logger.info("="*60)
    
    # Cross-validation to check for overfitting
    logger.info("Performing cross-validation...")
    tscv = TimeSeriesSplit(n_splits=5)
    cv_scores = []
    
    for train_idx, val_idx in tscv.split(X_train_scaled):
        X_cv_train, X_cv_val = X_train_scaled[train_idx], X_train_scaled[val_idx]
        y_cv_train, y_cv_val = y_train.iloc[train_idx], y_train.iloc[val_idx]
        
        cv_model = LGBMRegressor(
            objective='regression',
            random_state=42,
            n_estimators=200,
            learning_rate=0.05,
            max_depth=4,
            num_leaves=15,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=0.1,
            min_child_samples=20,
            min_split_gain=0.01,
        )
        
        cv_model.fit(X_cv_train, y_cv_train)
        y_cv_pred = cv_model.predict(X_cv_val)
        cv_r2 = r2_score(y_cv_val, y_cv_pred)
        cv_scores.append(cv_r2)
    
    cv_mean = np.mean(cv_scores)
    cv_std = np.std(cv_scores)
    
    logger.info(f"Cross-validation R²: {cv_mean:.4f} ± {cv_std:.4f}")
    
    # Check for overfitting
    overfitting_gap = r2 - cv_mean
    logger.info(f"Overfitting gap: {overfitting_gap:.4f}")
    
    if overfitting_gap > 0.1:
        logger.warning("Potential overfitting detected!")
    else:
        logger.info("Model appears well-regularized")
    
    # Save model and scaler
    os.makedirs('models', exist_ok=True)
    
    # Save model
    model_path = 'models/balanced_lightgbm_model.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump({
            'model': model,
            'scaler': scaler,
            'feature_names': feature_cols,
            'metrics': {
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2,
                'cv_r2_mean': cv_mean,
                'cv_r2_std': cv_std,
                'overfitting_gap': overfitting_gap
            },
            'model_type': 'balanced',
            'version': '20251008_balanced'
        }, f)
    
    # Save scaler separately
    scaler_path = 'models/balanced_pipeline.pkl'
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    
    logger.info(f"Balanced model saved to: {model_path}")
    logger.info(f"Balanced scaler saved to: {scaler_path}")
    
    return {
        'model': model,
        'scaler': scaler,
        'metrics': {'mse': mse, 'rmse': rmse, 'mae': mae, 'r2': r2},
        'feature_names': feature_cols,
        'cv_scores': cv_scores
    }

if __name__ == '__main__':
    try:
        result = train_balanced_model()
        print("\nBalanced model training completed!")
        print(f"R² Score: {result['metrics']['r2']:.4f}")
        print(f"Cross-validation R²: {result['cv_scores']}")
        print("You can now compare all three models in the web interface.")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
