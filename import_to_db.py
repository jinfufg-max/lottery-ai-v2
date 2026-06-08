import pandas as pd
import sqlite3
import os

FILE = "大樂透.csv"
DB = "lottery_v2.db"

# =========================
# 檔案檢查（防呆）
# =========================
if not os.path.exists(FILE):
    print("❌ 找不到檔案:", FILE)
    exit()

df = pd.read_csv(FILE, header=None)

from services.db import get_lottery_db

conn = get_lottery_db()
c = conn.cursor()

# =========================
# 建表（保險）
# =========================
c.execute("""
CREATE TABLE IF NOT EXISTS lottery_results (
    draw_date TEXT PRIMARY KEY,
    numbers TEXT NOT NULL
)
""")

# =========================
# 清空舊資料（重建）
# =========================
c.execute("DELETE FROM lottery_results")

# =========================
# 統計
# =========================
skipped_total = 0

skip_reason = {"count": 0, "duplicate": 0, "range": 0, "special": 0}

inserted = 0

# =========================
# 匯入開始
# =========================
for _, row in df.iterrows():
    data = list(row.dropna())

    date = data[0]
    nums = [int(n) for n in data[1:]]

    # ===== 驗證 =====

    # 1️⃣ 數量
    if len(nums) != 7:
        print("❌ 跳過（數量錯）:", date, nums)
        skipped_total += 1
        skip_reason["count"] += 1
        continue

    main = nums[:6]
    special = nums[6]

    # 2️⃣ 主號重複
    if len(set(main)) != 6:
        print("❌ 跳過（主號重複）:", date, nums)
        skipped_total += 1
        skip_reason["duplicate"] += 1
        continue

    # 3️⃣ 範圍
    if any(n < 1 or n > 49 for n in nums):
        print("❌ 跳過（超出範圍）:", date, nums)
        skipped_total += 1
        skip_reason["range"] += 1
        continue

    # 4️⃣ 特別號
    if special in main:
        print("❌ 跳過（特別號重複）:", date, nums)
        skipped_total += 1
        skip_reason["special"] += 1
        continue

    # ===== 寫入 =====
    numbers = ",".join(map(str, nums))

    c.execute(
        """
        INSERT OR REPLACE INTO lottery_results (draw_date, numbers)
        VALUES (?, ?)
    """,
        (date, numbers),
    )

    inserted += 1

# =========================
# 結果輸出
# =========================
conn.commit()
conn.close()

print("\n===== 匯入結果 =====")
print("成功寫入:", inserted)
print("跳過總數:", skipped_total)
print("數量錯:", skip_reason["count"])
print("主號重複:", skip_reason["duplicate"])
print("範圍錯:", skip_reason["range"])
print("特別號錯:", skip_reason["special"])
print("✅ 匯入完成")
