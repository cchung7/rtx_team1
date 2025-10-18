#!/usr/bin env python3
"""
Data Pipeline for CSV Ingestion,
"""

import numpy as np
import pandas as pd

# Read raw CSV for data ingestion
df = pd.read_csv('daily_aqi_by_county_2024.csv', parse_dates=['Date'], index_col='Date')

# DataFrame (df) to define location features
df['Defining Parameter'].unique()
df['State Name'].unique()
df['county Name'].unique()
df.info()

# Sort rows by descending date
df = df.sort_index(ascending=False)

# Remove unused columns to simplify dataset
df = df.drop(columns=['Defining Site', 'Number of Sites Reporting'])
df['Defining Parameter'].unique()

# One-hot encoding for Defining_Parameter categories
df_encoded = pd.get_dummies(df, columns=["Defining Parameter"], drop_first=False)
# Prefix-match
dummy_cols = [col for col in df_encoded.columns if col.startswith("Defining Parameter_")]

df_encoded[dummy_cols] = df_encoded[dummy_cols].astype(int)

# Select target variable (AQI) to generate lag features from 
cols_to_lag = ["AQI"]

# Generate lag features
for col in cols_to_lag:
    df_encoded[f"{col}_lag7"] = df_encoded[col].shift(7)

# Drop location data 
df_encoded = df_encoded.drop(columns=['State Name', 'county Name', 'Category'])

# Save feature-engineered dataset to CSV for model training
df_encoded.to_csv("encoded_dataset.csv", index=True)