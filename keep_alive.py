import time
import requests

URL = "https://lottery-ai-app.onrender.com"

while True:
    try:
        r = requests.get(URL)
        print("Ping成功:", r.status_code)
    except:
        print("Ping失敗")

    time.sleep(180)  # 每3分鐘