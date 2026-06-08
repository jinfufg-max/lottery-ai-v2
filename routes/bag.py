import sqlite3
import random

from services.bag_utils import (
    build_removed_numbers,
    get_bag_name,
    get_bag_price,
)

from datetime import datetime, timedelta

from services.bag_rules import can_change_bag_status
from services.bags.big_gold import build_gold_scores
from services.bags.core import (
    get_market_data,
    build_sorted_scores,
)

from flask import *

from services.db import *
from ai.engine import *


def get_target_draw_date():

    now = datetime.utcnow() + timedelta(hours=8)

    today = now.date()

    weekday = now.weekday()  # 二=1 五=4

    current_time = now.strftime("%H:%M")
    # =====================
    # 今天是開獎日
    # =====================
    if weekday in [1, 4]:

        # 19:00 前 → 算今天
        if current_time < "19:00":
            return today.strftime("%Y-%m-%d")
    # =====================
    # 否則找下一個 二 / 五
    # =====================
    next_day = today + timedelta(days=1)

    while next_day.weekday() not in [1, 4]:
        next_day += timedelta(days=1)

    return next_day.strftime("%Y-%m-%d")


bag_bp = Blueprint("bag_bp", __name__)


def generate_numbers(bag_type):

    all_numbers = list(range(1, 50))

    last_draw, history_rows = get_market_data()

    removed_numbers = build_removed_numbers(last_draw, bag_type)

    print("排除號碼:", removed_numbers)

    available_numbers = [n for n in all_numbers if n not in removed_numbers]

    # 🔹 大銀袋
    if bag_type == "silver":

        # =====================
        # 去除上期連莊號
        # =====================

        removed_numbers = set(last_draw)

        # =====================
        # 海流最差尾數
        # =====================

        tail_scores = {}

        for i in range(10):

            tail_scores[i] = 0

        for row in history_rows:

            nums = row["numbers"].split(",")

            nums = list(map(int, nums[:6]))

            for n in nums:

                tail = n % 10

                tail_scores[tail] += 1

        # 最差2個尾數
        worst_tails = sorted(tail_scores.items(), key=lambda x: x[1])[:2]

        worst_tails = [x[0] for x in worst_tails]

        # 加入尾數排除
        for n in all_numbers:

            if n % 10 in worst_tails:

                removed_numbers.add(n)

        # =====================
        # 建立大銀袋球池
        # =====================

        silver_pool = [n for n in available_numbers if n not in removed_numbers]

        # =====================
        # 大銀袋自由亂數
        # =====================

        numbers = sorted(random.sample(silver_pool, 6))

        # 🔸 大金袋
    elif bag_type == "gold":

        scores = build_gold_scores(last_draw, history_rows)

        sorted_scores = build_sorted_scores(scores)

        # 海流前18顆
        flow_pool = [n for n, s in sorted_scores[:18]]

        # 去除上期連莊號
        gold_pool = [n for n in flow_pool if n not in last_draw]

        # 防止球池不足
        if len(gold_pool) < 6:

            gold_pool = flow_pool

        # 大金池亂數選號
        numbers = sorted(random.sample(gold_pool, 6))

        # ✨ 準提銀袋
    elif bag_type == "pray_silver":

        scores = build_gold_scores(last_draw, history_rows)

        sorted_scores = build_sorted_scores(scores)

        # =====================
        # 扣除連莊號
        # =====================

        removed_numbers = set(last_draw)

        # =====================
        # 扣除大金袋前6名
        # =====================

        top_6 = [n for n, s in sorted_scores[:6]]

        removed_numbers.update(top_6)

        # =====================
        # 扣除大金袋後6名
        # =====================

        bottom_6 = [n for n, s in sorted_scores[-6:]]

        removed_numbers.update(bottom_6)

        # =====================
        # 建立準提銀袋球池
        # =====================

        pray_silver_pool = [n for n in all_numbers if n not in removed_numbers]

        # =====================
        # 準提銀袋亂數出號
        # =====================

        numbers = sorted(random.sample(pray_silver_pool, 6))

        # 🔥 準提金袋
    elif bag_type == "pray_gold":

        scores = build_gold_scores(last_draw, history_rows)

        sorted_scores = build_sorted_scores(scores)

        # =====================
        # 海流高壓縮核心區
        # =====================

        core_pool = [n for n, s in sorted_scores[:8]]

        # =====================
        # 大金袋次海流區
        # =====================

        sub_pool = [n for n, s in sorted_scores[6:12]]

        # 合併球池
        pray_gold_pool = list(set(core_pool + sub_pool))

        # =====================
        # 去除上期連莊
        # =====================

        pray_gold_pool = [n for n in pray_gold_pool if n not in last_draw]

        # =====================
        # 最低球池保護
        # =====================

        if len(pray_gold_pool) < 18:

            backup_pool = [n for n, s in sorted_scores[:18]]

            for n in backup_pool:

                if n not in pray_gold_pool:

                    pray_gold_pool.append(n)

                if len(pray_gold_pool) >= 18:

                    break

        # =====================
        # 準提金袋亂數出號
        # =====================

        numbers = sorted(random.sample(pray_gold_pool, 6))

    else:

        numbers = random.sample(available_numbers, 6)

    numbers = sorted(numbers)

    return numbers


# =========================
# 🎁 福袋購買頁
# =========================
@bag_bp.route("/bag")
def bag_page():

    # 🔐 未登入擋掉
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_shop_db()
    print(conn)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 🎯 1. 抓「未開福袋（分組）」
    c.execute(
        """
        SELECT bag_type, COUNT(*) as total
        FROM user_bags
        WHERE user_id=? AND is_opened=0
        GROUP BY bag_type
        """,
        (user_id,),
    )
    groups = c.fetchall()

    # 🔥 補齊所有袋型（關鍵） ← 一定要在 function 裡
    bag_types = ["silver", "gold", "pray_silver", "pray_gold"]

    groups_dict = {g["bag_type"]: g["total"] for g in groups}

    fixed_groups = []
    for t in bag_types:
        fixed_groups.append({"bag_type": t, "total": groups_dict.get(t, 0)})

    groups = fixed_groups

    # 💰 3. 抓餘額
    c.execute("SELECT points FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    balance = user["points"] if user else 0

    # ===== 本週命中統計 =====
    start = datetime.now() - timedelta(days=7)
    end = datetime.now()

    c.execute(
        """
        SELECT hit_count
        FROM user_bags
        WHERE status='settled'
        AND date(settled_at) BETWEEN ? AND ?
        """,
        (
            start.strftime("%Y-%m-%d"),
            end.strftime("%Y-%m-%d"),
        ),
    )

    rows = c.fetchall()

    hit3 = sum(1 for r in rows if r["hit_count"] == 3)
    hit4 = sum(1 for r in rows if r["hit_count"] == 4)

    conn.close()

    return render_template(
        "bag.html",
        groups=groups,
        money=balance,
        hit3=hit3,
        hit4=hit4,
    )


@bag_bp.route("/buy/<bag_type>", methods=["POST"])
def buy(bag_type):

    # 🔒 登入檢查
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    # 🎁 福袋內容（唯一正確來源）

    # ❗ 防呆（避免錯誤 bag_type）
    valid_types = ["silver", "gold", "pray_silver", "pray_gold"]

    if bag_type not in valid_types:
        return "福袋類型錯誤"

    # 💰 價格
    price = get_bag_price(bag_type)

    # 🗄 DB
    conn = get_shop_db()
    c = conn.cursor()

    # 💸 扣點（防負數）
    c.execute(
        """
        UPDATE users
        SET points = points - ?
        WHERE id = ? AND points >= ?
    """,
        (price, user_id, price),
    )

    if c.rowcount == 0:
        conn.close()
        return "餘額不足"

    # 🎁 建立未開封福袋
    print("現在買的袋子:", bag_type)

    for _ in range(1):
        c.execute(
            """
            INSERT INTO user_bags
            (user_id, bag_type, numbers, is_opened, created_at)
            VALUES (?, ?, NULL, 0, ?)
            """,
            (
                user_id,
                bag_type,
                (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )

    try:

        conn.commit()

        conn.close()

        return redirect("/bag")

    except Exception as e:

        conn.rollback()

        print("⚠️ 購買福袋失敗")
        print(e)

        conn.close()

        return "購買失敗"


@bag_bp.route("/topup/<int:amount>", methods=["POST"])
def topup(amount):

    if "user_id" not in session:
        return redirect("/login")

    valid_amounts = [150, 300, 500, 800]

    if amount not in valid_amounts:
        return "金額錯誤"

    conn = get_shop_db()
    c = conn.cursor()

    user_id = session["user_id"]

    order_no = (
        "TOP"
        + (datetime.utcnow() + timedelta(hours=8)).strftime("%m%d%H%M%S")
        + str(random.randint(1000, 9999))
    )

    now = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

    # 建立 orders

    c.execute(
        """
        SELECT
            name,
            phone,
            address,
            email
        FROM users
        WHERE id=?
        """,
        (user_id,),
    )

    user_info = c.fetchone()

    print("======== TOPUP DEBUG ========")
    print("user_id =", user_id)
    print("session =", dict(session))
    print("user_info =", user_info)

    name = user_info["name"] if user_info else ""
    phone = user_info["phone"] if user_info else ""
    address = user_info["address"] if user_info else ""
    email = user_info["email"] if user_info else ""

    c.execute(
        """
        INSERT INTO orders (
            user_id,
            username,
            total,
            payment_method,
            status,
            created_at,
            order_no,
            order_type,
            name,
            phone,
            address,
            email
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            session["user"],
            amount,
            "cash",
            "pending",
            now,
            order_no,
            "topup",
            name,
            phone,
            address,
            email,
        ),
    )

    order_id = c.lastrowid

    # 建立 transaction
    c.execute(
        """
        INSERT INTO transactions (
            user_id,
            type,
            status,
            amount,
            balance_before,
            balance_after,
            source_type,
            source_id,
            note,
            created_at,
            transaction_no,
            order_no,
            action_type,
            metadata_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            "topup",
            "pending",
            amount,
            0,
            0,
            "topup_order",
            order_id,
            "準提金儲值",
            now,
            "TXN" + order_no,
            order_no,
            "cash_payment",
            "{}",
        ),
    )

    conn.commit()
    conn.close()

    return redirect(f"/ecpay_checkout/{order_no}")


def do_open_bag(bag_id, user_id):

    conn = get_shop_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute(
        """
        SELECT *
        FROM user_bags
        WHERE id=? AND user_id=?
        """,
        (bag_id, user_id),
    )

    bag = c.fetchone()

    if not bag:
        conn.close()
        return False

    if bag["is_opened"] == 1:
        conn.close()
        return False

    bag_numbers = generate_numbers(bag["bag_type"])

    target_draw_date = get_target_draw_date()

    numbers_text = ",".join(map(str, bag_numbers))

    c.execute(
        """
        UPDATE user_bags
        SET numbers=?,
            is_opened=1,
            opened_at=?,
            target_draw_date=?,
            status='opened'
        WHERE id=?
        """,
        (
            numbers_text,
            (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
            target_draw_date,
            bag_id,
        ),
    )

    conn.commit()
    conn.close()

    return True


@bag_bp.route("/open/<int:bag_id>", methods=["POST"])
def open_bag(bag_id):

    if "user_id" not in session:
        return "login required", 403

    ok = do_open_bag(bag_id, session["user_id"])

    if not ok:
        return "open failed", 400

    return "success"


@bag_bp.route("/open_all/<bag_type>", methods=["POST"])
def open_all_bags(bag_type):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_shop_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute(
        """
        SELECT id
        FROM user_bags
        WHERE user_id=?
        AND bag_type=?
        AND status='pending'
        """,
        (
            session["user_id"],
            bag_type,
        ),
    )

    bags = c.fetchall()

    conn.close()

    for bag in bags:

        do_open_bag(bag["id"], session["user_id"])

    return redirect("/mybag")


# =====開獎後兌獎 =====


def settle_lottery(draw_date, draw_numbers):

    conn = get_shop_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute(
        """
        SELECT id, numbers
        FROM user_bags
        WHERE target_draw_date=?
        AND status='opened'
    """,
        (draw_date,),
    )
    bags = c.fetchall()

    for b in bags:
        bag_id = b["id"]
        user_numbers = list(map(int, b["numbers"].split(",")))

        hit_count = len(set(user_numbers) & set(draw_numbers))
        old_status = "opened"
        new_status = "settled"

        if not can_change_bag_status(old_status, new_status):
            continue

        is_3_hit = 1 if hit_count == 3 else 0
        is_4_hit = 1 if hit_count == 4 else 0
        is_5_hit = 1 if hit_count >= 5 else 0
        is_all_dead = 1 if hit_count == 0 else 0

        c.execute(
            """
            UPDATE user_bags
            SET hit_count=?,
                status='settled',
                settled_at=?,
                is_3_hit=?,
                is_4_hit=?,
                is_5_hit=?,
                is_all_dead=?
            WHERE id=?
            """,
            (
                hit_count,
                (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
                is_3_hit,
                is_4_hit,
                is_5_hit,
                is_all_dead,
                bag_id,
            ),
        )

    # =====================
    # 🧹 清除舊期資料
    # 只保留最新一期
    # pending 不刪
    # =====================

    c.execute(
        """
        DELETE FROM user_bags
        WHERE target_draw_date < ?
        AND status != 'pending'
        """,
        (draw_date,),
    )

    deleted = c.rowcount

    print(f"🧹 已清除 {deleted} 筆舊期福袋")

    conn.commit()
    conn.close()


@bag_bp.route("/delete_bag/<int:bag_id>", methods=["POST"])
def delete_bag(bag_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_shop_db()
    c = conn.cursor()

    c.execute(
        """
        DELETE FROM user_bags
        WHERE id=? AND user_id=?
        """,
        (bag_id, session["user_id"]),
    )

    conn.commit()
    conn.close()

    return redirect("/mybag")


@bag_bp.route("/mybag")
def mybag():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_shop_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 🔥 撈資料
    c.execute(
        """
        SELECT
            id,
            bag_type,
            numbers,
            is_opened,
            created_at,
            opened_at,
            target_draw_date,
            hit_count,
            status
        FROM user_bags
        WHERE user_id=?
        ORDER BY is_opened ASC, id DESC
        """,
        (session["user_id"],),
    )

    rows = c.fetchall()
    # 🎯 最新開獎資料
    conn_lottery = get_lottery_db()
    c_lottery = conn_lottery.cursor()

    c_lottery.execute("""
        SELECT draw_date, numbers
        FROM lottery_results
        ORDER BY draw_date DESC
        LIMIT 1
    """)

    latest = c_lottery.fetchone()

    if latest:
        last_draw_date = latest[0]
        latest_numbers = latest[1]
    else:
        last_draw_date = "尚未開獎"
        latest_numbers = "無資料"

    try:
        base_date = datetime.strptime(last_draw_date, "%Y-%m-%d")

        if base_date.weekday() == 1:
            next_draw_date = (base_date + timedelta(days=3)).strftime("%Y-%m-%d")

        else:
            next_draw_date = (base_date + timedelta(days=4)).strftime("%Y-%m-%d")

    except:
        next_draw_date = "等待更新"

    conn_lottery.close()

    pending_bags = []
    opened_bags = []
    settled_bags = []

    for r in rows:

        bag = {
            "id": r["id"],
            "type": get_bag_name(r["bag_type"]),
            "numbers": r["numbers"],
            "created_at": r["created_at"],
            "opened_at": r["opened_at"],
            "target_draw_date": r["target_draw_date"],
            "hit_count": r["hit_count"],
            "status": r["status"],
        }

        status = r["status"]

        if status == "pending":
            pending_bags.append(bag)

        elif status == "opened":
            opened_bags.append(bag)

        elif status == "settled":
            settled_bags.append(bag)

    conn.close()

    bags = pending_bags + opened_bags + settled_bags

    return render_template(
        "mybag.html",
        bags=bags,
        pending_bags=pending_bags,
        opened_bags=opened_bags,
        settled_bags=settled_bags,
        last_draw_date=last_draw_date,
        latest_numbers=latest_numbers,
        next_draw_date=next_draw_date,
    )


@bag_bp.route("/download_bags")
def download_bags():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_shop_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute(
        """
        SELECT bag_type, numbers, created_at, is_opened
        FROM user_bags
        WHERE user_id=?
        ORDER BY created_at DESC
        """,
        (session["user_id"],),
    )

    rows = c.fetchall()
    conn.close()

    if not rows:
        return "沒有資料"

    content = "我的福袋紀錄\n"
    content += "=========================\n\n"

    for r in rows:

        status = "已開封" if r["is_opened"] else "未開封"

        name = get_bag_name(r["bag_type"])

        numbers = r["numbers"] if r["numbers"] else "尚未開袋"

        content += f"""
        【{name}】
        狀態：{status}
        時間：{r['created_at']}
        號碼：{numbers}
        -------------------------
        """
    return Response(
        content,
        mimetype="text/plain; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=bags.txt"},
    )
