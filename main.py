"""
User after Login and user page
"""
from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Modules from own library
from modules.mongo import MongoDB
from modules.form import LoginForm, RegisterForm
from modules.password import Password
from routes.user import router
import docs_description as docs

# Setup
app = FastAPI(title="TBROS Worker", version=1.0, description=docs.description, openapi_tags=docs.tags_metadata)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# MongoDB
_mongo = MongoDB()

# Index----------------------------------------------------------------------
@app.get("/", tags=["mainpage"], response_class=HTMLResponse)
async def index(request: Request, response: Response) -> HTMLResponse:
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

@app.post("/", response_class=RedirectResponse, tags=["mainpage"])
async def index_post(request: Request, login: LoginForm = Depends(LoginForm.login)) -> RedirectResponse:
    """Get login data and check user does exist"""
    _pass = Password()
    check_users = _mongo.user_collection().find({})

    # Get data from form post section
    login_email = login.email
    login_password = login.password
    
    async for user in check_users:
        if login_email == user["email"]:
            password = _pass.check_password(login_password, user["password"])
            
            if password:
                title = user["company_name"]
                redirect_url = request.url_for("mainpage")
                response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
                response.set_cookie(key="company_name", value=title)
                return response
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
async def register(request: Request) -> HTMLResponse:
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
async def register_post(request: Request, register: RegisterForm = Depends(RegisterForm.register)) -> RedirectResponse:
    """Get register data to save on mongodb"""
    user_list = [user["email"] async for user in _mongo.user_collection().find({})]
    hash_password = Password().create_password(register.password)

    new_user = {
        "email": register.email,
        "password": hash_password,
        "company_name": register.company_name.title()
    }

    if register.email not in user_list:
        await _mongo.user_collection().insert_one(new_user)
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
@app.get("/logout", tags=["Mainpage"])
def logout(request: Request):
    """Logout"""
    redirect_url = request.url_for("index")
    response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="company_name")
    return response

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

# Routes to user section
app.include_router(router)