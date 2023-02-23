"""User Page"""
# import library
from datetime import datetime
from fastapi import (
    APIRouter,
    Cookie,
    Request,
    Depends,
    HTTPException,
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

# library from own
from excels import EmpSalary
from models.form import ExcelForm
from models.mongo import MongoDB
from models.jwt_token import Token

# router
from routes.user_add_emp import add_emp_router
from routes.user_all_emp import all_emp_router
from routes.user_single_emp import single_emp_router
from routes.user_delete_emp import delete_emp_router
from routes.user_salary import salary

user_mainpage = APIRouter()
templates = Jinja2Templates(directory="templates")

# work list mongodb connect
_db = MongoDB()

# token
_token = Token()

# normal get date now
_date_now = datetime.now()


# user main_page ------------------------------
@user_mainpage.get("/user", tags=["Emp mainpage"])
async def mainpage(
    request: Request,
    access_token: str | None = Cookie(default=None),
):
    """user mainpage"""

    try:
        get_token = _token.verify_access_token(access_token)
        return templates.TemplateResponse(
            "user.html",
            {
                "request": request,
                "date": _date_now,
                "title": get_token["name"],
                "db": _db.status(),
            },
        )
    except:
        raise HTTPException(status_code=404, detail="Not Found")


@user_mainpage.post(
    "/user", tags=["Emp mainpage"], response_class=HTMLResponse, include_in_schema=False
)
async def send_file(
    request: Request,
    access_token: str | None = Cookie(default=None),
    upload_file: ExcelForm = Depends(ExcelForm.excel_upload),
) -> _TemplateResponse:
    """user post section"""

    # send file to excels models to work
    try:
        get_token = _token.verify_access_token(access_token)
        emp_salary = EmpSalary(
            excel_file=upload_file.excel.file,
            db_collection=_token.cookie_2_dbname(get_token["name"]),
        )

        # check employee not in web
        emp_not_in_web = emp_salary.emp_not_in_web()
        msg_output = f"*Message: File upload complete"
    except Exception as err:
        emp_not_in_web = ""
        msg_output = f"*Error: {err}"

    return templates.TemplateResponse(
        "user.html",
        {
            "request": request,
            "date": _date_now,
            "emp_not_in_web": emp_not_in_web,
            "msg_output": msg_output,
        },
    )


user_mainpage.include_router(add_emp_router)
user_mainpage.include_router(all_emp_router)
user_mainpage.include_router(single_emp_router)
user_mainpage.include_router(delete_emp_router)
user_mainpage.include_router(salary)
