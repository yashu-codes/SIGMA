import pandas as pd
import mysql.connector
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yashusql@cse16",
    database="mineguard_nexus"
)

cursor = connection.cursor()

print("MySQL connected successfully!\n")


# =========================
# MINES
# =========================

df = pd.read_csv(BASE_DIR / "mines.csv")
df.columns = [
    "mine_id", "mine_name", "state", "district",
    "latitude", "longitude", "mine_type",
    "annual_production", "workers", "contractors", "status"
]

df["annual_production"] = (
    df["annual_production"].astype(str).str.replace(",", "", regex=False)
)

for _, row in df.iterrows():
    cursor.execute("""
        INSERT IGNORE INTO mines
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, tuple(row))

print("Mines imported:", len(df))


# =========================
# INSPECTIONS
# =========================

df = pd.read_csv(BASE_DIR / "inspection.csv")

for _, row in df.iterrows():
    cursor.execute("""
        INSERT IGNORE INTO inspections
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        row.iloc[0],                         # inspection_id
        row.iloc[1],                         # mine_id
        pd.to_datetime(row.iloc[2], dayfirst=True).strftime("%Y-%m-%d"),
        row.iloc[3],                         # inspection type
        row.iloc[4],                         # inspector
        row.iloc[5],                         # safety observations
        row.iloc[6],                         # violations
        row.iloc[7],                         # severity
        row.iloc[8]                          # score
    ))

print("Inspections imported:", len(df))


# =========================
# VIOLATIONS
# =========================

df = pd.read_csv(BASE_DIR / "Violations.csv")

for _, row in df.iterrows():
    cursor.execute("""
        INSERT IGNORE INTO violations
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        row.iloc[0],
        row.iloc[1],
        row.iloc[2],
        row.iloc[3],
        row.iloc[4],
        row.iloc[5],
        pd.to_datetime(row.iloc[6], dayfirst=True).strftime("%Y-%m-%d"),
        row.iloc[7],
        pd.to_datetime(row.iloc[8], dayfirst=True).strftime("%Y-%m-%d"),
        row.iloc[9]
    ))

print("Violations imported:", len(df))


# =========================
# EQUIPMENT
# =========================

df = pd.read_csv(BASE_DIR / "equipment.csv")

for _, row in df.iterrows():
    cursor.execute("""
        INSERT IGNORE INTO equipment
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        row.iloc[0],                         # equipment_id
        row.iloc[1],                         # mine_id
        row.iloc[2],                         # equipment type
        pd.to_datetime(row.iloc[3], dayfirst=True).strftime("%Y-%m-%d"),
        pd.to_datetime(row.iloc[4], dayfirst=True).strftime("%Y-%m-%d"),
        row.iloc[5],                         # maintenance delay
        row.iloc[6],                         # failure count
        row.iloc[7]                          # condition
    ))

print("Equipment imported:", len(df))


# =========================
# OTHER TABLES
# =========================

def import_normal_table(filename, table):

    df = pd.read_csv(BASE_DIR / filename)

    columns = ", ".join(df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))

    query = f"""
        INSERT IGNORE INTO {table}
        ({columns})
        VALUES ({placeholders})
    """

    for row in df.itertuples(index=False, name=None):
        cursor.execute(query, row)

    print(f"{table} imported:", len(df))


import_normal_table(
    "corrective_actions.csv",
    "corrective_actions"
)

import_normal_table(
    "contractors.csv",
    "contractors"
)

import_normal_table(
    "environment.csv",
    "environment"
)


connection.commit()

cursor.close()
connection.close()

print("\n================================")
print("ALL DATA IMPORTED SUCCESSFULLY!")
print("================================")