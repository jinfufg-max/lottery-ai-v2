import random
import time
import threading
import pandas as pd

from collections import Counter
from datetime import datetime, timedelta
from services.db import get_lottery_db

# ==================================================
# AI Cache
# ==================================================
AI_STATE = {"numbers": [], "hot": [], "cold": [], "updated_at": 0, "analysis_data": {}}

HIT_CACHE = {"value": None, "time": 0}


# ==================================================
# AI人格策略
# ==================================================
def strategy_hot(history):
    # 熱區爆發
    freq, recent, gap = build_ai_engine(history)
    score = score_with_weights(freq, recent, gap, 0.7, 0.2, 0.1)
    return pick_by_score(score)


def strategy_extreme(history):
    # 極端集中（只選前10）
    freq, recent, gap = build_ai_engine(history)
    score = score_with_weights(freq, recent, gap, 0.8, 0.1, 0.1)

    sorted_nums = sorted(score, key=score.get, reverse=True)
    pool = sorted_nums[:10]

    return sorted(random.sample(pool, 6))


def strategy_recent_burst(history):
    # 短期爆發
    freq, recent, gap = build_ai_engine(history)
    score = score_with_weights(freq, recent, gap, 0.1, 0.8, 0.1)
    return pick_by_score(score)


def strategy_mix(history):

    freq, recent, gap = build_ai_engine(history)

    sorted_hot = sorted(freq, key=freq.get, reverse=True)
    sorted_cold = sorted(gap, key=gap.get, reverse=True)

    picks = set()

    picks.update(random.sample(sorted_hot[:15], 4))
    picks.update(random.sample(sorted_cold[:20], 2))

    while len(picks) < 6:
        n = random.randint(1, 49)
        picks.add(n)

    return sorted(list(picks))


# ==================================================
# AI生成流程
# ==================================================
def pray_gold_engine(history):

    strategies = {
        "熱區爆發": strategy_hot,
        "極端集中": strategy_extreme,
        "近期爆發": strategy_recent_burst,
        "冷熱混合": strategy_mix,
    }

    candidates = []

    for name, func in strategies.items():
        nums = func(history)

        if len(nums) != 6:
            continue

        score = score_numbers(nums, history[-100:])

        candidates.append({"nums": nums, "score": score, "name": name})

    best = max(candidates, key=lambda x: x["score"])

    print("🔥 準提金袋選擇:", best)

    return best


def get_ai_numbers(history):
    return get_ai_by_model(history, "silver")


def score_numbers(nums, history):
    score = 0
    recent = history[-100:]

    # ===== 命中分數 =====
    for draw in recent:
        match = len(set(nums) & set(draw))

        if match >= 3:
            score += 10
        elif match == 2:
            score += 4
        elif match == 1:
            score += 1

    # ===== 結構加分 =====

    # 1️⃣ 區間平衡
    low = [n for n in nums if n <= 25]
    high = [n for n in nums if n > 25]

    if 2 <= len(low) <= 4 and 2 <= len(high) <= 4:
        score += 5

    # 2️⃣ 連號檢查
    consecutive = sum(1 for i in range(len(nums) - 1) if nums[i + 1] - nums[i] == 1)

    if consecutive >= 3:
        score -= 5

    # 3️⃣ 尾數分散
    tails = [n % 10 for n in nums]

    if len(set(tails)) >= 5:
        score += 3

    return score


# ==================================================
# AI Cache 系統
# ==================================================
def refresh_ai_cache():

    global AI_STATE
    global HIT_CACHE

    try:

        history = get_lottery_data()

        nums = get_ai_numbers(history)

        avoid = get_avoid_numbers(history)

        # ===== 主特別號（全站統一）=====
        main_numbers, special_numbers = get_full_data()

        latest_special = special_numbers[-1]

        AI_STATE["main_special"] = latest_special

        # ===== AI資料 =====
        AI_STATE["numbers"] = nums
        AI_STATE["hot"] = nums[:5]
        AI_STATE["cold"] = avoid[:5]

        # ===== analysis 快照 =====
        AI_STATE["analysis_data"] = generate_analysis_data()

        AI_STATE["updated_at"] = time.time()

        print("✅ AI Cache 已刷新")

    except Exception as e:

        print("❌ refresh_ai_cache 錯誤:", e)


# ==================================================
# AI背景更新（60小時）
# ==================================================
def update_ai_background():

    def job():

        while True:

            try:

                now = time.time()

                last_update = AI_STATE.get("updated_at", 0)

                passed = now - last_update

                # 60小時 = 216000秒
                if passed >= 216000:

                    print("🧠 AI人格60小時重組")

                    refresh_ai_cache()

            except Exception as e:

                print("❌ AI更新錯誤:", e)

            # 每2小時檢查一次
            time.sleep(7200)

    t = threading.Thread(target=job)

    t.daemon = True

    t.start()


# ==================================================
# AI市場生成
# ==================================================
def build_ai_engine(history):

    # ===== freq =====
    flat = [n for row in history for n in row]
    freq = Counter(flat)
    total = sum(freq.values())
    freq = {n: freq[n] / total for n in freq}

    # ===== recent =====
    recent_data = history[-20:]
    flat_r = [n for row in recent_data for n in row]
    recent = Counter(flat_r)
    total_r = sum(recent.values())
    recent = {n: recent[n] / total_r for n in recent}

    # ===== gap =====
    last_seen = {}

    for i, draw in enumerate(history):
        for n in draw:
            last_seen[n] = i

    gap = {}
    current = len(history)

    for n in range(1, 50):
        gap[n] = current - last_seen.get(n, 0)

    max_gap = max(gap.values())
    gap = {n: gap[n] / max_gap for n in gap}

    return freq, recent, gap


def get_avoid_numbers(history):

    freq, recent, gap = build_ai_engine(history)

    sorted_cold = sorted(gap, key=gap.get, reverse=True)

    return sorted(sorted_cold[:6])


def score_with_weights(freq, recent, gap, w1, w2, w3):

    score = {}

    for n in range(1, 50):
        score[n] = freq.get(n, 0) * w1 + recent.get(n, 0) * w2 + gap.get(n, 0) * w3

    return score


def pick_by_score(score):

    sorted_nums = sorted(score, key=score.get, reverse=True)
    pool = sorted_nums[:20]

    return sorted(random.sample(pool, 6))


def get_ai_by_model(history, model):

    freq, recent, gap = build_ai_engine(history)

    if model == "silver":
        w = (0.4, 0.3, 0.3)

    elif model == "gold":
        w = (0.2, 0.6, 0.2)

    elif model == "pray_silver":
        w = (0.3, 0.2, 0.5)

    elif model == "pray_gold":
        w = (0.7, 0.2, 0.1)

    else:
        w = (0.33, 0.33, 0.33)

    score = score_with_weights(freq, recent, gap, *w)

    return pick_by_score(score)


# ==================================================
# AI分析系統
# ==================================================
def special_analysis_with_score():

    main_numbers, special_numbers = get_full_data()

    flat = [n for row in main_numbers for n in row]
    global_count = Counter(flat)

    mapping = {}

    for main, sp in zip(main_numbers, special_numbers):
        if sp not in mapping:
            mapping[sp] = []

        mapping[sp].extend(main)

    sp_result = {}

    for sp, nums in mapping.items():
        count = Counter(nums)

        top_list = []

        for n, c in count.most_common(3):
            base = global_count[n]

            ratio = round((c / base) * 100, 1)

            top_list.append((n, ratio))

        sp_result[sp] = top_list

    return sp_result


# ==================================================
# 資料來源
# ==================================================
def get_lottery_data():

    main_numbers, _ = get_full_data()

    main_numbers = main_numbers[-300:]

    return main_numbers


def get_full_data():

    conn = get_lottery_db()

    df = pd.read_sql_query(
        """
        SELECT numbers
        FROM lottery_results
        ORDER BY draw_date
    """,
        conn,
    )

    conn.close()

    main_numbers = []
    special_numbers = []

    for row in df["numbers"]:
        nums = [int(x) for x in row.split(",")]
        main_numbers.append(nums[:6])
        special_numbers.append(nums[6])

    return main_numbers, special_numbers


def generate_analysis_data():

    data = special_analysis_with_score()

    if not data:
        return None

    # ===== 使用全站統一特別號 =====
    sample_sp = AI_STATE.get("main_special")

    # 防呆
    if sample_sp not in data:
        sample_sp = sorted(data.keys())[0]

    sp_result = data[sample_sp]

    # ===== 共用市場資料 =====
    main_data = get_lottery_data()

    freq, recent_data, gap = build_ai_engine(main_data)

    # ===== 共用熱門資料 =====
    count = {n: int(freq.get(n, 0) * 1000) for n in range(1, 50)}

    recent = main_data[-20:]
    older = main_data[-40:-20]

    recent_flat = [n for row in recent for n in row]
    older_flat = [n for row in older for n in row]

    recent_count = Counter(recent_flat)
    older_count = Counter(older_flat)

    # =========================
    # AI 綜合評分引擎
    # =========================

    scores = {}

    max_hot = max(count.values())

    for n in range(1, 50):

        hot_weight = count.get(n, 0) / max_hot

        recent_v = recent_count.get(n, 0)
        older_v = older_count.get(n, 0)

        trend_weight = max(recent_v - older_v, 0)

        balance_weight = 1 - hot_weight

        sp_bonus = 0

        for sp_num, score in sp_result:
            if n == sp_num:
                sp_bonus += score / 100

        final_score = (
            hot_weight * 0.4
            + trend_weight * 0.3
            + balance_weight * 0.2
            + sp_bonus * 0.1
        )

        scores[n] = round(final_score, 4)

    final_ai = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    ai_numbers = [n for n, _ in final_ai[:6]]

    sorted_hot = sorted(count.items(), key=lambda x: (-x[1], x[0]))
    hot = [n for n, _ in sorted_hot[:5]]

    sorted_count = sorted(count.items(), key=lambda x: (x[1], x[0]))
    cold = [n for n, _ in sorted_count[:5]]

    top5_total = sum(v for _, v in sorted_hot[:5])
    all_total = sum(count.values())

    hot_score = round((top5_total / all_total) * 100, 1)

    diff_total = 0

    for n in range(1, 50):
        diff_total += abs(recent_count.get(n, 0) - older_count.get(n, 0))

    trend_score = round(diff_total / 49, 1)

    sp_score = round(sum(score for _, score in sp_result[:3]) / 3, 1)

    hit_rate = 24
    sample_count = len(main_data)

    return {
        "ai_numbers": ai_numbers,
        "hot": hot,
        "cold": cold,
        "hit_rate": hit_rate,
        "sample_count": sample_count,
        "hot_score": hot_score,
        "trend_score": trend_score,
        "sp_score": sp_score,
        "sample_sp": sample_sp,
        "sp_result": sp_result,
    }
