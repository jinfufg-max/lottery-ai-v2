from flask import Blueprint, render_template, request

from services.lottery_service import get_latest_draw

check_bp = Blueprint("check", __name__)


# =========================
# 🎯 對獎
# =========================
@check_bp.route("/check", methods=["GET", "POST"])
def check():

    draw_numbers, special_number, draw_date = get_latest_draw()

    period = "尚未更新"
    results = ["", "", "", "", "", ""]
    inputs = ["", "", "", "", "", ""]

    if draw_numbers:
        period = f"{draw_date}（最新一期）"

    if request.method == "POST":

        for i in range(6):  # ✅ 固定6組
            raw = request.form.get(f"set{i+1}", "").strip()
            inputs[i] = raw

            if not raw:
                continue

            try:
                nums = [int(x) for x in raw.split(",") if x]

                # 數量錯誤
                if len(nums) != 6:
                    results[i] = "X"
                    continue

                # 重複
                if len(set(nums)) != 6:
                    results[i] = "X"
                    continue

                # 範圍
                if any(n < 1 or n > 49 for n in nums):
                    results[i] = "X"
                    continue

                # 沒開獎
                if not draw_numbers:
                    results[i] = "-"
                    continue

                # 命中
                match = len(set(nums) & set(draw_numbers))
                results[i] = match

            except:
                results[i] = "X"

    return render_template(
        "check.html",
        period=period,
        draw_numbers=draw_numbers,
        special_number=special_number,
        results=results,
        inputs=inputs,
    )
