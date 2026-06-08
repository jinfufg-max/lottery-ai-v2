import random

from services.bags.core import (
    build_ball_scores,
    get_removed_numbers,
)

from services.bags.big_silver import build_silver_scores


def build_pray_silver_scores(last_draw, history_rows):

    # =========================
    # 基礎分數
    # =========================

    scores, market = build_ball_scores(last_draw, history_rows)

    # =========================
    # 取得大銀袋分數
    # =========================

    silver_scores = build_silver_scores(last_draw, history_rows)

    # 大銀袋排除區
    silver_removed = get_removed_numbers(silver_scores)

    print("準提銀袋接收區:", silver_removed)

    # =========================
    # 🔥 承接大銀袋部分棄球
    # =========================

    boost_count = random.randint(
        int(len(silver_removed) * 0.4),
        int(len(silver_removed) * 0.6),
    )

    boosted = random.sample(silver_removed, boost_count)

    print("準提銀袋強化:", boosted)

    # 強化被大銀袋放棄的號碼
    for n in boosted:
        scores[n] += 15

    # =========================
    # 🔥 準提銀袋自身人格邏輯
    # =========================

    appear_count = market["recent_20_appear"]

    # =========================
    # 🔥 準提銀袋自身排除區
    # =========================

    pray_removed = []

    for n, count in appear_count.items():

        # 超熱門號
        if count >= 6:
            pray_removed.append(n)

        # 太平均中段號
        elif 20 <= n <= 30 and count >= 4:
            pray_removed.append(n)

    # 控制 remove 數量
    random.shuffle(pray_removed)

    pray_removed = pray_removed[: random.randint(12, 15)]

    print("準提銀袋排除區:", pray_removed)

    # 正式降低權重
    for n in pray_removed:
        scores[n] -= 20

    return scores
