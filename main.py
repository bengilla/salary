"""User Login and Register Page"""
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
from routes.user import router

# token
from datetime import timedelta

# setup
app = FastAPI(title="TBROS Worker", version="1.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# password hash and verify class
_pass = Password()

# mongoDB
_DB = MongoDB()

# error handle
@app.exception_handler(StarletteHTTPException)
async def my_exception_handler(request: Request, exc):
    """error handle"""

    return templates.TemplateResponse(
        "error/error.html",
        {"request": request, "status_code": exc.status_code, "error": exc.detail},
    )

def get_user_data(email: str):
    user_list = _DB.user_collection().find({})
    for user in user_list:
        if email in user['email']:
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
@app.get(
    "/", tags=["User Login"], response_class=HTMLResponse, description="User login page"
)
async def index(request: Request) -> _TemplateResponse:
    """index page"""

    title = "Employee work system - Login"

    response = templates.TemplateResponse(
        "index.html", {"request": request, "title": title}
    )
    response.delete_cookie(key="company_name")
    return response


@app.post(
    "/",
    tags=["User Login"],
    response_class=RedirectResponse,
    description="User post login data",
)
async def index_post(
    request: Request, login: LoginForm = Depends(LoginForm.login),
):
    """index post section"""

    user_in_db = get_user_data(login.email)

    if user_in_db:
        if _pass.verify_password(login.password, user_in_db.password):
            title = user_in_db.company_name

            # response
            redirect_url = request.url_for("mainpage")
            response = RedirectResponse(
                redirect_url, status_code=status.HTTP_302_FOUND
            )
            response.set_cookie(key="company_name", value=title)
            return response
        else:
            raise HTTPException(status_code=401, detail="Invalid username or password")
    else:
        raise HTTPException(status_code=404, detail="User doesn't exist, please register")

# register----------------------------------------------------------------------
@app.get(
    "/register",
    tags=["User Register"],
    response_class=HTMLResponse,
    description="Register page",
)
async def register(request: Request) -> _TemplateResponse:
    """register page"""

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
    request: Request, register_info: RegisterForm = Depends(RegisterForm.register)
) -> RedirectResponse:
    """register post section"""

    user_list = [user["email"] for user in _DB.user_collection().find({})]

    new_user = {
        "email": register_info.email,
        "password": _pass.get_password_hash(register_info.password),
        "company_name": register_info.company_name,
    }

    if register_info.email not in user_list:
        _DB.user_collection().insert_one(new_user)
        redirect_url = request.url_for("index")
        return RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
    else:
        raise HTTPException(
            status_code=401, detail="User is exists, please use other email"
        )


# logout----------------------------------------------------------------------
@app.get("/logout", tags=["User Logout"], description="Logout user")
async def logout(request: Request):
    """logout section"""

    redirect_url = request.url_for("index")
    response = RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="company_name")
    return response


# routes to user section
app.include_router(router)
