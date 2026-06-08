from flask import Blueprint, render_template, request, redirect, session

from flask import current_app

from services.db import get_shop_db

import sqlite3
import bcrypt

from datetime import datetime, timedelta

auth_bp = Blueprint("auth", __name__)


# =========================
# 👤 會員系統（乾淨版）
# =========================
@auth_bp.route("/create_member_order", methods=["POST"])
def create_member_order():

    import random
    from datetime import datetime, timedelta

    conn = get_shop_db()
    c = conn.cursor()

    username = request.form["username"]
    password = request.form["password"]

    name = request.form["name"]
    phone = request.form["phone"]
    address = request.form["address"]
    email = request.form["email"]

    # bcrypt
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )

    # 帳號重複檢查
    c.execute("SELECT id FROM users WHERE username = ?", (username,))

    existing_user = c.fetchone()

    if existing_user:
        conn.close()
        return "帳號已存在"

    order_no = (
        "MEM"
        + (datetime.utcnow() + timedelta(hours=8)).strftime("%m%d%H%M%S")
        + str(random.randint(1000, 9999))
    )

    now = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

    c.execute(
        """
        INSERT INTO orders (
            username,
            password,
            name,
            phone,
            address,
            email,
            total,
            payment_method,
            status,
            order_no,
            created_at,
            order_type,
            is_registered
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            username,
            hashed_password,
            name,
            phone,
            address,
            email,
            100,
            "cash",
            "pending",
            order_no,
            now,
            "member",
            0,
        ),
    )

    # 🔥 先抓 order id
    order_id = c.lastrowid

    # 🔥 建立 transaction
    c.execute(
        """
        INSERT INTO transactions (
            user_id,
            type,
            status,
            amount,
            balance_before,
            balance_after,
            source_type,
            source_id,
            note,
            created_at,
            transaction_no,
            order_no,
            action_type,
            metadata_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            0,
            "cash_order",
            "pending",
            100,
            0,
            0,
            "member_order",
            order_id,
            "會員註冊付款",
            now,
            "TXN" + order_no,
            order_no,
            "cash_payment",
            "{}",
        ),
    )

    conn.commit()
    conn.close()

    return redirect(f"/ecpay_checkout/{order_no}")


@auth_bp.route("/register", methods=["GET"])
def register():

    return render_template(
        "register.html",
        register_price=100,
        register_bonus=150,
        is_free=False,
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_shop_db()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=?",
            (username,),
        )

        user = c.fetchone()
        conn.close()

        if user:

            stored_password = user["password"]

            # =========================
            # 新會員（bcrypt）
            # =========================
            if stored_password.startswith("$2"):

                if bcrypt.checkpw(
                    password.encode("utf-8"), stored_password.encode("utf-8")
                ):

                    session["user"] = user["username"]
                    session["user_id"] = user["id"]

                    return redirect("/bag")

            # =========================
            # 舊會員（明文）
            # =========================
            else:

                if stored_password == password:

                    # 🔥 自動升級 bcrypt
                    conn = get_shop_db()
                    c = conn.cursor()

                    hashed_password = bcrypt.hashpw(
                        password.encode("utf-8"), bcrypt.gensalt()
                    ).decode("utf-8")

                    c.execute(
                        """
                        UPDATE users
                        SET password = ?
                        WHERE id = ?
                        """,
                        (hashed_password, user["id"]),
                    )

                    conn.commit()
                    conn.close()

                    session["user"] = user["username"]
                    session["user_id"] = user["id"]

                    return redirect("/bag")

        return "登入失敗"

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/")


@auth_bp.route("/member")
def member():
    return render_template("member.html")
