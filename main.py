"""
User after Login and user page
"""

import os

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for

# Modules from own library
from modules.cookie import Cookie
from modules.form import LoginForm, RegisterForm
from modules.mongo import MongoDB
from modules.password import Password
# Flask Blueprint
from user.routes import user

# Setup
load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Add blueprint section
app.register_blueprint(user)

# Work List MongoDB connect
_mongo = MongoDB()

# Password
_pass = Password()

# Cookie
_cookie = Cookie()


@app.route("/", methods=["GET", "POST"])
def index():
    """
    链接至 index.html, 同时也输出日期
    """
    title = "Employee work system - Login"
    error = ""

    form = LoginForm(request.form)
    check_users = _mongo.user_collection().find({})

    if form.validate_on_submit():
        get_email = form.email.data
        get_password = form.password.data

        for member in check_users:
            company_name = member["company_name"]

            if member["email"] == get_email and _pass.check_password(
                get_password, member["password"]
            ):
                # set cookie
                resp = _cookie.set_cookie(
                    page="user.mainpage",
                    cookie_name="userID",
                    cookie_value=company_name,
                )
                return resp
            else:
                error = "Invalid credentials, please register"

    # if login direct to user page else to login page
    if request.cookies.get("userID"):
        return redirect(url_for("user.mainpage"))
    else:
        return render_template("index.html", title=title, form=form, error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register"""
    title = "Employee work system - Register"

    form = RegisterForm(request.form)
    get_emp = _mongo.user_collection().find({})
    error = ""

    # Members in list
    users_list = [list_member["email"] for list_member in get_emp]


    if form.validate_on_submit():
        # From register.html Form
        email = form.email.data.strip()
        password = form.password.data.strip()
        company_name = form.company_name.data.strip()

        # Password to hash
        generate_password = _pass.create_password(password)

        # dict mongodb
        new_members = {
            "email": email,
            "password": generate_password,
            "company_name": str(company_name).upper(),
        }

        if len(users_list) == 0:
            _mongo.user_collection().insert_one(new_members)
            return redirect(url_for("index"))
        else:
            if email not in users_list:
                _mongo.user_collection().insert_one(new_members)
                return redirect(url_for("index"))
            else:
                error = "You have registed, please login"

    return render_template("register.html", form=form, title=title, error=error)


@app.route("/logout")
def logout():
    """Logout"""
    resp = _cookie.empty_cookie(page="index", cookie_name="userID")
    return resp


@app.errorhandler(404)
def page_not_found(e):
    """Page Not Found"""
    title = _cookie.get_cookie("userID")
    return render_template("404.html", title=title), 404


@app.errorhandler(AttributeError)
def not_login(e):
    """Not Login"""
    return render_template("attrerror.html")


if __name__ == "__main__":
    app.run(debug=True)
