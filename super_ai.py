import sqlite3
import random
from collections import Counter

DB_PATH = "lottery.db"

# 建立資料庫
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS lotto (
        date TEXT PRIMARY KEY,
        n1 INT, n2 INT, n3 INT,
        n4 INT, n5 INT, n6 INT
    )
    """)
    conn.commit()
    conn.close()

# 產生假資料（穩定）
def generate_fake_data():
    data = []
    for i in range(50):
        nums = random.sample(range(1,50),6)
        data.append((f"2024{i}", nums))
    return data

# 存資料
def save(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for date, nums in data:
        try:
            c.execute("INSERT INTO lotto VALUES (?, ?, ?, ?, ?, ?, ?)", (date, *nums))
        except:
            pass

    conn.commit()
    conn.close()

# 分析
def analyze():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT n1,n2,n3,n4,n5,n6 FROM lotto")
    rows = c.fetchall()

    nums = []
    for r in rows:
        nums.extend(r)

    counter = Counter(nums)
    result = counter.most_common(10)

    conn.close()
    return result

# 預測
def predict():
    return random.sample(range(1,50),6)

# 主流程（關鍵🔥）
if __name__ == "__main__":
    print("初始化...")
    init_db()

    print("產生資料...")
    data = generate_fake_data()
    save(data)

    print("分析結果：")
    print(analyze())

    print("預測號碼：")
    print(predict())