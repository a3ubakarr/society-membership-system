from flask import Blueprint, render_template, request, redirect, session

auth_bp = Blueprint("auth", __name__)  # no url_prefix

STATIC_USER = "admin"
STATIC_PASS = "admin123"

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if (request.form["username"] == STATIC_USER and
            request.form["password"] == STATIC_PASS):
            session["user"] = "admin"
            return redirect("/home")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")
