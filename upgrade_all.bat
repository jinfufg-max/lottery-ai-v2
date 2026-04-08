@echo off
chcp 65001 > nul

echo =============================
echo 🚀 AI 彩券系統 升級中...
echo =============================

cd /d %~dp0

echo 📦 安裝套件...
pip install fastapi uvicorn numpy requests

echo 📁 建立資料夾...
mkdir data 2>nul
mkdir web 2>nul

echo 🧠 建立後端...

(
echo from fastapi import FastAPI
echo import random, json, os
echo import numpy as np
echo.
echo app = FastAPI()
echo DATA_FILE = "data/lottery.json"
echo.
echo def generate_data(n=1000):
echo     data = []
echo     for _ in range(n):
echo         draw = sorted(random.sample(range(1,50),6))
echo         data.append(draw)
echo     return data
echo.
echo def load_data():
echo     if not os.path.exists(DATA_FILE):
echo         data = generate_data()
echo         json.dump(data, open(DATA_FILE,"w"))
echo     return json.load(open(DATA_FILE))
echo.
echo @app.get("/")
echo def home():
echo     return {"msg":"AI Lottery Running"}
echo.
echo @app.get("/analyze")
echo def analyze():
echo     data = load_data()
echo     flat = [n for d in data for n in d]
echo.
echo     freq = {}
echo     for n in flat:
echo         freq[n] = freq.get(n,0)+1
echo.
echo     sorted_nums = sorted(freq.items(), key=lambda x:x[1], reverse=True)
echo.
echo     hot = [n for n,_ in sorted_nums[:10]]
echo     cold = [n for n,_ in sorted_nums[-10:]]
echo.
echo     return {"hot":hot, "cold":cold}
echo.
echo @app.get("/predict")
echo def predict():
echo     data = load_data()
echo     flat = [n for d in data for n in d]
echo.
echo     freq = {}
echo     for n in flat:
echo         freq[n] = freq.get(n,0)+1
echo.
echo     nums = list(range(1,50))
echo     weights = np.array([freq.get(n,1) for n in nums])
echo     weights = weights / weights.sum()
echo.
echo     pick = np.random.choice(nums, size=6, replace=False, p=weights)
echo.
echo     return {"prediction": sorted(pick.tolist())}
) > main.py

echo 🌐 建立前端...

(
echo ^<!DOCTYPE html^>
echo ^<html^>
echo ^<head^>
echo ^<meta charset="utf-8"^>
echo ^<title^>AI 彩券系統^</title^>
echo ^<style^>
echo body {font-family:Arial; background:#f5f7fa; text-align:center;}
echo .box {background:white; padding:20px; margin:20px auto; width:600px; border-radius:10px;}
echo .num {display:inline-block; margin:5px; padding:10px 15px; background:#3498db; color:white; border-radius:50%%;}
echo .hot {background:#e74c3c;}
echo .cold {background:#95a5a6;}
echo button {padding:10px 20px; margin:10px;}
echo ^</style^>
echo ^</head^>
echo ^<body^>
echo ^<h1^>🎯 AI 彩券分析系統^</h1^>
echo ^<button onclick="analyze()"^>分析^</button^>
echo ^<button onclick="predict()"^>預測^</button^>
echo ^<div id="result" class="box"^>等待操作...^</div^>
echo.
echo ^<script^>
echo async function analyze() {
echo let res = await fetch("http://127.0.0.1:8000/analyze");
echo let data = await res.json();
echo.
echo let html = "<h2>🔥 熱門</h2>";
echo data.hot.forEach(n => html += `<span class='num hot'>${n}</span>`);
echo.
echo html += "<h2>❄️ 冷門</h2>";
echo data.cold.forEach(n => html += `<span class='num cold'>${n}</span>`);
echo.
echo document.getElementById("result").innerHTML = html;
echo }
echo.
echo async function predict() {
echo let res = await fetch("http://127.0.0.1:8000/predict");
echo let data = await res.json();
echo.
echo let html = "<h2>🤖 AI 預測</h2>";
echo data.prediction.forEach(n => html += `<span class='num'>${n}</span>`);
echo.
echo document.getElementById("result").innerHTML = html;
echo }
echo ^</script^>
echo ^</body^>
echo ^</html^>
) > web/index.html

echo.
echo =============================
echo ✅ 升級完成！
echo =============================
echo.
echo 👉 啟動後端：
echo uvicorn main:app --reload
echo.
echo 👉 開啟：
echo web/index.html
echo.

pause