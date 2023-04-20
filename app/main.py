"""User Login and Register Page"""

# import library
from fastapi import FastAPI, Request, Depends, HTTPException, Cookie, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.templating import _TemplateResponse

# models from own library
from config.settings import settings
from models.mongo import MongoDB
from models.form import LoginForm, RegisterForm, RegisterFormWithCode
from models.password import Password
from models.jwt_token import Token

# router
from routes.user_mainpage import user_mainpage

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
    """错误功能"""

    return templates.TemplateResponse(
        "error/error.html",
        {"request": request, "status_code": exc.status_code, "error": exc.detail},
    )


# index----------------------------------------------------------------------
@app.get("/", tags=["User Login"], response_class=HTMLResponse)
async def index(
    request: Request, access_token: str | None = Cookie(default=None)
) -> _TemplateResponse:
    """主页"""

    if access_token:
        get_token = _token.verify_access_token(access_token)
        if get_token:
            redirect_url = request.url_for("mainpage")
            return RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": settings.LOGIN_TITLE, "db": _db.status()},
    )


@app.post("/", tags=["User Login"], response_class=RedirectResponse)
async def index_post(
    request: Request,
    login: LoginForm = Depends(LoginForm.login),
):
    """主页POST"""

    def get_user_data(email: str):
        user_list = _db.user_collection().find({})
        for user in user_list:  # dict
            if email in user["email"]:
                return RegisterForm(**user)
            return None

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
        raise HTTPException(status_code=400, detail="Invalid username or password")
    raise HTTPException(
        status_code=404, detail="User does not exist, please register a new user"
    )


# register----------------------------------------------------------------------
@app.get("/register", tags=["User Register"], response_class=HTMLResponse)
async def register(request: Request) -> _TemplateResponse:
    """注册页"""

    return templates.TemplateResponse(
        "register.html",
        {"request": request, "title": settings.REGISTER_TITLE, "db": _db.status()},
    )


@app.post("/register", tags=["User Register"])
async def register_post(
    request: Request,
    register_info: RegisterForm = Depends(RegisterFormWithCode.register),
) -> RedirectResponse:
    """注册页POST"""

    def get_code() -> list:
        code_list = []
        for i in _db.verify_code().find({}):
            code_list.append(i["code"])
        return code_list

    # get all verify code from server
    verify_code = get_code()

    user_list = [user["email"] for user in _db.user_collection().find({})]

    if register_info.code in verify_code:
        new_user = {
            "email": register_info.email,
            "password": _pass.get_password_hash(register_info.password),
            "company_name": register_info.company_name,
        }

        if register_info.email not in user_list:
            company_name = register_info.company_name.replace(" ", "").lower()
            if company_name not in _db.collection_list():
                _db.user_collection().insert_one(new_user)

                # delete temporary code for database
                get_code = _db.verify_code().find_one({"code": register_info.code})
                _db.verify_code().delete_one({"_id": get_code["_id"]})

                redirect_url = request.url_for("index")
                return RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
            raise HTTPException(
                status_code=400, detail="Company name is already exists"
            )
        raise HTTPException(
            status_code=400,
            detail="Email is already exists!",
        )
    raise HTTPException(status_code=400, detail="Verify code is invalid")


# logout----------------------------------------------------------------------
@app.get("/logout", tags=["User Logout"])
async def logout(request: Request):
    """退出页"""

    redirect_url = request.url_for("index")
    response = RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token", path="/", domain=None)
    return response


# routes to user section
app.include_router(user_mainpage)
