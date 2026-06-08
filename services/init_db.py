from services.db import get_shop_db, get_lottery_db


# =========================
# users
# =========================
def init_user_db():

    conn = get_shop_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        points INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


# =========================
# orders
# =========================
def init_orders_db():

    conn = get_shop_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,
        username TEXT,

        product_id INTEGER,
        product_name TEXT,

        qty INTEGER,
        price INTEGER,
        shipping INTEGER,
        total INTEGER,

        name TEXT,
        phone TEXT,
        address TEXT,

        payment_method TEXT,
        status TEXT,

        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


# =========================
# transactions
# =========================
def init_transactions_db():

    conn = get_shop_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        type TEXT,
        status TEXT,

        amount INTEGER,

        balance_before INTEGER,
        balance_after INTEGER,

        source_type TEXT,
        source_id INTEGER,

        note TEXT,

        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

    # ======== ========= =========


# 🛠 商品DB升級（只跑一次）
# ========= ========= =========
def upgrade_products_table():
    conn = get_shop_db()
    c = conn.cursor()

    # 👉 先確保 table 存在
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT
        )
    """)

    c.execute("PRAGMA table_info(products)")
    columns = [col[1] for col in c.fetchall()]

    if "category" not in columns:
        c.execute("ALTER TABLE products ADD COLUMN category TEXT DEFAULT '食品'")

    if "stock" not in columns:
        c.execute("ALTER TABLE products ADD COLUMN stock INTEGER DEFAULT 0")

    if "status" not in columns:
        c.execute("ALTER TABLE products ADD COLUMN status INTEGER DEFAULT 1")

    conn.commit()
    conn.close()


def init_lottery_db():
    conn = get_lottery_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS lottery_results (
        draw_date TEXT PRIMARY KEY,
        numbers TEXT
    )
    """)

    conn.commit()
    conn.close()
