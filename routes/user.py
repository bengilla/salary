"""
User After Login Page
"""
import pendulum
from datetime import datetime
from fastapi import (
    APIRouter,
    Cookie,
    Request,
    Depends,
    File,
    UploadFile,
    HTTPException,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# Library from own
from excels import EmpSalary
from models.form import CreateForm, EditForm
from models.image import ImageConvert
from models.mongo import MongoDB

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# # Work List MongoDB connect
_mongodb = MongoDB()

# Normal get date now
_date_now = datetime.now()


# User mainpae ------------------------------
@router.get("/user", tags=["Emp mainpage"])
async def mainpage(request: Request, company_name: str | None = Cookie(default=None)):
    """User mainpage"""

    return templates.TemplateResponse(
        "user.html",
        {
            "request": request,
            "date": _date_now,
            "title": company_name,
        },
    )


@router.post("/user", tags=["Emp mainpage"], response_class=HTMLResponse)
async def sendfile(
    request: Request,
    company_name: str | None = Cookie(default=None),
    excels: UploadFile = File(None),
) -> HTMLResponse:
    # get cookie
    db_collection = company_name.upper().replace(" ", "")

    # send file to excels models to work
    emp_salary = EmpSalary(file=excels, db_collection=db_collection)

    # main function run
    emp_salary.main()

    try:
        if len(emp_salary.emp_not_in_web()) == 0:
            return templates.TemplateResponse("complete.html", {"request": request})
        else:
            err_title = "This all members not in website"
            not_register_emp = emp_salary.emp_not_in_web()
    except Exception as err:
        err_title = "You have error message:"
        err_exception_msg = err

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "date": _date_now,
            "err_title": err_title,
            "err_emp": not_register_emp,
            # "err_exception_msg": err_exception_msg,
        },
    )


# Add Employee Info ------------------------------
@router.get("/add", tags=["Emp add employee"], response_class=HTMLResponse)
async def add_emp(
    request: Request,
    company_name: str | None = Cookie(default=None),
) -> HTMLResponse:
    """Add Employee info page"""

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
    add_emp: CreateForm = Depends(CreateForm.create),
) -> RedirectResponse:
    """Post Employee info to server"""

    # get cookie
    db_collection = company_name.upper().replace(" ", "")

    # Image concert and resize
    if add_emp.img_emp.filename:
        image_data = ImageConvert().img_base64(add_emp.img_emp.file)
    else:
        empty_image = "./static/images/no-data.jpg"
        image_data = ImageConvert().img_base64(empty_image)

    new_emp = {
        "_id": add_emp.name.replace(" ", "").lower(),
        "img_employee": image_data,
        "name": add_emp.name.title(),
        "pay_hour": add_emp.pay_hour,
        "ic": add_emp.ic,
        "dob": add_emp.dob,
        "nationality": add_emp.nationality,
        "gender": add_emp.gender,
        "contact": add_emp.contact,
        "address": add_emp.address,
        "sign_date": _date_now.date().strftime("%d-%m-%Y"),
    }

    _mongodb.emp_info_collection(db_collection).insert_one(new_emp)
    redirect_url = request.url_for("mainpage")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


# List all Employee Info ------------------------------
@router.get("/all", tags=["Emp all employee"], response_class=HTMLResponse)
async def all_emp(
    request: Request, company_name: str | None = Cookie(default=None)
) -> HTMLResponse:
    """List all Employee info"""

    # get cookie
    db_collection = company_name.upper().replace(" ", "")

    empinfo = _mongodb.emp_info_collection(db_collection)
    list_empinfo = empinfo.find({})

    list_empinfo = [i for i in list_empinfo.sort("_id", 1)]
    list_count = len(list_empinfo)

    return templates.TemplateResponse(
        "all.html",
        {
            "request": request,
            "info": list_empinfo,
            "count": list_count,
            "title": company_name,
        },
    )


# Single employee info ------------------------------
@router.get("/info/{id}", tags=["Emp single employee"])
async def info_emp(
    *, request: Request, company_name: str | None = Cookie(default=None), id: str
):
    """Show single Employee info"""

    # get cookie
    db_collection = company_name.upper().replace(" ", "")

    empinfo = _mongodb.emp_info_collection(db_collection)
    single_emp = empinfo.find_one({"_id": id})

    return templates.TemplateResponse(
        "emp.html",
        {
            "request": request,
            "info": single_emp,
            "emp_name": single_emp,
            "title": company_name,
        },
    )


# Single employee EDIT ------------------------------
@router.get("/edit/{id}", tags=["Emp edit employee"], response_class=HTMLResponse)
async def edit_emp(
    *, request: Request, company_name: str | None = Cookie(default=None), id: str
) -> HTMLResponse:
    """Edit Employee info"""

    # get cookie
    db_collection = company_name.upper().replace(" ", "")

    # Get Employee info
    empinfo = _mongodb.emp_info_collection(db_collection)
    single_emp = empinfo.find_one({"_id": id})

    return templates.TemplateResponse(
        "edit.html", {"request": request, "edit_emp": single_emp, "title": company_name}
    )


@router.post("/edit/{id}", tags=["Emp edit employee"], response_class=RedirectResponse)
async def edit_emp_post(
    *,
    request: Request,
    company_name: str | None = Cookie(default=None),
    edit_emp: EditForm = Depends(EditForm.edit),
    id: str,
) -> RedirectResponse:
    """Post edit Employee info"""

    # get cookie
    db_collection = company_name.upper().replace(" ", "")

    # if send image
    if edit_emp.img_emp.filename:
        edit_emp = {
            "img_employee": ImageConvert().img_base64(edit_emp.img_emp.file),
            "pay_hour": edit_emp.pay_hour,
            "ic": edit_emp.ic,
            "contact": edit_emp.contact,
            "address": edit_emp.address,
        }
    # if NO image
    else:
        edit_emp = {
            "pay_hour": edit_emp.pay_hour,
            "ic": edit_emp.ic,
            "contact": edit_emp.contact,
            "address": edit_emp.address,
        }

    # update emp info
    _mongodb.emp_info_collection(db_collection).update_one(
        {"_id": id}, {"$set": edit_emp}
    )

    redirect_url = request.url_for("all_emp")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


# Delete employee ------------------------------
@router.get(
    "/delete/{id}", tags=["Emp delete employee"], response_class=RedirectResponse
)
def delete_emp(
    *, request: Request, company_name: str | None = Cookie(default=None), id: str
) -> RedirectResponse:
    """Delete Employee"""

    # get cookie
    db_collection = company_name.upper().replace(" ", "")

    # delete emp info
    _mongodb.emp_info_collection(db_collection).delete_one({"_id": id})

    redirect_url = request.url_for("all_emp")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


# Employee salary info ------------------------------
@router.get("/salarymenu", tags=["Emp employee salary list"])
async def salary_menu(
    *, request: Request, company_name: str | None = Cookie(default=None)
):
    # get cookie
    db_collection_name = company_name.upper().replace(" ", "")

    # get own company year collection and save to list
    db_list_collection = _mongodb.user_data.list_collection_names()
    year_collection = []
    for x in db_list_collection:
        get_str = x.split("-")
        if get_str[0] == db_collection_name and get_str[1].isnumeric():
            year_collection.append(get_str[1])

    return templates.TemplateResponse(
        "salarymenu.html",
        {
            "request": request,
            "date": _date_now,
            "title": company_name,
            "year_collection": year_collection,
        },
    )


@router.get("/all_list/{year}", tags=["Emp employee salary list"])
async def all_list(
    *,
    request: Request,
    company_name: str | None = Cookie(default=None),
    year: str,
):
    # get cookie
    db_collection = company_name.upper().replace(" ", "")

    # all salary list
    work_hour_collection = _mongodb.emp_work_hour_collection(db_collection, year)
    work_hour_list = [list["date"] for list in work_hour_collection.find({})]

    # get single salary list
    salary_list = work_hour_collection.find_one({"date": work_hour_list[-1]})
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
            "drop_down": work_hour_list,
            "year": year,
            "month": output_month,
            "total_cash": total_cash,
            "total_emp_on_list": len(salary_output),
        },
    )


@router.get("/all_list/{year}/{id}", tags=["Emp employee salary list"])
async def all_list(
    *,
    request: Request,
    company_name: str | None = Cookie(default=None),
    id: str,
    year: str,
):
    # get cookie
    db_collection = company_name.upper().replace(" ", "")

    # all salary list
    work_hour_collection = _mongodb.emp_work_hour_collection(db_collection, year)
    work_hour_list = [list["date"] for list in work_hour_collection.find({})]

    # get single salary list
    salary_list = work_hour_collection.find_one({"date": id})
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
            "drop_down": work_hour_list,
            "year": year,
            "month": output_month,
            "total_cash": total_cash,
            "total_emp_on_list": len(salary_output),
        },
    )
