"""
User after Login and user page
"""

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, Depends, Cookie, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Modules from own library
from modules.form import LoginForm, RegisterForm
from modules.mongo import MongoDB
from modules.password import Password

# Setup
app = FastAPI(title="TBROS")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

load_dotenv()

# MongoDB
_mongo = MongoDB()

# Index----------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, response: Response):
    """Main page of tbros website"""
    title = "Employee work system - Login"

    response = templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": title
        }
    )
    response.delete_cookie(key="company_name")
    return response

@app.post("/")
async def index_post(request: Request, response: Response, login_data: LoginForm = Depends(LoginForm.login)):
    """Get login data and check user does exist"""
    _pass = Password()
    check_users = _mongo.user_collection().find({})

    # Get data from form post section
    get_email = login_data.email
    get_password = login_data.password
    
    for user in check_users:
        if get_email == user["email"]:
            password = _pass.check_password(get_password, user["password"])
            
            if password:
                title = user["company_name"]
                response.set_cookie(key="company_name", value=title)

                # redirect_url = request.url_for("user")
                # return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

                return {
                    "status": "Login",
                    "email": user["email"],
                    "company name": user['company_name'],
                }
            else:
                return {
                    "status": "Not Login",
                    "message": "Password not correct!"
                    }

    return {"message": "User doesn't exists"}

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
    hash_password = Password().create_password(register_data.password)

    new_user = {
        "email": register_data.email,
        "password": hash_password,
        "company_name": register_data.company_name.title()
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

# Logout----------------------------------------------------------------------
@app.get("/logout")
def logout(request: Request):
    """Logout"""
    redirect_url = request.url_for("index")
    response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="company_name")
    return response