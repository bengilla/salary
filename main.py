"""
User after Login and user page
"""

from fastapi import FastAPI, Request, Response, Depends, Cookie, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Modules from own library
from modules.mongo import MongoDB
from modules.form import LoginForm, RegisterForm
from modules.password import Password
from routes.user import router

description = """
TBROS Worker website to record all worker info and calcular every month salary
"""

tags_metadata = [
    {
        "name": "mainpage",
        "description": "mainpage for user who register to imput email and password"
    },
    {
        "name": "user",
        "description": "user after login"
    }
]

# Setup
app = FastAPI(title="TBROS Worker", version=1.0, description=description, openapi_tags=tags_metadata)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Routes to user section
app.include_router(router)

# MongoDB
_mongo = MongoDB()

# Index----------------------------------------------------------------------
@app.get("/", tags=["mainpage"], response_class=HTMLResponse)
async def index(request: Request, response: Response) -> Response:
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

@app.post("/", tags=["mainpage"])
async def index_post(request: Request, response: Response, login_data: LoginForm = Depends(LoginForm.login)) -> dict:
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
                redirect_url = request.url_for("mainpage")
                return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
            else:
                raise HTTPException(
                    status_code=422,
                    detail="Password not correct",
                    headers={"X-Error": "Password no correct!"}
                )
                # redirect_url = request.url_for("error")
                # return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

    raise HTTPException(
        status_code=422,
        detail="User doesn't exists",
        headers={"X-Error": "User doesn't exists!"}
    )

# Register----------------------------------------------------------------------
@app.get("/register", tags=["mainpage"], response_class=HTMLResponse)
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

@app.post("/register", tags=["mainpage"])
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

# # Logout----------------------------------------------------------------------
# @app.get("/logout", tags=["Mainpage"])
# def logout(request: Request):
#     """Logout"""
#     redirect_url = request.url_for(us.mainpage)
#     response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
#     response.delete_cookie(key="company_name")
#     return response

# # Error----------------------------------------------------------------------
@app.get("/error", tags=["mainpage"], response_class=HTMLResponse)
def error(request: Request):
    """Error"""
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request
        }
    )