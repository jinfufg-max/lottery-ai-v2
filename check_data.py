import pandas as pd

FILE = "大樂透.csv"

df = pd.read_csv(FILE, header=None)

errors = []

for i, row in df.iterrows():
    data = list(row.dropna())

    # 👉 分離
    date = data[0]
    nums = data[1:]

    # 1️⃣ 數量檢查
    if len(nums) != 7:
        errors.append((i, "數量錯誤", nums))
        continue

    nums = [int(n) for n in nums]

    main = nums[:6]
    special = nums[6]

    # 2️⃣ 主號重複
    if len(set(main)) != 6:
        errors.append((i, "主號重複", main))

    # 3️⃣ 範圍檢查
    for n in nums:
        if n < 1 or n > 49:
            errors.append((i, "數值超界", nums))

    # 4️⃣ 特別號重複
    if special in main:
        errors.append((i, "特別號重複", nums))

print("======== 結果 ========")
print("總筆數:", len(df))
print("錯誤數:", len(errors))

if errors:
    for e in errors[:10]:
        print(e)
else:
    print("✅ 完全乾淨")