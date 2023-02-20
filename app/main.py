"""User Login and Register Page"""
from config.settings import settings

# import library
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.templating import _TemplateResponse

# models from own library
from models.mongo import MongoDB
from models.form import LoginForm, RegisterForm
from models.password import Password

# router
from routes.user_mainpage import user_mainpage
from models.jwt_token import Token

# setup
app = FastAPI(title="TBROS Worker", version="1.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# password hash and verify class
_pass = Password()

# mongoDB
_db = MongoDB()

# token
_token = Token()


# error handle
@app.exception_handler(StarletteHTTPException)
async def my_exception_handler(request: Request, exc):
    """error handle"""

    return templates.TemplateResponse(
        "error/error.html",
        {"request": request, "status_code": exc.status_code, "error": exc.detail},
    )


def get_user_data(email: str):
    user_list = _db.user_collection().find({})
    for user in user_list:
        if email in user["email"]:
            return RegisterForm(**user)


# db modify ----------------------------------------------------------------------
# total = 0
# data = _DB.emp_work_hour_collection(db_title="TBROSVENTURESSDNBHD", db_year="2023")
# find_data = data.find_one({"date": "16-Jan-2023"})
# look_emp = find_data["emp_work_hours"]
# for name in look_emp:
#     total += look_emp[name]["total_salary"]
# print(total)
# db modify ----------------------------------------------------------------------


# index----------------------------------------------------------------------
@app.get("/", tags=["User Login"], response_class=HTMLResponse)
async def index(request: Request) -> _TemplateResponse:
    """index page"""

    response = templates.TemplateResponse(
        "index.html", {"request": request, "title": settings.LOGIN_TITLE}
    )
    response.delete_cookie(key="access_token")
    return response


@app.post("/", tags=["User Login"], response_class=RedirectResponse)
async def index(
    request: Request,
    login: LoginForm = Depends(LoginForm.login),
):
    """index post section"""

    user_in_db = get_user_data(login.email)

    if user_in_db:
        if _pass.verify_password(login.password, user_in_db.password):
            title = user_in_db.company_name

            # token create
            access_token = _token.create_access_token(title)

            # response
            redirect_url = request.url_for("mainpage")
            response = RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
            response.set_cookie(
                key="access_token", value=f"{access_token}", httponly=True, secure=True
            )
            return response
        else:
            raise HTTPException(status_code=401, detail="Invalid username or password")
    else:
        raise HTTPException(
            status_code=404, detail="User doesn't exist, please register"
        )


# register----------------------------------------------------------------------
@app.get("/register", tags=["User Register"], response_class=HTMLResponse)
async def register(request: Request) -> _TemplateResponse:
    """register page"""

    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "title": settings.REGISTER_TITLE,
        },
    )


@app.post("/register", tags=["User Register"])
async def register(
    request: Request, register_info: RegisterForm = Depends(RegisterForm.register)
) -> RedirectResponse:
    """register post section"""

    user_list = [user["email"] for user in _db.user_collection().find({})]

    new_user = {
        "email": register_info.email,
        "password": _pass.get_password_hash(register_info.password),
        "company_name": register_info.company_name,
    }

    if register_info.email not in user_list:
        _db.user_collection().insert_one(new_user)
        redirect_url = request.url_for("index")
        return RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
    else:
        raise HTTPException(
            status_code=401, detail="User is exists, please use other email"
        )


# logout----------------------------------------------------------------------
@app.get("/logout", tags=["User Logout"])
async def logout(request: Request):
    """logout section"""

    redirect_url = request.url_for("index")
    response = RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response


# routes to user section
app.include_router(user_mainpage)