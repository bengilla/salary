"""
User Login and Register Page
"""
from fastapi import FastAPI, Request, Response, Depends, Cookie, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Modules from own library
from models.mongo import MongoDB
from models.form import LoginForm, RegisterForm
from models.password import Password
from routes.user import router

# Setup
app = FastAPI(title="TBROS Worker", version=1.0)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# MongoDB
_mongo = MongoDB()


# Index----------------------------------------------------------------------
@app.get(
    "/", tags=["User Login"], response_class=HTMLResponse, description="User login page"
)
async def index(request: Request, response: Response) -> HTMLResponse:
    title = "Employee work system - Login"

    response = templates.TemplateResponse(
        "index.html", {"request": request, "title": title}
    )
    response.delete_cookie(key="company_name")
    response.delete_cookie(key="error_msg")
    return response


@app.post(
    "/",
    tags=["User Login"],
    response_class=RedirectResponse,
    description="User post login data",
)
async def index_post(
    request: Request, login: LoginForm = Depends(LoginForm.login)
) -> RedirectResponse:
    # Password generated
    _pass = Password()

    # Check user is it exists
    check_users = _mongo.user_collection().find({})

    # Get data from form post section
    login_email = login.email
    login_password = login.password

    for user in check_users:
        if login_email == user["email"]:
            password = _pass.check_password(login_password, user["password"])

            if password:
                title = user["company_name"]
                redirect_url = request.url_for("mainpage")
                response = RedirectResponse(
                    redirect_url, status_code=status.HTTP_303_SEE_OTHER
                )
                response.set_cookie(key="company_name", value=title)
                return response
            else:
                redirect_url = request.url_for("error")
                response = RedirectResponse(
                    redirect_url, status_code=status.HTTP_303_SEE_OTHER
                )
                response.set_cookie(key="error_msg", value="Password not correct!")
                return response

    redirect_url = request.url_for("error")
    response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="error_msg", value="User doesn't exists")
    return response


# Register----------------------------------------------------------------------
@app.get(
    "/register",
    tags=["User Register"],
    response_class=HTMLResponse,
    description="Register page",
)
async def register(request: Request) -> HTMLResponse:
    title = "Employee work system - Register"

    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "title": title,
        },
    )


@app.post("/register", tags=["User Register"], description="Register post data")
async def register_post(
    request: Request, register: RegisterForm = Depends(RegisterForm.register)
) -> RedirectResponse:
    user_list = [user["email"] for user in _mongo.user_collection().find({})]
    hash_password = Password().create_password(register.password)

    new_user = {
        "email": register.email,
        "password": hash_password,
        "company_name": register.company_name,
    }

    if register.email not in user_list:
        _mongo.user_collection().insert_one(new_user)
        redirect_url = request.url_for("index")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    else:
        return templates.TemplateResponse(
            "register.html", {"request": request, "title": "User is exsit"}
        )


# # Logout----------------------------------------------------------------------
@app.get("/logout", tags=["User Logout"], description="Logout user")
async def logout(request: Request):
    redirect_url = request.url_for("index")
    response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="company_name")
    response.delete_cookie(key="error_msg")
    return response


# # Error----------------------------------------------------------------------
@app.get(
    "/error", tags=["User Error"], response_class=HTMLResponse, description="Error page"
)
async def error(
    request: Request, error_msg: str | None = Cookie(default=None)
) -> HTMLResponse:
    return templates.TemplateResponse(
        "error.html", {"request": request, "error_msg": error_msg}
    )


# Routes to user section
app.include_router(router)
