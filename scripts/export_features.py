# Exports features_train table to data/features_train.csv using the configured DB (SQLite/MySQL)

import os
from pathlib import Path
import pandas as pd
from sqlalchemy import text
from app.db import get_engine

def main():
    Path("data").mkdir(exist_ok=True, parents=True)
    eng = get_engine()
    try:
        with eng.connect() as c:
            df = pd.read_sql(
                text("SELECT * FROM features_train ORDER BY city_id, date"),
                c
            )
    except Exception as e:
        raise SystemExit(f"Error reading features_train: {e}")

    if df.empty:
        raise SystemExit("Error: features_train is empty; run feature builder first (python -m app.features)")

    outp = Path("data/features_train.csv")
    df.to_csv(outp, index=False)
    print(f"exported {len(df)} rows to {outp}")

if __name__ == "__main__":
    main()
