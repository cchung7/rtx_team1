"""
Machine Learning Model for CLAP system
Implements LightGBM for AQI prediction (Stages 7, 8, 9)
"""
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pickle
import os
import logging
from datetime import datetime
import json

# Database functionality removed - using CSV files instead
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AQIPredictor:
    """LightGBM-based AQI prediction model"""
    
    def __init__(self, model_path='models/'):
        self.model_path = model_path
        self.model = None
        self.feature_names = None
        self.model_version = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.metrics = {}
        
        # LightGBM hyperparameters
        self.params = {
            'objective': 'regression',
            'metric': 'mse',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'max_depth': -1,
            'min_data_in_leaf': 20,
            'lambda_l1': 0.1,
            'lambda_l2': 0.1
        }
    
    def log_operation(self, operation, status, duration=None, details=None, error_msg=None):
        """Log model operation to database"""
        try:
            session = db_manager.get_session()
            log_entry = SystemLog(
                timestamp=datetime.utcnow(),
                operation=operation,
                status=status,
                duration_seconds=duration,
                details=details,
                error_message=error_msg
            )
            session.add(log_entry)
            session.commit()
            session.close()
        except Exception as e:
            logger.error(f"Failed to log operation: {str(e)}")
    
    # Stage 7: Train
    def train(self, X_train, y_train, X_val=None, y_val=None, num_rounds=1000):
        """
        Stage 7: Train LightGBM model
        
        Args:
            X_train: Training features
            y_train: Training targets (AQI values)
            X_val: Validation features (optional)
            y_val: Validation targets (optional)
            num_rounds: Number of boosting rounds
            
        Returns:
            Trained model
        """
        import time
        start_time = time.time()
        
        try:
            logger.info("Stage 7: Training LightGBM model")
            
            # Store feature names
            if isinstance(X_train, pd.DataFrame):
                self.feature_names = list(X_train.columns)
                X_train = X_train.values
            
            if isinstance(y_train, pd.Series):
                y_train = y_train.values
            
            # Create LightGBM datasets
            train_data = lgb.Dataset(X_train, label=y_train)
            
            valid_sets = [train_data]
            valid_names = ['train']
            
            if X_val is not None and y_val is not None:
                if isinstance(X_val, pd.DataFrame):
                    X_val = X_val.values
                if isinstance(y_val, pd.Series):
                    y_val = y_val.values
                
                val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
                valid_sets.append(val_data)
                valid_names.append('valid')
            
            # Train model
            logger.info(f"Training with {len(X_train)} samples, {X_train.shape[1]} features")
            
            self.model = lgb.train(
                self.params,
                train_data,
                num_boost_round=num_rounds,
                valid_sets=valid_sets,
                valid_names=valid_names,
                callbacks=[
                    lgb.early_stopping(stopping_rounds=50),
                    lgb.log_evaluation(period=100)
                ]
            )
            
            duration = time.time() - start_time
            logger.info(f"Model training completed in {duration:.2f}s")
            logger.info(f"Best iteration: {self.model.best_iteration}")
            
            self.log_operation('TRAIN', 'SUCCESS', duration,
                             f"Trained LightGBM model with {len(X_train)} samples")
            
            return self.model
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Training failed: {str(e)}")
            self.log_operation('TRAIN', 'ERROR', duration, error_msg=str(e))
            raise
    
    # Stage 8: Evaluate
    def evaluate(self, X_test, y_test):
        """
        Stage 8: Evaluate model performance
        
        Args:
            X_test: Test features
            y_test: Test targets (actual AQI values)
            
        Returns:
            Dictionary of evaluation metrics
        """
        import time
        start_time = time.time()
        
        try:
            logger.info("Stage 8: Evaluating model")
            
            if self.model is None:
                raise ValueError("Model not trained. Call train() first.")
            
            # Make predictions
            if isinstance(X_test, pd.DataFrame):
                X_test = X_test.values
            if isinstance(y_test, pd.Series):
                y_test = y_test.values
            
            y_pred = self.model.predict(X_test)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            self.metrics = {
                'mse': float(mse),
                'rmse': float(rmse),
                'mae': float(mae),
                'r2': float(r2),
                'samples': len(y_test)
            }
            
            duration = time.time() - start_time
            
            logger.info("="*60)
            logger.info("Model Evaluation Metrics:")
            logger.info(f"  MSE (Mean Squared Error): {mse:.2f}")
            logger.info(f"  RMSE (Root Mean Squared Error): {rmse:.2f}")
            logger.info(f"  MAE (Mean Absolute Error): {mae:.2f}")
            logger.info(f"  R² (R-Squared): {r2:.4f}")
            logger.info(f"  Test samples: {len(y_test)}")
            logger.info("="*60)
            
            # Store metrics in database
            self._store_metrics()
            
            self.log_operation('EVALUATE', 'SUCCESS', duration,
                             f"MSE: {mse:.2f}, RMSE: {rmse:.2f}, R²: {r2:.4f}")
            
            return self.metrics
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Evaluation failed: {str(e)}")
            self.log_operation('EVALUATE', 'ERROR', duration, error_msg=str(e))
            raise
    
    def _store_metrics(self):
        """Store evaluation metrics to database"""
        try:
            session = db_manager.get_session()
            
            metric_record = ModelMetrics(
                model_version=self.model_version,
                training_date=datetime.utcnow(),
                mse=self.metrics.get('mse'),
                rmse=self.metrics.get('rmse'),
                r_squared=self.metrics.get('r2'),
                mae=self.metrics.get('mae'),
                samples_count=self.metrics.get('samples'),
                features_used=json.dumps(self.feature_names) if self.feature_names else None,
                hyperparameters=json.dumps(self.params)
            )
            
            session.add(metric_record)
            session.commit()
            session.close()
            
            logger.info("Metrics stored to database")
            
        except Exception as e:
            logger.error(f"Failed to store metrics: {str(e)}")
    
    # Stage 9: Forecast
    def forecast(self, X_forecast, county_name=None, state_name=None, 
                 forecast_date=None, store_predictions=True):
        """
        Stage 9: Generate AQI predictions
        
        Args:
            X_forecast: Features for forecasting
            county_name: County name for prediction
            state_name: State name for prediction
            forecast_date: Date of forecast
            store_predictions: Whether to store predictions in database
            
        Returns:
            Dictionary with predictions and probabilities
        """
        import time
        start_time = time.time()
        
        try:
            logger.info("Stage 9: Forecasting AQI")
            
            if self.model is None:
                raise ValueError("Model not trained. Call train() first.")
            
            # Make prediction
            if isinstance(X_forecast, pd.DataFrame):
                X_forecast = X_forecast.values
            
            predicted_aqi = self.model.predict(X_forecast)
            
            # Calculate category and probabilities
            results = []
            for i, aqi_value in enumerate(predicted_aqi):
                category, probabilities = self._calculate_category_probabilities(aqi_value)
                
                result = {
                    'predicted_aqi': float(aqi_value),
                    'predicted_category': category,
                    'probabilities': probabilities,
                    'county_name': county_name,
                    'state_name': state_name,
                    'forecast_date': forecast_date or datetime.utcnow()
                }
                results.append(result)
            
            duration = time.time() - start_time
            
            logger.info(f"Generated {len(results)} predictions in {duration:.2f}s")
            
            # Store predictions to database
            if store_predictions and county_name and state_name:
                self._store_predictions(results)
            
            self.log_operation('FORECAST', 'SUCCESS', duration,
                             f"Generated {len(results)} predictions")
            
            return results[0] if len(results) == 1 else results
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Forecasting failed: {str(e)}")
            self.log_operation('FORECAST', 'ERROR', duration, error_msg=str(e))
            raise
    
    def _calculate_category_probabilities(self, aqi_value):
        """
        Calculate AQI category and probability distribution
        
        Args:
            aqi_value: Predicted AQI value
            
        Returns:
            Tuple of (category, probabilities_dict)
        """
        # Define AQI categories
        categories = [
            ('Good', 0, 50),
            ('Moderate', 51, 100),
            ('Unhealthy for Sensitive Groups', 101, 150),
            ('Unhealthy', 151, 200),
            ('Very Unhealthy', 201, 300),
            ('Hazardous', 301, 500)
        ]
        
        # Determine primary category
        category = 'Unknown'
        for cat_name, cat_min, cat_max in categories:
            if cat_min <= aqi_value <= cat_max:
                category = cat_name
                break
        
        if aqi_value > 500:
            category = 'Hazardous'
        
        # Calculate probability distribution (simplified using normal distribution)
        # Assume uncertainty of ±15 AQI units (based on RMSE ~13)
        std_dev = 15
        probabilities = {}
        
        for cat_name, cat_min, cat_max in categories:
            # Calculate probability that actual value falls in this category
            from scipy import stats
            lower_z = (cat_min - aqi_value) / std_dev
            upper_z = (cat_max - aqi_value) / std_dev
            prob = stats.norm.cdf(upper_z) - stats.norm.cdf(lower_z)
            probabilities[cat_name] = float(max(0, min(1, prob)))
        
        # Normalize probabilities
        total_prob = sum(probabilities.values())
        if total_prob > 0:
            probabilities = {k: v/total_prob for k, v in probabilities.items()}
        
        return category, probabilities
    
    def _store_predictions(self, predictions):
        """Store predictions to database"""
        try:
            session = db_manager.get_session()
            
            for pred in predictions:
                probs = pred['probabilities']
                
                prediction_record = Prediction(
                    county_name=pred['county_name'],
                    state_name=pred['state_name'],
                    prediction_date=datetime.utcnow(),
                    forecast_date=pred['forecast_date'],
                    predicted_aqi=pred['predicted_aqi'],
                    predicted_category=pred['predicted_category'],
                    prob_good=probs.get('Good', 0),
                    prob_moderate=probs.get('Moderate', 0),
                    prob_unhealthy_sensitive=probs.get('Unhealthy for Sensitive Groups', 0),
                    prob_unhealthy=probs.get('Unhealthy', 0),
                    prob_very_unhealthy=probs.get('Very Unhealthy', 0),
                    prob_hazardous=probs.get('Hazardous', 0)
                )
                
                session.add(prediction_record)
            
            session.commit()
            session.close()
            
            logger.info(f"Stored {len(predictions)} predictions to database")
            
        except Exception as e:
            logger.error(f"Failed to store predictions: {str(e)}")
    
    def save_model(self, filename='lightgbm_model.pkl'):
        """Save trained model to file"""
        try:
            os.makedirs(self.model_path, exist_ok=True)
            filepath = os.path.join(self.model_path, filename)
            
            model_data = {
                'model': self.model,
                'feature_names': self.feature_names,
                'params': self.params,
                'metrics': self.metrics,
                'version': self.model_version
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save model: {str(e)}")
            return False
    
    def load_model(self, filename='lightgbm_model.pkl'):
        """Load trained model from file"""
        try:
            filepath = os.path.join(self.model_path, filename)
            
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.feature_names = model_data.get('feature_names')
            self.params = model_data.get('params', self.params)
            self.metrics = model_data.get('metrics', {})
            self.model_version = model_data.get('version', 'loaded')
            
            logger.info(f"Model loaded from {filepath}")
            logger.info(f"Model version: {self.model_version}")
            
            if self.metrics:
                logger.info(f"Model metrics: MSE={self.metrics.get('mse', 'N/A'):.2f}, "
                          f"R²={self.metrics.get('r2', 'N/A'):.4f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            return False


def train_model_pipeline(data_path='data/', model_path='models/'):
    """
    Complete model training pipeline
    
    Args:
        data_path: Path to data directory
        model_path: Path to save trained model
        
    Returns:
        Trained AQIPredictor instance
    """
    
    logger.info("="*60)
    logger.info("Starting Model Training Pipeline")
    logger.info("="*60)
    
    # Run data pipeline
    pipeline = DataPipeline(data_path=data_path)
    scaled_data = pipeline.run_full_pipeline()
    
    # Prepare training data
    logger.info("\nPreparing training/test split...")
    
    if 'AQI' in scaled_data.columns:
        y = scaled_data['AQI']
        X = scaled_data.drop('AQI', axis=1)
    else:
        raise ValueError("AQI column not found in processed data")
    
    # Time-based split (80% train, 20% test) - like prototype
    # Sort by index (data pipeline already sorted by date)
    split_idx = int(len(X) * 0.8)
    X_train = X.iloc[:split_idx]
    X_test = X.iloc[split_idx:]
    y_train = y.iloc[:split_idx]
    y_test = y.iloc[split_idx:]
    
    logger.info(f"Training set: {len(X_train)} samples")
    logger.info(f"Test set: {len(X_test)} samples")
    
    # Train model
    predictor = AQIPredictor(model_path=model_path)
    predictor.train(X_train, y_train, X_test, y_test)
    
    # Evaluate model
    metrics = predictor.evaluate(X_test, y_test)
    
    # Save model and pipeline
    predictor.save_model()
    pipeline.save_pipeline()
    
    logger.info("="*60)
    logger.info("Model Training Pipeline Completed")
    logger.info("="*60)
    
    return predictor


if __name__ == '__main__':
    # Example usage
    try:
        predictor = train_model_pipeline(data_path='../data/', model_path='../models/')
        print("\n✓ Model training completed successfully")
        print(f"  - MSE: {predictor.metrics['mse']:.2f}")
        print(f"  - RMSE: {predictor.metrics['rmse']:.2f}")
        print(f"  - R²: {predictor.metrics['r2']:.4f}")
    except Exception as e:
        print(f"\n✗ Model training failed: {str(e)}")

