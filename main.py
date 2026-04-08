from flask import Flask, jsonify
import sqlite3
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)
DB = "lottery.db"

# =====================
# 初始化資料庫
# =====================
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS lotto (
        draw_no TEXT PRIMARY KEY,
        n1 INTEGER, n2 INTEGER, n3 INTEGER,
        n4 INTEGER, n5 INTEGER, n6 INTEGER
    )
    """)
    conn.commit()
    conn.close()

# =====================
# 存資料
# =====================
def save_draw(draw_no, nums):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute("""
        INSERT OR IGNORE INTO lotto VALUES (?,?,?,?,?,?,?)
        """, (draw_no, *nums))
        conn.commit()
    except:
        pass
    conn.close()

# =====================
# 抓資料（單一來源，穩定版）
# =====================
def fetch_once(page):
    url = f"https://www.taiwanlottery.com.tw/lotto/Lotto649/history.aspx?page={page}"
    res = requests.get(url, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.select("table tr")
    count = 0

    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 7:
            continue

        try:
            draw_no = tds[0].text.strip()
            nums = [int(td.text.strip()) for td in tds[1:7]]

            save_draw(draw_no, nums)
            count += 1
        except:
            continue

    return count

# =====================
# 更新資料（只抓新期）
# =====================
@app.route("/update_real")
def update_real():
    init_db()
    total_new = 0

    for page in range(1, 50):  # 自動翻頁
        try:
            c = fetch_once(page)
            if c == 0:
                break
            total_new += c
            time.sleep(1)
        except:
            continue

    return jsonify({
        "status": "ok",
        "new": total_new
    })

# =====================
# 分析
# =====================
@app.route("/analyze")
def analyze():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT n1,n2,n3,n4,n5,n6 FROM lotto")
    rows = c.fetchall()
    conn.close()

    freq = {}

    for row in rows:
        for n in row:
            freq[n] = freq.get(n, 0) + 1

    hot = sorted(freq, key=freq.get, reverse=True)[:10]
    cold = sorted(freq, key=freq.get)[:10]

    return jsonify({
        "hot": hot,
        "cold": cold,
        "total": len(rows)
    })

# =====================
# 預測（簡單版）
# =====================
@app.route("/predict")
def predict():
    import random
    nums = sorted(random.sample(range(1, 50), 6))
    return jsonify({"prediction": nums})

# =====================
# 啟動
# =====================
if __name__ == "__main__":
    app.run(debug=True)