import random

import sqlite3

from services.db import get_lottery_db


def build_ball_scores(last_draw, history_rows):

    scores = {}

    # 1~49
    for n in range(1, 50):
        scores[n] = 0

    # =========================
    # 最近5期熱號
    # 避免過熱
    # =========================
    recent_5 = history_rows[-5:]

    for row in recent_5:

        nums = list(map(int, row["numbers"].split(",")))

        for n in nums:

            scores[n] -= random.randint(2, 5)

    # =========================
    # 上期連莊降權
    # 避免黏死
    # =========================
    for n in last_draw:

        scores[n] -= random.randint(6, 14)

    total = len(history_rows)

    # =========================
    # AI潮汐人格
    # =========================
    tide_mode = random.randint(1, 100)

    # ===== 短浪人格 =====
    if tide_mode <= 25:

        window_size = random.randint(50, 120)

    # ===== 中浪人格 =====
    elif tide_mode <= 55:

        window_size = random.randint(150, 350)

    # ===== 大浪人格 =====
    elif tide_mode <= 85:

        window_size = random.randint(400, 900)

    # ===== 深海人格 =====
    else:

        if total < 1000:
            window_size = total
        else:
            window_size = random.randint(1000, min(2000, total))

    # =========================
    # 第一海流
    # =========================
    if total <= window_size:

        recent_history = history_rows

        start = 0

    else:

        start = random.randint(0, total - window_size)

        recent_history = history_rows[start : start + window_size]

    print("第一海流:", start, "~", start + window_size)

    # =========================
    # 第二海流
    # =========================
    second_window = random.choice(
        [
            80,
            120,
            200,
            500,
            900,
            1500,
        ]
    )

    if total <= second_window:

        second_history = history_rows

        second_start = 0

    else:

        second_start = random.randint(0, total - second_window)

        second_history = history_rows[second_start : second_start + second_window]

    print("第二海流:", second_start, "~", second_start + second_window)

    # =========================
    # 出現統計
    # =========================
    appear_count = {}

    # =========================
    # 最近20期市場統計
    # =========================
    recent_20 = history_rows[-20:]

    recent_20_appear = {}

    for n in range(1, 50):

        recent_20_appear[n] = 0

    for row in recent_20:

        nums = list(map(int, row["numbers"].split(",")))

        for n in nums:

            recent_20_appear[n] += 1

    for n in range(1, 50):

        appear_count[n] = 0

    # ===== 第一海流統計 =====
    for row in recent_history:

        nums = list(map(int, row["numbers"].split(",")))

        for n in nums:

            appear_count[n] += 1

    # ===== 第二海流統計 =====
    for row in second_history:

        nums = list(map(int, row["numbers"].split(",")))

        for n in nums:

            appear_count[n] += 1

    # =========================
    # AI動態人格
    # =========================
    for n, count in appear_count.items():

        # 冷區微復活
        if count == 0:

            scores[n] += random.randint(4, 10)

        # 微冷區
        elif count == 1:

            scores[n] += random.randint(2, 8)

        # 中熱核心
        elif 3 <= count <= 5:

            scores[n] += random.randint(6, 15)

        # 過熱懷疑
        elif count >= 8:

            scores[n] -= random.randint(5, 15)

    # =========================
    # AI人格亂流
    # =========================
    chaos = random.randint(1, 100)

    if chaos <= 50:

        candidate = []

        for n, count in appear_count.items():

            if 2 <= count <= 5:

                candidate.append(n)

        if candidate:

            random_ball = random.choice(candidate)

            # ===== 偏執強化 =====
            if random.randint(1, 100) <= 70:

                scores[random_ball] += random.randint(10, 25)

                print("人格強化:", random_ball)

            # ===== 偏執毀滅 =====
            else:

                scores[random_ball] -= random.randint(10, 25)

                print("人格毀滅:", random_ball)

    # =========================
    # AI海嘯模式
    # 偶發全面翻海
    # =========================
    tsunami = random.randint(1, 100)

    if tsunami <= 12:

        print("AI海嘯啟動")

        for n in scores:

            scores[n] += random.randint(-20, 20)

    market = {
        "appear_count": appear_count,
        "recent_20_appear": recent_20_appear,
    }

    print(scores)

    return scores, market


def get_removed_numbers(scores):

    # 分數最低優先排除
    sorted_balls = sorted(scores.items(), key=lambda x: x[1])

    # =========================
    # AI動態壓縮
    # =========================
    remove_count = random.choice(
        [
            5,
            6,
            8,
            10,
            12,
            15,
            18,
            22,
        ]
    )

    removed = [n for n, s in sorted_balls[:remove_count]]

    print("排除球:", removed)

    return removed


def get_market_data():

    conn = get_lottery_db()

    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    # 最新一期
    c.execute("""
        SELECT numbers
        FROM lottery_results
        ORDER BY draw_date DESC
        LIMIT 1
    """)

    latest = c.fetchone()

    if latest:

        last_draw = list(map(int, latest["numbers"].split(",")))

    else:

        last_draw = []

    # 最近50期
    c.execute("""
        SELECT numbers
        FROM lottery_results
        ORDER BY draw_date DESC
        LIMIT 50
    """)

    history_rows = c.fetchall()

    conn.close()

    return last_draw, history_rows


def build_sorted_scores(scores):

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
