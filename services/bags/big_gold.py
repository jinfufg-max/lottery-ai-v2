from services.bags.core import build_ball_scores
import random


def build_gold_scores(last_draw, history_rows):

    scores, market = build_ball_scores(last_draw, history_rows)

    appear_count = market["recent_20_appear"]

    # ===== 大金袋人格 =====

    for n, count in appear_count.items():

        # 🔥 超熱門開始反轉
        if count >= 6:
            scores[n] -= 20

        # 🔥 主流核心區（保留）
        elif 4 <= count <= 5:
            scores[n] += 8

        # 🔥 第二核心層（開始輪動）
        elif count == 3:
            scores[n] += 12

        # 🔥 微熱區（擴散）
        elif count == 2:
            scores[n] += 8

        # 🔥 完全死亡冷號降權
        elif count == 0:
            scores[n] -= 10
            # ===== 保留少量連莊 =====
            for n in last_draw:
                scores[n] += 2

    # =========================
    # 🔥 大金袋自身人格排除區
    # 主流核心壓縮人格
    # =========================

    remove_zone = []

    for n, count in appear_count.items():

        # 超熱門垃圾區
        if count >= 7:
            remove_zone.append(n)

        # 完全死亡區
        elif count == 0:
            remove_zone.append(n)

        # 高尾極端冷區
        elif n >= 45 and count <= 1:
            remove_zone.append(n)

    # 控制 remove 數量
    random.shuffle(remove_zone)

    remove_zone = remove_zone[: random.randint(15, 18)]

    print("大金袋排除區:", remove_zone)

    # 正式降權
    for n in remove_zone:
        scores[n] -= 30

    return scores
