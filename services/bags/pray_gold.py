from services.bags.core import (
    build_ball_scores,
    get_removed_numbers,
)

import random


def build_pray_gold_scores(last_draw, history_rows):

    # ===== 基礎分數 =====
    scores, market = build_ball_scores(last_draw, history_rows)

    appear_count = market["recent_20_appear"]

    # ===== 準提金袋人格 =====
    for n, count in appear_count.items():

        # 🔥 中熱區強化（核心壓縮）
        if 3 <= count <= 5:
            scores[n] += 20

        # 🔥 熱門區保留
        elif 6 <= count <= 7:
            scores[n] += 5

        # 🔥 完全死亡冷號降權
        elif count == 0:
            scores[n] -= 25

        elif count >= 8:
            scores[n] -= 12

    # ===== 保留連莊 =====
    for n in last_draw:
        scores[n] += 10

        chaos = random.randint(1, 100)

    if chaos <= 18:
        random_ball = random.randint(1, 49)
        scores[random_ball] += 18

    # =========================
    # 🔥 準提金袋自身人格排除區
    # AI核心壓縮人格
    # =========================

    remove_zone = []

    for n, count in appear_count.items():

        # 完全死亡區
        if count == 0:
            remove_zone.append(n)

        # 超低活躍區
        elif count == 1:
            remove_zone.append(n)

        # 冷區開始復活保護
        elif count == 2:

            revive_roll = random.randint(1, 100)

            # 35% 機率放過
            if revive_roll <= 35:
                continue

            remove_zone.append(n)

        # 極端高尾冷區
        elif n >= 45 and count <= 1:
            remove_zone.append(n)

    # 控制 remove 數量
    random.shuffle(remove_zone)

    remove_zone = remove_zone[: random.randint(12, 15)]

    print("準提金袋排除區:", remove_zone)

    # 正式降權
    for n in remove_zone:
        scores[n] -= 30

    return scores
