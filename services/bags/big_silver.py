from services.bags.core import build_ball_scores


def build_silver_scores(last_draw, history_rows):

    scores, market = build_ball_scores(last_draw, history_rows)

    # 強力排斥上期號碼
    for n in last_draw:
        scores[n] -= 25

    # 打壓熱門號

    appear_count = market["recent_20_appear"]

    for n, count in appear_count.items():

        if count >= 3:
            scores[n] -= 20

            # 強化冷門號

    for n, count in appear_count.items():

        if count == 0:
            scores[n] += 25

        elif count == 1:
            scores[n] += 15

    return scores
