import os
import sqlite3
import requests
from bs4 import BeautifulSoup
from collections import Counter

DB_PATH = "lottery.db"

# =========================
# 初始化資料庫
# =========================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS lotto (
        date TEXT PRIMARY KEY,
        n1 INTEGER, n2 INTEGER, n3 INTEGER,
        n4 INTEGER, n5 INTEGER, n6 INTEGER
    )
    """)

    conn.commit()
    conn.close()

# =========================
# 抓資料
# =========================
def fetch_data():
    url = "https://www.taiwanlottery.com.tw/lotto/Lotto649/history.aspx"
    res = requests.get(url)
    res.encoding = "utf-8"

    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select(".contents_box02 tr")

    results = []

    for row in rows:
        cols = row.text.split()
        if len(cols) >= 7:
            try:
                date = cols[0]
                nums = list(map(int, cols[1:7]))
                results.append((date, nums))
            except:
                pass

    return results

# =========================
# 存資料
# =========================
def save_data(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for date, nums in data:
        try:
            c.execute("""
            INSERT INTO lotto VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (date, *nums))
        except:
            pass  # 已存在就跳過

    conn.commit()
    conn.close()

# =========================
# 分析
# =========================
def analyze():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT * FROM lotto")
    rows = c.fetchall()

    conn.close()

    numbers = []
    for row in rows:
        numbers.extend(row[1:7])

    counter = Counter(numbers)
    return counter.most_common(10)

# =========================
# 主流程
# =========================
def main():
    print("🚀 AI Agent 啟動")

    init_db()

    print("📥 抓資料...")
    data = fetch_data()

    print("💾 存資料...")
    save_data(data)

    print("📊 分析中...")
    result = analyze()

    print("\n🔥 熱門號碼 Top 10")
    for num, count in result:
        print(f"{num} → {count} 次")

if __name__ == "__main__":
    main()