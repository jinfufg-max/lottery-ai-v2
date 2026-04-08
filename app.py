from flask import Flask, render_template, request, redirect, session, Response
import sqlite3
import pandas as pd

def get_lottery_data():
    df = pd.read_csv("大樂透.csv")

    numbers = []

    for _, row in df.iterrows():
        nums = row[:6].tolist()  # 前6碼
        numbers.append(nums)

    return numbers
import random
from datetime import datetime

from collections import Counter
import pandas as pd
import os

def get_lottery_data():
    main_numbers, _ = get_full_data()
    return main_numbers
def get_full_data():
    path = r"C:\openclaw\agent_project\大樂透.csv"
    df = pd.read_csv(path)

    main_numbers = []
    special_numbers = []

    for _, row in df.iterrows():
        try:
            main = row.iloc[:6].astype(int).tolist()   # 前6碼
            special = int(row.iloc[6])                # 第7碼

            main_numbers.append(main)
            special_numbers.append(special)
        except:
            continue

    return main_numbers, special_numbers

def special_analysis():

    main_numbers, special_numbers = get_full_data()

    mapping = {}

    # 建立對應
    for main, sp in zip(main_numbers, special_numbers):
        if sp not in mapping:
            mapping[sp] = []

        mapping[sp].extend(main)

    # 統計
    result = {}

    for sp, nums in mapping.items():
        count = Counter(nums)

        # 取前3名
        top = count.most_common(3)

        result[sp] = top

    return result

def special_analysis_with_score():

    main_numbers, special_numbers = get_full_data()

    flat = [n for row in main_numbers for n in row]
    global_count = Counter(flat)

    mapping = {}

    for main, sp in zip(main_numbers, special_numbers):
        if sp not in mapping:
            mapping[sp] = []

        mapping[sp].extend(main)

    result = {}

    for sp, nums in mapping.items():
        count = Counter(nums)

        top_list = []

        for n, c in count.most_common(3):
            base = global_count[n]

            # 👉 偏差（關鍵）
            ratio = round((c / base) * 100, 1)

            top_list.append((n, ratio))

        result[sp] = top_list

    return result

app = Flask(__name__)
app.secret_key = "secret123"

DB_PATH = "lottery_v2.db"


# =========================
# ✅ 功能區（放這裡🔥）
# =========================

def use_points(username, cost):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT points FROM users WHERE username=?", (username,))
    user = c.fetchone()

    if not user:
        conn.close()
        return False, "找不到使用者"

    points = user[0] or 0

    if points < cost:
        conn.close()
        return False, "準提金不足"

    new_points = points - cost
    c.execute("UPDATE users SET points=? WHERE username=?", (new_points, username))
    conn.commit()
    conn.close()

    return True, new_points


# ===== DB =====
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ===== 首頁 =====
from collections import Counter

@app.route('/')
def index():

    data = get_lottery_data()
    flat = [n for row in data for n in row]
    count = Counter(flat)

    # 補齊所有號碼
    for i in range(1, 50):
        if i not in count:
            count[i] = 0

    # 熱門
    sorted_hot = sorted(count.items(), key=lambda x: (-x[1], x[0]))
    hot = [n for n, _ in sorted_hot[:3]]

    # 冷門
    sorted_count = sorted(count.items(), key=lambda x: (x[1], x[0]))
    cold = [n for n, _ in sorted_count[:3]]

    hit_rate = 24
    sample_count = len(data)

    # 區間分析（🔥修正：放進 function 內）
    ranges = {
        "1-10": 0,
        "11-20": 0,
        "21-30": 0,
        "31-40": 0,
        "41-49": 0
    }

    for n in flat:
        if 1 <= n <= 10:
            ranges["1-10"] += 1
        elif 11 <= n <= 20:
            ranges["11-20"] += 1
        elif 21 <= n <= 30:
            ranges["21-30"] += 1
        elif 31 <= n <= 40:
            ranges["31-40"] += 1
        else:
            ranges["41-49"] += 1

    total = sum(ranges.values())

    if total == 0:
        range_percent = {k: "0%" for k in ranges}
    else:
        percent_values = [v / total * 100 for v in ranges.values()]
        rounded = [round(p, 1) for p in percent_values]
        diff = round(100 - sum(rounded), 1)
        rounded[-1] += diff
        range_percent = dict(zip(ranges.keys(), [f"{r}%" for r in rounded]))

    return render_template(
        "index.html",
        hot=hot,
        cold=cold,
        hit_rate=hit_rate,
        sample_count=sample_count,
        range_percent=range_percent
    )    
    # ===== AI推薦 =====
from datetime import datetime
import random

@app.route('/ai')
def ai_page():
    return render_template('ai.html')  # 👉 AI頁面

    # =========================
    # 👤 未登入（免費試用1次）
    # =========================
    if "user" not in session:

        # 第一次使用
        if not session.get("trial_used"):

            session["trial_used"] = True

            numbers = sorted(random.sample(range(1, 50), 6))

            return render_template("ai.html",
                                   numbers=numbers,
                                   points="試用")

        # 第二次 → 強制註冊
        return redirect("/register")

    # =========================
    # 👤 已登入（正常扣點）
    # =========================

    username = session["user"]

    # =========================
    # 💰 扣準提金（10點）
    # =========================
    ok, result = use_points(username, 10)

    if not ok:
        return result   # 顯示「準提金不足」

    # =========================
    # 🤖 AI號碼（先簡單版）
    # =========================
    # 🤖 AI號碼（先簡單版）
        numbers = sorted(random.sample(range(1, 50), 6))

    # =========================
    # 💰 查剩餘準提金
    # =========================
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT points FROM users WHERE username=?", (username,))
    row = c.fetchone()
    points = row[0] if row else 0

    conn.close()

    # =========================
    # 📤 傳給前端
    # =========================
    return render_template("ai.html",
                           numbers=numbers,
                           points=points)


# =========================
# 👤 會員系統
# =========================

def init_user_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        points INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

init_user_db()


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # 👉 不存DB
        session["temp_user"] = {
            "username": username,
            "password": password
        }

        return redirect("/create_order")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()

        conn.close()

        if user:
            session["user"] = username   # 🔥 核心
                                        
            return redirect("/")
        else:
            return "登入失敗"

    return render_template("login.html")


@app.route("/payment-preview")
def payment_preview():
    return redirect("/member")

@app.route("/member")
def member():
    return render_template("member.html")


@app.route("/payment-success", methods=["POST"])
def payment_success():
    return "unused"

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

import hashlib
import urllib.parse

ECPAY_MERCHANT_ID = "3495663"
ECPAY_HASH_KEY = "OqodLmQBAMrhzvUO"
ECPAY_HASH_IV = "iSdTq4wYga4phFG8"

ECPAY_URL = "https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5"


def generate_check_mac_value(params):
    sorted_params = sorted(params.items())
    encoded = urllib.parse.urlencode(sorted_params)

    raw = f"HashKey={ECPAY_HASH_KEY}&{encoded}&HashIV={ECPAY_HASH_IV}"
    raw = urllib.parse.quote_plus(raw).lower()

    return hashlib.sha256(raw.encode()).hexdigest().upper()


from flask import redirect, session

@app.route("/analysis")
def analysis():

    user = "test"

    data = special_analysis_with_score()

    if not data:
        return "資料載入失敗"

    sample_sp = list(data.keys())[0]
    result = data[sample_sp]

    # 補熱門冷門
    main_data = get_lottery_data()
    flat = [n for row in main_data for n in row]
    count = Counter(flat)

    sorted_hot = sorted(count.items(), key=lambda x: (-x[1], x[0]))
    hot = [n for n, _ in sorted_hot[:3]]

    sorted_count = sorted(count.items(), key=lambda x: (x[1], x[0]))
    cold = [n for n, _ in sorted_count[:3]]

    hit_rate = 24
    sample_count = len(main_data)

    return render_template(
        "analysis.html",
        user=user,
        sp=sample_sp,
        result=result,
        hot=hot,
        cold=cold,
        hit_rate=hit_rate,
        sample_count=sample_count
    )
    
@app.route("/create_order")
def create_order():

    trade_no = "ORDER" + datetime.now().strftime("%Y%m%d%H%M%S")

    params = {
        "MerchantID": ECPAY_MERCHANT_ID,
        "MerchantTradeNo": trade_no,
        "MerchantTradeDate": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        "PaymentType": "aio",
        "TotalAmount": 100,
        "TradeDesc": "會員開通",
        "ItemName": "會員服務",
        "ReturnURL": "https://lottery-ai-app.onrender.com/return",
        "ChoosePayment": "ALL",
        "EncryptType": 1,
    }

    params["CheckMacValue"] = generate_check_mac_value(params)

    html = f'<form id="pay" method="post" action="{ECPAY_URL}">'
    for k, v in params.items():
        html += f'<input type="hidden" name="{k}" value="{v}">'
    html += '</form><script>document.getElementById("pay").submit();</script>'

    return html

@app.route("/return", methods=["POST"])
def ecpay_return():

    data = request.form.to_dict()
    print("綠界回傳:", data)

    # ✅ 付款成功
    if data.get("RtnCode") == "1":

        temp_user = session.get("temp_user")

        if not temp_user:
            return "no temp user"

        username = temp_user["username"]
        password = temp_user["password"]

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # 🔥 防重複
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

        if user is None:
            c.execute(
                "INSERT INTO users (username, password, points) VALUES (?, ?, ?)",
                (username, password, 150)
            )
            conn.commit()

        conn.close()

        # 🔥 登入
        session["user"] = username
        # 🎁 送福袋
        session["bags"] = ["大金袋", "大銀袋", "大銀袋"]

        # 🔥 清掉暫存
        session.pop("temp_user", None)

        return "1|OK"

    return "fail"

# =========================
# 🎁 福袋購買頁
# =========================
@app.route("/bag")
def bag_page():

    if "money" not in session:
        session["money"] = 500

    if "bags" not in session:
        session["bags"] = []

    return render_template(
        "bag.html",
        money=session["money"],
        bags=session["bags"]
    )


# =========================
# 🟩 我的福袋頁（修正版）
# =========================
@app.route("/mybag")
def mybag():

    if "bags" not in session:
        session["bags"] = []

    today = datetime.now().strftime("%Y-%m-%d")
    period = f"{today}（最新一期）"

    parsed_bags = []

    # 🔥 修正：加入 index
    for i, b in enumerate(session["bags"]):

        if "已開" in b:
            parts = b.split("_")

            parsed_bags.append({
                "type": parts[1],
                "numbers": parts[2],
                "index": i
            })

        else:
            parsed_bags.append({
                "type": b,
                "numbers": None,
                "index": i
            })

    # 排序（保留你的邏輯）
    order_map = {
        "準提金袋": 1,
        "大金袋": 2,
        "大銀袋": 3,
        "準提銀袋": 4
    }

    parsed_bags.sort(key=lambda x: order_map.get(x["type"], 99))

    return render_template(
        "mybag.html",
        bags=parsed_bags,
        today=today,
        period=period
    )


# =========================
# 🛒 購買福袋
# =========================
@app.route("/buy/<bag_type>")
def buy(bag_type):

    price_map = {
        "silver": 50,
        "gold": 100,
        "pray_silver": 200,
        "pray_gold": 1000,
    }

    bag_map = {
        "silver": ["大銀袋"]*4 + ["大金袋"],
        "gold": ["大銀袋"]*3 + ["大金袋"] + ["準提銀袋"],
        "pray_silver": ["準提銀袋"]*3 + ["大金袋"] + ["大銀袋"],
        "pray_gold": ["準提金袋"]*5
    }

    if "money" not in session:
        session["money"] = 500

    if "bags" not in session:
        session["bags"] = []

    if bag_type not in price_map:
        return "錯誤類型"

    if session["money"] < price_map[bag_type]:
        return "金額不足"

    session["money"] -= price_map[bag_type]
    session["bags"] += bag_map[bag_type]

    return redirect("/bag")


# =========================
# 🎁 開袋
# =========================
@app.route("/open/<int:i>")
def open_bag(i):

    if "bags" not in session:
        return redirect("/mybag")

    bags = session["bags"]

    if i >= len(bags):
        return redirect("/mybag")

    if "已開" in bags[i]:
        return redirect("/mybag")

    nums = sorted(random.sample(range(1, 50), 6))

    bags[i] = f"已開_{bags[i]}_{','.join(map(str, nums))}"

    session["bags"] = bags

    return redirect("/mybag")


# =========================
# 📥 下載全部
# =========================
@app.route("/download_all")
def download_all():

    if "bags" not in session:
        return "沒有資料"

    today = datetime.now().strftime("%Y-%m-%d")
    period = f"{today}（最新一期）"

    lines = []
    lines.append(f"期數：{period}")
    lines.append(f"開獎日：{today}")
    lines.append("")

    for b in session["bags"]:
        if "已開" in b:
            parts = b.split("_")
            lines.append(f"{parts[1]}：{parts[2]}")

    content = "\n".join(lines)

    return Response(
        content,
        mimetype="text/plain",
        headers={
            "Content-Disposition": f"attachment;filename=lottery_{today}.txt"
        }
    )


# =========================
# 💰 儲值
# =========================
@app.route("/topup/<int:amount>")
def topup(amount):

    if "money" not in session:
        session["money"] = 0

    session["money"] += amount

    return redirect("/bag")


@app.route("/topup/custom", methods=["POST"])
def topup_custom():

    amount = request.form.get("amount")

    if not amount:
        return redirect("/bag")

    amount = int(amount)

    if amount <= 0:
        return redirect("/bag")

    if "money" not in session:
        session["money"] = 0

    session["money"] += amount

    return redirect("/bag")


# =========================
# 🎯 對獎
# =========================
@app.route("/check", methods=["GET", "POST"])
def check():

    draw_numbers = [3, 8, 15, 21, 29, 37]
    period = "2026-04-03 第001期"

    inputs = ["", "", "", "", ""]
    results = ["", "", "", "", ""]

    if request.method == "POST":

        for i in range(5):
            raw = request.form.get(f"set{i+1}", "").strip()
            inputs[i] = raw

            if not raw:
                continue

            try:
                nums = [int(x) for x in raw.split(",") if x]

                if len(nums) != 6:
                    results[i] = "❌"
                    continue

                if len(set(nums)) != 6:
                    results[i] = "❌"
                    continue

                if any(n < 1 or n > 49 for n in nums):
                    results[i] = "❌"
                    continue

                match = len(set(nums) & set(draw_numbers))
                results[i] = match

            except:
                results[i] = "❌"

    return render_template(
        "check.html",
        period=period,
        draw=draw_numbers,
        results=results,
        inputs=inputs
    )


# ===== 啟動 =====
if __name__ == "__main__":
    app.run(debug=True)