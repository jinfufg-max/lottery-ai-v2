from services.db import get_lottery_db


# =========================
# 🟩 取得最新開獎（🔥核心）
# =========================
def get_latest_draw():

    conn = get_lottery_db()
    c = conn.cursor()

    c.execute("""
        SELECT draw_date, numbers
        FROM lottery_results
        ORDER BY draw_date DESC
        LIMIT 1
    """)

    row = c.fetchone()
    conn.close()

    if not row:
        return None, None, None

    date = row[0]
    nums = list(map(int, row[1].split(",")))

    return nums[:6], nums[6], date
