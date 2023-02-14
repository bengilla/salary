"""User Page"""
# import library
import pendulum
from datetime import datetime
from fastapi import (
    APIRouter,
    Cookie,
    Request,
    Depends,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from starlette.templating import _TemplateResponse

# library from own
from excels import EmpSalary
from models.form import CreateForm, EditForm, ExcelForm
from models.image import ImageConvert
from models.mongo import MongoDB

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# oauth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# work list mongodb connect
_DB = MongoDB()

# normal get date now
_date_now = datetime.now()


# user main_page ------------------------------
@router.get("/user", tags=["Emp mainpage"])
async def mainpage(
        request: Request,
        company_name: str | None = Cookie(default=None),
):
    """user mainpage"""

    return templates.TemplateResponse(
        "user.html",
        {
            "request": request,
            "date": _date_now,
            "title": company_name,
        },
    )


@router.post("/user", tags=["Emp mainpage"], response_class=HTMLResponse)
async def send_file(
    request: Request,
    company_name: str | None = Cookie(default=None),
    upload_file: ExcelForm = Depends(ExcelForm.excel_upload),
) -> _TemplateResponse:
    """user post section"""

    # get cookie
    db_collection_name = company_name.upper().replace(" ", "")

    try:
        # send file to excels models to work
        emp_salary = EmpSalary(excel_file=upload_file.excel.file, db_collection=db_collection_name)

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


# add employee info ------------------------------
@router.get("/add", tags=["Emp add employee"], response_class=HTMLResponse)
async def add_emp(
    request: Request,
    company_name: str | None = Cookie(default=None),
) -> _TemplateResponse:
    """add employee info page"""

    return templates.TemplateResponse(
        "add.html",
        {
            "request": request,
            "title": company_name,
        },
    )


@router.post("/add", tags=["Emp add employee"])
async def add_emp_post(
    request: Request,
    company_name: str | None = Cookie(default=None),
    add_emp_form: CreateForm = Depends(CreateForm.create),
) -> RedirectResponse:
    """post employee info to server"""

    # get cookie
    db_collection_name = company_name.upper().replace(" ", "")

    # Image concert and resize
    if add_emp_form.img_emp.filename:
        image_data = ImageConvert().img_base64(add_emp_form.img_emp.file)
    else:
        empty_image = "./static/images/no-data.jpg"
        image_data = ImageConvert().img_base64(empty_image)

    new_emp = {
        "_id": add_emp_form.name.replace(" ", "").lower(),
        "img_employee": image_data,
        "name": add_emp_form.name.title(),
        "pay_hour": add_emp_form.pay_hour,
        "ic": add_emp_form.ic,
        "dob": add_emp_form.dob,
        "nationality": add_emp_form.nationality,
        "gender": add_emp_form.gender,
        "contact": add_emp_form.contact,
        "address": add_emp_form.address,
        "sign_date": _date_now.date().strftime("%d-%m-%Y"),
    }

    _DB.emp_info_collection(db_collection_name).insert_one(new_emp)
    redirect_url = request.url_for("mainpage")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


# list all employee info ------------------------------
@router.get("/all", tags=["Emp all employee"], response_class=HTMLResponse)
async def all_emp(
    request: Request, company_name: str | None = Cookie(default=None)
) -> _TemplateResponse:
    """list all employee info"""

    # get cookie
    db_collection_name = company_name.upper().replace(" ", "")

    emp_info = _DB.emp_info_collection(db_collection_name)
    list_emp_info = emp_info.find({})

    list_emp_info = [emp for emp in list_emp_info.sort("_id", 1)]
    list_count = len(list_emp_info)

    return templates.TemplateResponse(
        "all.html",
        {
            "request": request,
            "info": list_emp_info,
            "count": list_count,
            "title": company_name,
        },
    )


# single employee info ------------------------------
@router.get("/info/{ids}", tags=["Emp single employee"])
async def info_emp(
    *, request: Request, company_name: str | None = Cookie(default=None), ids: str
):
    """show single employee info"""

    # get cookie
    db_collection_name = company_name.upper().replace(" ", "")

    emp_info = _DB.emp_info_collection(db_collection_name)
    single_emp = emp_info.find_one({"_id": ids})

    return templates.TemplateResponse(
        "emp.html",
        {
            "request": request,
            "info": single_emp,
            "emp_name": single_emp,
            "title": company_name,
        },
    )


# single employee edit ------------------------------
@router.get("/edit/{ids}", tags=["Emp edit employee"], response_class=HTMLResponse)
async def edit_emp(
    *, request: Request, company_name: str | None = Cookie(default=None), ids: str
) -> _TemplateResponse:
    """edit employee info"""

    # get cookie
    db_collection_name = company_name.upper().replace(" ", "")

    # Get Employee info
    emp_info = _DB.emp_info_collection(db_collection_name)
    single_emp = emp_info.find_one({"_id": ids})

    return templates.TemplateResponse(
        "edit.html", {"request": request, "edit_emp": single_emp, "title": company_name}
    )


@router.post("/edit/{ids}", tags=["Emp edit employee"], response_class=RedirectResponse)
async def edit_emp_post(
    *,
    request: Request,
    company_name: str | None = Cookie(default=None),
    edit_emp_form: EditForm = Depends(EditForm.edit),
    ids: str,
) -> RedirectResponse:
    """post edit employee info"""

    # get cookie
    db_collection_name = company_name.upper().replace(" ", "")

    # if send image
    if edit_emp_form.img_emp.filename:
        edit_emp_form = {
            "img_employee": ImageConvert().img_base64(edit_emp_form.img_emp.file),
            "pay_hour": edit_emp_form.pay_hour,
            "ic": edit_emp_form.ic,
            "contact": edit_emp_form.contact,
            "address": edit_emp_form.address,
        }
    # if NO image
    else:
        edit_emp_form = {
            "pay_hour": edit_emp_form.pay_hour,
            "ic": edit_emp_form.ic,
            "contact": edit_emp_form.contact,
            "address": edit_emp_form.address,
        }

    # update emp info
    _DB.emp_info_collection(db_collection_name).update_one(
        {"_id": ids}, {"$set": edit_emp_form}
    )

    redirect_url = request.url_for("all_emp")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


# delete employee ------------------------------
@router.get(
    "/delete/{ids}", tags=["Emp delete employee"], response_class=RedirectResponse
)
def delete_emp(
    *, request: Request, company_name: str | None = Cookie(default=None), ids: str
) -> RedirectResponse:
    """delete employee"""

    # get cookie
    db_collection_name = company_name.upper().replace(" ", "")

    # delete emp info
    _DB.emp_info_collection(db_collection_name).delete_one({"_id": ids})

    redirect_url = request.url_for("all_emp")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


# employee salary info ------------------------------
@router.get("/salary-list", tags=["Emp employee salary list"])
async def salary_list(
    *, request: Request, company_name: str | None = Cookie(default=None)
):
    """salary list select year section"""

    # get cookie
    db_collection_name = company_name.upper().replace(" ", "")

    year_collection = _DB.collection_name(db_collection_name)

    return templates.TemplateResponse(
        "salary-list.html",
        {
            "request": request,
            "date": _date_now,
            "title": company_name,
            "year_collection": year_collection,
        },
    )


@router.get("/all_list/{year}/{ids}", tags=["Emp employee salary list"])
async def all_list(
    *,
    request: Request,
    company_name: str | None = Cookie(default=None),
    ids: str,
    year: str,
):
    """list every month of employee salary 2"""

    # get cookie
    db_collection_name = company_name.upper().replace(" ", "")

    # drop down list
    def drop_down_list():
        date_list = _DB.collection_name(db_collection_name)
        for key, value in date_list.items():
            if key == year:
                return value

    # get single salary list
    work_hour_collection = _DB.emp_work_hour_collection(db_collection_name, year)

    salary_list = work_hour_collection.find_one({"date": ids})
    salary_output = salary_list["emp_work_hours"]
    sort_emp_dict = dict(sorted(salary_output.items()))

    # get total amounts
    total_amounts = salary_list["total_amounts"]
    total_cash = f"RM {total_amounts:,.2f}"

    # get month title
    output_month = salary_list["date"].split("-")[1]

    return templates.TemplateResponse(
        "list.html",
        {
            "request": request,
            "title": company_name,
            "emp": sort_emp_dict,
            "drop_down": drop_down_list(),
            "year": year,
            "month": output_month,
            "total_cash": total_cash,
            "total_emp_on_list": len(salary_output),
        },
    )
