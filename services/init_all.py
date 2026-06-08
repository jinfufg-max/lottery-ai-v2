from services.db import *
from services.init_db import *


# =========================
# 🛒 商城 DB 初始化
# =========================
def init_shop_db():

    conn = get_shop_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        stock INTEGER DEFAULT 0,
        desc TEXT,
        image1 TEXT,
        image2 TEXT,
        status INTEGER DEFAULT 1
    )
    """)

    conn.commit()
    conn.close()


# =========================
# 🔥 升級 orders 表
# =========================
def upgrade_orders_table():

    conn = get_shop_db()
    c = conn.cursor()

    c.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='orders'
    """)

    table = c.fetchone()

    if not table:
        conn.close()
        return

    c.execute("PRAGMA table_info(orders)")
    columns = [col[1] for col in c.fetchall()]

    if "username" not in columns:
        c.execute("ALTER TABLE orders ADD COLUMN username TEXT")

    if "created_at" not in columns:
        c.execute("ALTER TABLE orders ADD COLUMN created_at DATETIME")

    conn.commit()
    conn.close()


# =========================
# 🎒 升級 user_bags 表
# =========================
def upgrade_user_bags_table():

    conn = get_shop_db()
    c = conn.cursor()

    c.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='user_bags'
    """)

    table = c.fetchone()

    if not table:
        conn.close()
        return

    c.execute("PRAGMA table_info(user_bags)")
    columns = [col[1] for col in c.fetchall()]

    if "status" not in columns:
        c.execute("""
            ALTER TABLE user_bags
            ADD COLUMN status TEXT DEFAULT 'pending'
        """)

    if "target_draw_date" not in columns:
        c.execute("""
            ALTER TABLE user_bags
            ADD COLUMN target_draw_date TEXT
        """)

    if "opened_at" not in columns:
        c.execute("""
            ALTER TABLE user_bags
            ADD COLUMN opened_at TEXT
        """)

    if "settled_at" not in columns:
        c.execute("""
            ALTER TABLE user_bags
            ADD COLUMN settled_at TEXT
        """)

    if "hit_count" not in columns:
        c.execute("""
            ALTER TABLE user_bags
            ADD COLUMN hit_count INTEGER
        """)

    conn.commit()
    conn.close()


# =========================
# 🤖 AI predictions
# =========================
def init_ai_predictions_db():

    conn = get_lottery_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS ai_predictions (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        created_at TEXT,

        draw_date TEXT,

        model TEXT,

        numbers TEXT,

        hit_count INTEGER DEFAULT 0

    )
    """)

    conn.commit()
    conn.close()


# =========================
# 🤖 AI usage
# =========================
def init_ai_usage_db():

    conn = get_lottery_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS ai_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        identifier TEXT,
        use_date TEXT
    )
    """)

    conn.commit()
    conn.close()


# =========================
# 🚀 初始化全部
# =========================
def init_all():

    # ===== 基礎 DB =====
    init_user_db()

    init_orders_db()

    init_transactions_db()

    init_lottery_db()

    init_shop_db()

    # ===== 升級 =====
    upgrade_orders_table()

    upgrade_user_bags_table()

    # ===== AI =====
    init_ai_predictions_db()

    init_ai_usage_db()
