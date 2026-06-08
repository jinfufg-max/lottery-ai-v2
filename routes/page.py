from flask import Blueprint, render_template

page_bp = Blueprint("page", __name__)


# =========================
# 🔥 AI資料取得（穩定版）
# =========================
@page_bp.route("/privacy")
def privacy():
    return render_template("privacy.html")


@page_bp.route("/terms")
def terms():
    return render_template("terms.html")


@page_bp.route("/games/mario_demo")
def mario_demo():
    return render_template("games/mario_demo.html")
