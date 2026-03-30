"""
Authentication routes
"""

import os

from dotenv import load_dotenv
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user

load_dotenv()

auth_bp = Blueprint("auth", __name__)

USERS = {
    os.getenv("LOGIN_USERNAME", "tbros"): os.getenv("LOGIN_PASSWORD", "password")
}


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    if user_id in USERS:
        return User(user_id)
    return None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in USERS and USERS[username] == password:
            login_user(User(username))
            return redirect(url_for("salary.index"))
        error = "Invalid username or password"
    return render_template("login.html", error=error)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


def init_login_manager(app):
    """Initialize login manager with app"""
    login_manager.init_app(app)
