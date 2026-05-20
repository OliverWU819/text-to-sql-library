import sqlite3
import pandas as pd

conn = sqlite3.connect("library.db")

# Change this SQL to whatever you want to check
my_sql = """
SELECT Creator, SUM(Checkouts) AS Total
FROM checkouts
WHERE Creator IS NOT NULL AND Creator != ''
GROUP BY Creator
ORDER BY Total DESC
LIMIT 10
"""

result = pd.read_sql(my_sql, conn)
print(result)
conn.close()