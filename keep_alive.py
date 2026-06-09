import time
import requests

URL = "https://lottery-shop-prod.onrender.com"

while True:
    try:
        r = requests.get(URL)
        print("Ping成功:", r.status_code)
    except:
        print("Ping失敗")

    time.sleep(300)  # 每5分鐘