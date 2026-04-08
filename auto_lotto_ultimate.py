import requests
import sqlite3
import random
import time
import traceback
from collections import Counter
import numpy as np

from sklearn.ensemble import RandomForestClassifier

# ======================
# DB 初始化
# ======================
def init_db():
    conn = sqlite3.connect("lottery.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS lotto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        draw_date TEXT,
        n1 INT, n2 INT, n3 INT, n4 INT, n5 INT, n6 INT
    )
    """)
    conn.commit()
    conn.close()

# ======================
# 假資料來源（穩定 fallback）
# ======================
def fetch_data():
    print("🌐 嘗試抓資料...")

    try:
        # 模擬抓不到網路 → fallback
        raise Exception("模擬網路失敗")

    except:
        print("⚠️ 使用本地隨機資料")

        data = []
        for _ in range(500):
            nums = sorted(random.sample(range(1, 50), 6))
            data.append(nums)

        return data

# ======================
# 存DB
# ======================
def save_to_db(data):
    conn = sqlite3.connect("lottery.db")
    c = conn.cursor()

    for row in data:
        c.execute("""
        INSERT INTO lotto (draw_date, n1, n2, n3, n4, n5, n6)
        VALUES (datetime('now'), ?, ?, ?, ?, ?, ?)
        """, tuple(row))

    conn.commit()
    conn.close()

# ======================
# 載入資料
# ======================
def load_data():
    conn = sqlite3.connect("lottery.db")
    c = conn.cursor()

    c.execute("SELECT n1,n2,n3,n4,n5,n6 FROM lotto")
    rows = c.fetchall()

    conn.close()

    return [list(r) for r in rows]

# ======================
# 特徵工程
# ======================
def build_features(data):
    X, y = [], []

    for row in data:
        feature = [
            sum(row),
            max(row),
            min(row),
            np.std(row)
        ]

        for n in row:
            X.append(feature)
            y.append(n)

    return np.array(X), np.array(y)

# ======================
# ML模型
# ======================
def model_ml(X, y):
    model = RandomForestClassifier(n_estimators=50)
    model.fit(X, y)

    test = [[150, 49, 1, 10]]
    pred = model.predict(test)

    return pred.tolist()

# ======================
# DL模型（簡化穩定版）
# ======================
def model_dl(X, y):
    try:
        import tensorflow as tf
        from tensorflow.keras import layers

        model = tf.keras.Sequential([
            layers.Input(shape=(X.shape[1],)),
            layers.Dense(32, activation='relu'),
            layers.Dense(50, activation='softmax')
        ])

        model.compile(loss='sparse_categorical_crossentropy', optimizer='adam')

        model.fit(X, y, epochs=3, verbose=0)

        pred = model.predict(np.array([[150,49,1,10]]), verbose=0)
        return [int(np.argmax(pred))]

    except:
        print("⚠️ DL失敗，略過")
        return []

# ======================
# 熱門分析
# ======================
def hot_analysis(data):
    cnt = Counter()
    for row in data:
        cnt.update(row)
    return cnt.most_common(10)

# ======================
# 冷門分析
# ======================
def cold_analysis(data):
    cnt = Counter()
    for row in data:
        cnt.update(row)

    all_nums = set(range(1, 50))
    unused = list(all_nums - set(cnt.keys()))

    return unused[:10]

# ======================
# 模型融合
# ======================
def ensemble(data):
    X, y = build_features(data)

    ml = model_ml(X, y)
    dl = model_dl(X, y)

    hot = [n for n, _ in hot_analysis(data)[:6]]
    cold = cold_analysis(data)[:6]

    vote = Counter()

    for n in ml + dl + hot + cold:
        vote[n] += 1

    result = [n for n, _ in vote.most_common(6)]

    return result, vote

# ======================
# 回測
# ======================
def backtest(data):
    if len(data) < 10:
        return

    hit = 0
    total = 0

    for i in range(len(data)-1):
        train = data[:i+1]
        real = data[i+1]

        pred, _ = ensemble(train)

        match = len(set(pred) & set(real))
        if match >= 3:
            hit += 1

        total += 1

    print(f"📊 回測命中率: {hit}/{total}")

# ======================
# 主流程
# ======================
def run():
    print("\n🚀 執行開始")

    data = fetch_data()

    if not data:
        print("❌ 無資料")
        return

    save_to_db(data)

    db_data = load_data()
    print("📦 總資料筆數:", len(db_data))

    result, vote = ensemble(db_data)

    print("\n🔥 預測號碼:", result)

    print("\n📊 投票TOP:")
    for k, v in vote.most_common(10):
        print(k, v)

    backtest(db_data)

# ======================
# 排程
# ======================
def scheduler():
    while True:
        try:
            run()
        except:
            traceback.print_exc()

        print("\n⏳ 60秒後再跑（測試）")
        time.sleep(60)

# ======================
# MAIN
# ======================
if __name__ == "__main__":
    init_db()
    scheduler()