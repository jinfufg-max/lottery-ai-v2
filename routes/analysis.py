from flask import Blueprint, render_template, session, redirect

from ai.engine import AI_STATE

analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.route("/analysis")
def analysis():

    if "user" not in session:
        return redirect("/login")

    user = session.get("user")

    analysis_data = AI_STATE.get("analysis_data")

    if not analysis_data or "ai_numbers" not in analysis_data:
        return "AI資料初始化中"

    return render_template(
        "analysis.html",
        ai_numbers=analysis_data["ai_numbers"],
        user=user,
        sp=analysis_data["sample_sp"],
        result=analysis_data["sp_result"],
        hot=analysis_data["hot"],
        cold=analysis_data["cold"],
        hit_rate=analysis_data["hit_rate"],
        sample_count=analysis_data["sample_count"],
        hot_score=analysis_data["hot_score"],
        trend_score=analysis_data["trend_score"],
        sp_score=analysis_data["sp_score"],
    )
