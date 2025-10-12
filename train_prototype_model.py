#!/usr/bin/env python3
"""
Script to train the PROTOTYPE model (exact replica of lightgbm1.ipynb)
This creates a baseline model for comparison
"""
import sys
import os
import pandas as pd
import numpy as np
from datetime import timedelta
from lightgbm import LGBMRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import pickle
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_prototype_model():
    """Train the exact prototype model from lightgbm1.ipynb"""
    
    logger.info("="*60)
    logger.info("Training PROTOTYPE Model (Exact Replica)")
    logger.info("="*60)
    
    # Load data (same as prototype)
    logger.info("Loading encoded_dataset.csv...")
    df = pd.read_csv('data/encoded_dataset.csv', parse_dates=['Date'])
    logger.info(f"Loaded {len(df)} records")
    
    # Convert Date to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Drop exact duplicates (same date, state, county)
    df = df.drop_duplicates(subset=['Date', 'State Code', 'County Code']).copy()
    logger.info(f"After deduplication: {len(df)} records")
    
    # Sort data by location and date
    df = df.sort_values(['State Code', 'County Code', 'Date']).reset_index(drop=True)
    
    # Add lag features (exact prototype logic)
    def add_lags(group):
        group = group.sort_values('Date')
        group['AQI_lag1'] = group['AQI'].shift(1)
        group['AQI_lag3'] = group['AQI'].shift(3)
        group['AQI_lag7'] = group['AQI'].shift(7)
        return group
    
    logger.info("Adding lag features...")
    df = df.groupby(['State Code', 'County Code'], group_keys=False).apply(add_lags)
    
    # Drop rows where lag values are NaN
    df = df.dropna(subset=['AQI_lag1', 'AQI_lag3', 'AQI_lag7']).reset_index(drop=True)
    logger.info(f"After lag features: {len(df)} records")
    
    # Define features (exact prototype)
    feature_cols = [
        'State Code', 'County Code',
        'Defining Parameter_CO', 'Defining Parameter_NO2',
        'Defining Parameter_Ozone', 'Defining Parameter_PM10',
        'Defining Parameter_PM2.5',
        'AQI_lag1', 'AQI_lag3', 'AQI_lag7'
    ]
    target_col = 'AQI'
    
    X = df[feature_cols]
    y = df[target_col]
    
    # Time-based split (exact prototype method)
    df_sorted = df.sort_values('Date').reset_index(drop=True)
    split_idx = int(len(df_sorted) * 0.8)
    
    X_train = df_sorted[feature_cols].iloc[:split_idx]
    y_train = df_sorted[target_col].iloc[:split_idx]
    X_test = df_sorted[feature_cols].iloc[split_idx:]
    y_test = df_sorted[target_col].iloc[split_idx:]
    
    logger.info(f"Training set: {len(X_train)} samples")
    logger.info(f"Test set: {len(X_test)} samples")
    
    # Scale features (exact prototype)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train LightGBM (exact prototype parameters)
    logger.info("Training LightGBM model...")
    model = LGBMRegressor(
        objective='regression',
        random_state=42,
        n_estimators=100,
        learning_rate=0.1,
        max_depth=6,
        num_leaves=31,
        subsample=0.8,
        colsample_bytree=0.8
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
    logger.info("PROTOTYPE Model Performance:")
    logger.info(f"  MSE:  {mse:.2f}")
    logger.info(f"  RMSE: {rmse:.2f}")
    logger.info(f"  MAE:  {mae:.2f}")
    logger.info(f"  R²:   {r2:.4f}")
    logger.info("="*60)
    
    # Save model and scaler
    os.makedirs('models', exist_ok=True)
    
    # Save model
    model_path = 'models/prototype_lightgbm_model.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump({
            'model': model,
            'scaler': scaler,
            'feature_names': feature_cols,
            'metrics': {
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2
            },
            'model_type': 'prototype',
            'version': '20251008_prototype'
        }, f)
    
    # Save scaler separately
    scaler_path = 'models/prototype_pipeline.pkl'
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    
    logger.info(f"Prototype model saved to: {model_path}")
    logger.info(f"Prototype scaler saved to: {scaler_path}")
    
    return {
        'model': model,
        'scaler': scaler,
        'metrics': {'mse': mse, 'rmse': rmse, 'mae': mae, 'r2': r2},
        'feature_names': feature_cols
    }

if __name__ == '__main__':
    try:
        train_prototype_model()
        print("\nPrototype model training completed!")
        print("You can now compare models in the web interface.")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
