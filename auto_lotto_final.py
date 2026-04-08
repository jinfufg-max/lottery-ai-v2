import sqlite3
import requests
import time
import os
import random
from bs4 import BeautifulSoup
from collections import Counter
import numpy as np

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Input

DB = "lottery.db"

# =========================
# 安全請求（防爆）
# =========================
def safe_request(url, headers):
    for i in range(3):
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                return r
        except:
            time.sleep(2)
    return None

# =========================
# 初始化 DB
# =========================
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS lotto (
        draw_no TEXT PRIMARY KEY,
        draw_date TEXT,
        n1 INTEGER, n2 INTEGER, n3 INTEGER,
        n4 INTEGER, n5 INTEGER, n6 INTEGER
    )
    """)

    conn.commit()
    conn.close()

# =========================
# 資料清洗
# =========================
def validate_data(rows):
    valid = []

    for r in rows:
        nums = r[2:]

        if not all(1 <= n <= 49 for n in nums):
            continue

        if len(set(nums)) != 6:
            continue

        valid.append(r)

    return valid

# =========================
# 多來源抓資料
# =========================
def fetch_latest():
    print("🌐 抓資料中...")

    headers = {"User-Agent": "Mozilla/5.0"}

    urls = [
        "https://www.lotto-8.com/taiwan/lotto649/history",
        "https://lottohub.com/taiwan/lotto649/history"
    ]

    for url in urls:
        r = safe_request(url, headers)
        if not r:
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select("table tr")

        data = []

        for row in rows:
            cols = [c.text.strip() for c in row.find_all("td")]

            if len(cols) >= 8 and cols[0].isdigit():
                try:
                    draw_no = cols[0]
                    draw_date = cols[1]
                    nums = list(map(int, cols[2:8]))

                    data.append((draw_no, draw_date, *nums))
                except:
                    continue

        data = validate_data(data)

        if data:
            print(f"✅ 成功抓 {len(data)} 筆")
            save_to_db(data[:50])
            return

    print("❌ 抓資料失敗 → 使用本地資料")

# =========================
# 存DB
# =========================
def save_to_db(rows):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    count = 0

    for r in rows:
        c.execute("""
        INSERT OR IGNORE INTO lotto
        VALUES (?,?,?,?,?,?,?,?)
        """, r)
        count += 1

    conn.commit()
    conn.close()

    print(f"💾 新增 {count} 筆")

# =========================
# 讀資料
# =========================
def load_data():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT n1,n2,n3,n4,n5,n6 FROM lotto ORDER BY draw_no")
    rows = c.fetchall()

    conn.close()
    return rows

# =========================
# 建資料
# =========================
def build_dataset(data, window=10):
    X, Y = [], []

    for i in range(window, len(data)):
        X.append(data[i-window:i])

        target = [0]*49
        for n in data[i]:
            target[n-1] = 1

        Y.append(target)

    return np.array(X), np.array(Y)

# =========================
# 建模型
# =========================
def build_model(shape):
    model = Sequential()
    model.add(Input(shape=shape))
    model.add(LSTM(64))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(49, activation='sigmoid'))

    model.compile(loss='binary_crossentropy', optimizer='adam')
    return model

# =========================
# LSTM預測
# =========================
def lstm_predict(data):
    X, Y = build_dataset(data)

    if os.path.exists("model.h5"):
        print("📦 載入模型")
        model = load_model("model.h5")
    else:
        print("🧠 訓練模型")
        model = build_model((X.shape[1], X.shape[2]))
        model.fit(X, Y, epochs=5, batch_size=16, verbose=0)
        model.save("model.h5")

    recent = np.array([data[-10:]])
    probs = model.predict(recent)[0]

    ranked = sorted([(i+1,p) for i,p in enumerate(probs)],
                    key=lambda x: x[1],
                    reverse=True)

    return [n for n,_ in ranked[:6]]

# =========================
# 模型融合
# =========================
def ensemble_predict(data):
    stat_counter = Counter()
    for row in data:
        stat_counter.update(row)

    stat_top = [k for k,_ in stat_counter.most_common(20)]
    lstm_res = lstm_predict(data)

    pool = []
    pool += stat_top * 2
    pool += lstm_res * 3

    vote = Counter(pool)

    result = [k for k,_ in vote.most_common(10)]
    final = sorted(random.sample(result, 6))

    return final, vote

# =========================
# 主流程
# =========================
def run():
    fetch_latest()

    data = load_data()

    if len(data) < 50:
        print("❌ 資料不足")
        return

    result, vote = ensemble_predict(data)

    print("\n🎯 最終推薦號碼:")
    print(result)

    print("\n📊 投票 TOP10:")
    for k,v in vote.most_common(10):
        print(k, v)

# =========================
# 安全執行
# =========================
def safe_run():
    try:
        run()
    except Exception as e:
        print("❌ 錯誤:", e)

# =========================
# 主程式
# =========================
if __name__ == "__main__":
    init_db()

    for i in range(3):
        print(f"\n🔁 第 {i+1} 次執行")
        safe_run()