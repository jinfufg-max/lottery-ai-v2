import pandas as pd
import sqlite3

LOTTERY_DB = "lottery_v2.db"


def get_full_data():
    from services.db import get_lottery_db

    conn = get_lottery_db()
    df = pd.read_sql_query("SELECT * FROM lottery", conn)
    conn.close()
    return df


def get_lottery_data():
    df = get_full_data()

    # 你原本的 AI 邏輯（貼過來）

    return df
