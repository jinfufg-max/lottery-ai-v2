from services.db import get_lottery_db, get_shop_db
from datetime import datetime, timedelta


# =========================
# 🔥 缺期檢查
# =========================
def check_missing_draws():

    conn = get_lottery_db()
    c = conn.cursor()

    c.execute("""
        SELECT draw_date
        FROM lottery_results
        ORDER BY draw_date DESC
        LIMIT 20
    """)

    rows = c.fetchall()

    conn.close()

    if not rows:
        return []

    existing = set([r[0] for r in rows])

    dates = sorted(existing, reverse=True)

    start = datetime.strptime(dates[-1], "%Y-%m-%d")
    end = datetime.strptime(dates[0], "%Y-%m-%d")

    missing = []

    d = start

    while d <= end:

        if d.weekday() in [1, 4]:

            ds = d.strftime("%Y-%m-%d")

            if ds not in existing:
                missing.append(ds)

        d += timedelta(days=1)

    return missing


# =========================
# 🔥 AI使用限制
# =========================
def can_use_ai(identifier):

    conn = get_shop_db()
    c = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    c.execute(
        """
        SELECT COUNT(*)
        FROM ai_usage
        WHERE identifier=?
        AND date(created_at)=?
    """,
        (identifier, today),
    )

    count = c.fetchone()[0]

    conn.close()

    return count == 0


# =========================
# 🔥 紀錄AI使用
# =========================
def record_ai_use(identifier):

    conn = get_shop_db()
    c = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.execute(
        """
        INSERT INTO ai_usage (
            identifier,
            created_at
        )
        VALUES (?, ?)
    """,
        (identifier, now),
    )

    conn.commit()
    conn.close()
