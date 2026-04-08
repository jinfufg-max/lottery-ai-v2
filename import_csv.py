import sqlite3
import csv
import os

DB_NAME = "lottery.db"

# =========================
# 建立資料表
# =========================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS lotto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        n1 INT, n2 INT, n3 INT, n4 INT, n5 INT, n6 INT,
        special INT
    )
    """)

    conn.commit()
    conn.close()


# =========================
# 匯入 CSV
# =========================
def import_csv():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    files = [f for f in os.listdir() if f.endswith(".csv")]

    print(f"找到 {len(files)} 個CSV檔案")

    total = 0

    for file in files:
        print(f"匯入：{file}")

        with open(file, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)

            for row in reader:
                try:
                    # 👉 抓最後7個數字（6碼+特別號）
                    nums = [int(x) for x in row if x.isdigit()]

                    if len(nums) >= 7:
                        n1, n2, n3, n4, n5, n6, special = nums[-7:]

                        c.execute("""
                        INSERT INTO lotto (n1,n2,n3,n4,n5,n6,special)
                        VALUES (?,?,?,?,?,?,?)
                        """, (n1, n2, n3, n4, n5, n6, special))

                        total += 1

                except:
                    continue

    conn.commit()
    conn.close()

    print(f"✅ 匯入完成，共 {total} 筆資料")


# =========================
# 主程式
# =========================
if __name__ == "__main__":
    init_db()
    import_csv()