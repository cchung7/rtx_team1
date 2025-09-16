import sqlite3, pandas as pd, os


os.makedirs("data", exist_ok=True)
con = sqlite3.connect("data/aqi.sqlite")
df = pd.read_sql("SELECT * FROM features_train ORDER BY date", con)
df.to_csv("data/features_train.csv", index=False)
print("exported", len(df), "rows to data/features_train.csv")
