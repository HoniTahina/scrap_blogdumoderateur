import sqlite3
import csv

conn = sqlite3.connect("bourse.db")
cur = conn.cursor()

print("=== TOP 5 HAUSSES ===")
cur.execute("SELECT libelle, variation, cours FROM actions ORDER BY variation DESC LIMIT 5")
for row in cur.fetchall():
    print(row)

print("\n=== TOP 5 PLUS FAIBLES VARIATIONS ===")
cur.execute("SELECT libelle, variation, cours FROM actions ORDER BY variation ASC LIMIT 5")
for row in cur.fetchall():
    print(row)

print("\n=== VOLUME ANORMAL (> 2x mediane) ===")
cur.execute("""
    WITH ordered AS (
        SELECT volume,
               ROW_NUMBER() OVER (ORDER BY volume) AS rn,
               COUNT(*) OVER () AS total
        FROM actions
    ),
    mediane_calc AS (
        SELECT AVG(volume) AS mediane
        FROM ordered
        WHERE rn IN ((total + 1) / 2, (total + 2) / 2)
    )
    SELECT libelle, volume, cours
    FROM actions, mediane_calc
    WHERE volume > mediane_calc.mediane * 2
    ORDER BY volume DESC
""")
for row in cur.fetchall():
    print(row)

# Export CSV
cur.execute("SELECT * FROM actions ORDER BY variation DESC")
rows = cur.fetchall()
cols = [d[0] for d in cur.description]
with open("analyse_bourse.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(cols)
    w.writerows(rows)

print(f"\n{len(rows)} lignes exportees dans analyse_bourse.csv")
conn.close()