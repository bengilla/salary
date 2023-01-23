"""
User after Login and user page
"""

import os
import uvicorn

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Modules from own library
from modules.cookie import Cookie
from modules.form import LoginForm, RegisterForm
from modules.mongo import MongoDB
from modules.password import Password
# Flask Blueprint
# from user.routes import user

# Setup
app = FastAPI(title="TBROS")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

load_dotenv()

# MongoDB
_mongo = MongoDB()

# Password
_pass = Password()

# Cookie
_cookie = Cookie()

# Index----------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page of tbros website"""
    title = "Employee work system - Login"
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": title
        }
    )

@app.post("/")
async def index_post(login_data: LoginForm = Depends(LoginForm.login)):
    """Get login data and check user does exist"""
    return {"message": login_data}

# Register----------------------------------------------------------------------
@app.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    """register page"""
    title = "Employee work system - Register"

    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "title": title,
        }
    )

@app.post("/register")
async def register_post(request: Request, register_data: RegisterForm = Depends(RegisterForm.register)):
    """Get register data to save on mongodb"""
    user_list = [user["email"] for user in _mongo.user_collection().find({})]
    hash_password = _pass.create_password(register_data.password)

    new_user = {
        "email": register_data.email,
        "password": hash_password,
        "company_name": register_data.company_name.replace(" ", "").upper()
    }

    if register_data.email not in user_list:
        _mongo.user_collection().insert_one(new_user)
        redirect_url = request.url_for("index")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    else:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "title": "User is exsit"
            }
        )

# @app.route("/logout")
# def logout():
#     """Logout"""
#     resp = _cookie.empty_cookie(page="index", cookie_name="userID")
#     return resp


# @app.errorhandler(404)
# def page_not_found(e):
#     """Page Not Found"""
#     title = _cookie.get_cookie("userID")
#     return render_template("404.html", title=title), 404


# @app.errorhandler(AttributeError)
# def not_login(e):
#     """Not Login"""
#     return render_template("attrerror.html")