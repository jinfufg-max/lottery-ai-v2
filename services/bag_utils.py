from services.db import get_lottery_db

BAG_INFO = {
    "silver": {
        "name": "🥈 大銀袋",
        "price": 2,
    },
    "gold": {
        "name": "🥇 大金袋",
        "price": 3,
    },
    "pray_silver": {
        "name": "✨ 準提銀袋",
        "price": 5,
    },
    "pray_gold": {
        "name": "🔥 準提金袋",
        "price": 10,
    },
}


def get_bag_name(bag_type):

    return BAG_INFO.get(bag_type, {}).get("name", bag_type)


def get_bag_price(bag_type):

    return BAG_INFO.get(bag_type, {}).get("price", 0)


import random

from services.ball_factory import (
    build_gold_scores,
    build_silver_scores,
    build_pray_gold_scores,
    build_pray_silver_scores,
    get_removed_numbers,
)


def build_removed_numbers(last_draw, bag_type):

    conn = get_lottery_db()

    history_rows = conn.execute("""
        SELECT numbers
        FROM lottery_results
    """).fetchall()

    if bag_type == "gold":
        scores = build_gold_scores(last_draw, history_rows)

    elif bag_type == "silver":
        scores = build_silver_scores(last_draw, history_rows)

    elif bag_type == "pray_gold":
        scores = build_pray_gold_scores(last_draw, history_rows)

    else:
        scores = build_pray_silver_scores(last_draw, history_rows)

    removed = get_removed_numbers(scores)

    return removed
