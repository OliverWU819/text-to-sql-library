import pandas as pd
import sqlite3

print("Loading CSV (this may take 30-60 seconds)...")

# Read only 100,000 rows — plenty for our demo
df = pd.read_csv("library.csv", nrows=100000)

print(f"Loaded {len(df)} rows")
print(f"Columns: {list(df.columns)}")
print("\nFirst 3 rows:")
print(df.head(3))

print("\nSaving to SQLite database...")
conn = sqlite3.connect("library.db")
df.to_sql("checkouts", conn, if_exists="replace", index=False)
conn.close()

print("Done! Database saved as library.db")

# Quick sanity check
print("\n--- Sanity check: running a test SQL query ---")
conn = sqlite3.connect("library.db")
result = pd.read_sql("SELECT COUNT(*) as total_rows FROM checkouts", conn)
print(result)
conn.close()