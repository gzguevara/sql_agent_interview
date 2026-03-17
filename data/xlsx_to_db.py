import re
import sqlite3
from pathlib import Path

import pandas as pd

xlsx_path = Path("target-dashboard.xlsx")
db_path = Path("target-dashboard.db")

def clean_name(name: str) -> str:
    name = str(name).strip()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^0-9a-zA-Z_]", "_", name)
    return name or "sheet"

# Read all sheets at once
sheets = pd.read_excel(xlsx_path, sheet_name=None)

with sqlite3.connect(db_path) as conn:
    for sheet_name, df in sheets.items():
        table_name = clean_name(sheet_name)
        df.columns = [clean_name(col) for col in df.columns]
        df.to_sql(table_name, conn, if_exists="replace", index=False)

print(f"Created {db_path.resolve()}")