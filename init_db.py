import sqlite3

conn = sqlite3.connect("lottery.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS lotto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    draw_no TEXT UNIQUE,
    draw_date TEXT,
    n1 INTEGER,
    n2 INTEGER,
    n3 INTEGER,
    n4 INTEGER,
    n5 INTEGER,
    n6 INTEGER
)
""")

conn.commit()
conn.close()

print("✅ 資料庫建立完成")