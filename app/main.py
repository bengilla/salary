"""User Login and Register Page"""
from config.settings import settings

# import library
from fastapi import FastAPI, Request, Depends, HTTPException, Cookie, status
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
_db = MongoDB("TEST")

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
async def index(
    request: Request, access_token: str | None = Cookie(default=None)
) -> _TemplateResponse:
    """index page"""
    print(_db.collection_list())

    try:
        get_token = _token.verify_access_token(access_token)
        if get_token:
            redirect_url = request.url_for("mainpage")
            return RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
    except:
        response = templates.TemplateResponse(
            "index.html",
            {"request": request, "title": settings.LOGIN_TITLE, "db": _db.status()},
        )
        return response


@app.post("/", tags=["User Login"], response_class=RedirectResponse)
async def index(
    request: Request,
    login: LoginForm = Depends(LoginForm.login),
):
    """index post section"""

    def get_user_data(email: str):
        user_list = _db.user_collection().find({})
        for user in user_list:
            if email in user["email"]:
                return RegisterForm(**user)

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
                key="access_token", value=f"{access_token}", httponly=True
            )
            return response
        else:
            raise HTTPException(status_code=400, detail="Invalid username or password")
    else:
        raise HTTPException(
            status_code=404, detail="User does not exist, please register a new user"
        )


# register----------------------------------------------------------------------
@app.get("/register", tags=["User Register"], response_class=HTMLResponse)
async def register(request: Request) -> _TemplateResponse:
    """register page"""

    return templates.TemplateResponse(
        "register.html",
        {"request": request, "title": settings.REGISTER_TITLE, "db": _db.status()},
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
        company_name = register_info.company_name.replace(" ", "").lower()
        if company_name not in _db.collection_list():
            _db.user_collection().insert_one(new_user)
            redirect_url = request.url_for("index")
            return RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
        else:
            raise HTTPException(
                status_code=400, detail="Company name is already exists"
            )
    else:
        raise HTTPException(
            status_code=400,
            detail="Email is already exists!",
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
