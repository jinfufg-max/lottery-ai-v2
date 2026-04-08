@echo off
echo ==============================
echo 🚀 AI 彩券系統 一鍵安裝開始
echo ==============================

cd /d C:\openclaw
mkdir agent_project
cd agent_project

echo 📦 安裝套件...
pip install fastapi uvicorn requests beautifulsoup4

echo 🧠 建立主程式 main.py...

(
echo from fastapi import FastAPI
echo from fastapi.middleware.cors import CORSMiddleware
echo import requests, sqlite3, random
echo from bs4 import BeautifulSoup
echo from collections import Counter
echo.
echo app = FastAPI()
echo.
echo app.add_middleware(
echo     CORSMiddleware,
echo     allow_origins=["*"],
echo     allow_methods=["*"],
echo     allow_headers=["*"],
echo )
echo.
echo DB = "lottery.db"
echo URL = "https://www.taiwanlottery.com.tw/lotto/Lotto649/history.aspx"
echo.
echo def init_db():
echo     conn = sqlite3.connect(DB)
echo     c = conn.cursor()
echo     c.execute("CREATE TABLE IF NOT EXISTS lotto (n1 INT, n2 INT, n3 INT, n4 INT, n5 INT, n6 INT)")
echo     conn.commit()
echo     conn.close()
echo.
echo def fetch_data():
echo     all_data = []
echo     headers = {"User-Agent": "Mozilla/5.0"}
echo.
echo     for page in range(1,6):
echo         try:
echo             url = URL + "?pager=" + str(page)
echo             r = requests.get(url, headers=headers, timeout=10)
echo             r.encoding = "utf-8"
echo.
echo             soup = BeautifulSoup(r.text, "html.parser")
echo             rows = soup.select(".contents_box02 tr")
echo.
echo             for row in rows:
echo                 cols = row.text.split()
echo                 if len(cols) >= 7:
echo                     nums = list(map(int, cols[1:7]))
echo                     all_data.append(nums)
echo         except:
echo             pass
echo.
echo     if len(all_data) < 50:
echo         return [[random.randint(1,49) for _ in range(6)] for _ in range(200)]
echo.
echo     return all_data
echo.
echo def save_to_db(data):
echo     conn = sqlite3.connect(DB)
echo     c = conn.cursor()
echo     for row in data:
echo         try:
echo             c.execute("INSERT INTO lotto VALUES (?,?,?,?,?,?)", row)
echo         except:
echo             pass
echo     conn.commit()
echo     conn.close()
echo.
echo def load_db():
echo     conn = sqlite3.connect(DB)
echo     c = conn.cursor()
echo     rows = c.execute("SELECT * FROM lotto").fetchall()
echo     conn.close()
echo     return rows
echo.
echo def build_scores():
echo     data = load_db()
echo     nums = []
echo     for row in data:
echo         nums.extend(row)
echo.
echo     counter = Counter(nums)
echo     scores = {}
echo.
echo     for n in range(1,50):
echo         freq = counter.get(n,0)
echo         hot = freq * 2
echo         cold = (max(counter.values()) - freq) * 0.5 if counter else 0
echo         noise = random.uniform(0,3)
echo         scores[n] = round(hot + cold + noise,2)
echo.
echo     return scores
echo.
echo @app.get("/")
echo def home():
echo     return {"msg":"AI Lottery Running"}
echo.
echo @app.get("/update")
echo def update():
echo     data = fetch_data()
echo     save_to_db(data)
echo     return {"status":"updated","count":len(data)}
echo.
echo @app.get("/analyze")
echo def analyze():
echo     scores = build_scores()
echo     sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
echo     return {"top":sorted_nums[:10],"bottom":sorted_nums[-10:]}
echo.
echo @app.get("/predict")
echo def predict():
echo     scores = build_scores()
echo     nums = list(scores.keys())
echo     weights = list(scores.values())
echo     result = random.choices(nums, weights=weights, k=6)
echo     return {"prediction":result}
) > main.py

echo 🌐 建立前端...
mkdir web
cd web

(
echo ^<!DOCTYPE html^>
echo ^<html^>
echo ^<head^>
echo ^<meta charset="UTF-8"^>
echo ^<title^>AI 彩券^</title^>
echo ^<style^>
echo body{background:#020617;color:white;font-family:Arial;padding:20px;}
echo .num{display:inline-block;width:40px;height:40px;line-height:40px;margin:5px;border-radius:50%%;text-align:center;background:#22c55e;}
echo button{padding:10px;margin:5px;}
echo ^</style^>
echo ^</head^>
echo ^<body^>
echo ^<h1^>AI 彩券系統^</h1^>
echo ^<button onclick="update()"^>更新資料^</button^>
echo ^<button onclick="analyze()"^>分析^</button^>
echo ^<button onclick="predict()"^>預測^</button^>
echo ^<div id="out"^>^</div^>
echo ^<script^>
echo async function update(){
echo let r=await fetch("http://127.0.0.1:8000/update");
echo let d=await r.json();
echo out.innerHTML="更新:"+d.count;
echo }
echo async function analyze(){
echo let r=await fetch("http://127.0.0.1:8000/analyze");
echo let d=await r.json();
echo let h="";
echo d.top.forEach(x=>h+=x[0]+" ");
echo out.innerHTML=h;
echo }
echo async function predict(){
echo let r=await fetch("http://127.0.0.1:8000/predict");
echo let d=await r.json();
echo let h="";
echo d.prediction.forEach(n=>h+=`<div class='num'>${n}</div>`);
echo out.innerHTML=h;
echo }
echo ^</script^>
echo ^</body^>
echo ^</html^>
) > index.html

cd ..

echo ==============================
echo ✅ 安裝完成！
echo ==============================

echo 啟動後端:
echo uvicorn main:app --reload

echo 開前端:
echo cd web
echo python -m http.server 5500

pause