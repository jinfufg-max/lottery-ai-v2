import os

# =========================
# 建立資料夾
# =========================
os.makedirs("web", exist_ok=True)
os.makedirs("data", exist_ok=True)

# =========================
# 建立 API (app.py)
# =========================
with open("app.py", "w", encoding="utf-8") as f:
    f.write("""
from fastapi import FastAPI
import sqlite3
from collections import Counter
import random

app = FastAPI()

DB = "lottery.db"

def get_data():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM lotto")
    rows = c.fetchall()
    conn.close()
    return rows

@app.get("/")
def home():
    return {"msg": "AI API Running"}

@app.get("/analyze")
def analyze():
    rows = get_data()
    nums = []
    for r in rows:
        nums += r[1:7]

    counter = Counter(nums)
    return counter.most_common(10)

@app.get("/predict")
def predict():
    rows = get_data()
    nums = []
    for r in rows:
        nums += r[1:7]

    counter = Counter(nums)
    pool = [n for n,_ in counter.most_common(20)]
    return sorted(random.sample(pool, 6))
""")

# =========================
# 建立前端頁面
# =========================
with open("web/index.html", "w", encoding="utf-8") as f:
    f.write("""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>AI 彩券系統</title>
</head>
<body>
<h1>🎯 AI 彩券分析</h1>

<button onclick="loadAnalyze()">分析</button>
<button onclick="loadPredict()">預測</button>

<pre id="output"></pre>

<script>
async function loadAnalyze() {
    let res = await fetch('/analyze')
    let data = await res.json()
    document.getElementById("output").innerText = JSON.stringify(data, null, 2)
}

async function loadPredict() {
    let res = await fetch('/predict')
    let data = await res.json()
    document.getElementById("output").innerText = JSON.stringify(data, null, 2)
}
</script>
</body>
</html>
""")

# =========================
# 建立啟動器 run.py
# =========================
with open("run.py", "w", encoding="utf-8") as f:
    f.write("""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
""")

# =========================
# requirements
# =========================
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write("fastapi\nuvicorn\n")

print("🔥 部署完成！請執行 run.py")