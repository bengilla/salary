"""
User Section
"""
import os
from datetime import datetime
from fastapi import APIRouter, Cookie, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# Library from own
from emp import EmpInfo
from excels import EmpSalary
from modules.form import CreateForm, EditForm
from modules.mongo import MongoDB

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# # Work List MongoDB connect
_mongodb = MongoDB()

# Normal get date now
_date_now = datetime.now()

@router.get("/user", tags=["user"])
async def mainpage(request: Request, company_name: str | None = Cookie(default=None)):
    """
    链接至 index.html, 同时也输出日期
    """
    # Get cookie
    title = company_name
    db_title = title.upper().replace(" ", "")

    get_mongo = _mongodb.work_hour_collection(db_title)
    find_all_id = get_mongo.find({})
    all_id = [x["_id"] async for x in find_all_id]


    return templates.TemplateResponse(
        "user.html", 
        {
            "request": request,
            "date": _date_now,
            "title": title,
            "all_id": all_id,
            # "err_title"=err_title,
            # "err_emp"=not_register_emp,
            # "err_exception_msg"=err_exception_msg,
        }
    )

@router.post("/user")
async def mainpage_sendfile():
    # Get ID from list from data
    # get_mongo = _mongodb.work_hour_collection(db_title)
    # find_all_id = get_mongo.find({})
    # all_id = [x["_id"] async for x in find_all_id]

    # if request.method == "POST":
    #     file_input = request.files["file"]
    #     try:
    #         emp_salary = EmpSalary(filename=file_input, db_title=db_title)
    #         if len(emp_salary.find_no_emp()) == 0:
    #             return render_template("complete.html")
    #         else:
    #             err_title = "This all members not in website:"
    #             not_register_emp = emp_salary.find_no_emp()
    #     except Exception as err:  # pylint: disable=W0703
    #         err_title = "You have error message:"
    #         err_exception_msg = err
    pass



@router.get("/add")
async def add_emp(request: Request, company_name: str | None = Cookie(default=None)):
    """
    建立员工资料，如果员工已存在就会显示 error
    如果建立成功转至 all.html
    """
    title = company_name
    db_title = title.upper().replace(" ", "")
    _empinfo = EmpInfo(db_title)

    form = CreateForm()
    error = ""

    if form.validate_on_submit():
        create_emp = _empinfo.emp_create()
        if create_emp:
            redirect_url = request.url_for("all_emp")
            response = RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
            return response
        else:
            error = "Employee Exists"

    return templates.TemplateResponse(
        "add.html",
        {
            "request": request,
            "form": form,
            "title": title,
            "error": error
        }
        )


@router.get("/all")
async def all_emp(request: Request, company_name: str | None = Cookie(default=None)):
    """
    浏览全部员工
    """
    title = company_name
    db_title = title.upper().replace(" ", "")
    _empinfo = EmpInfo(db_title)

    count = 0
    for _ in _empinfo.emp_info():
        count += 1

    info_from_db = _empinfo.emp_info()
    info = info_from_db.sort("_id", 1)

    return templates.TemplateResponse(
        "all.html",
         { 
            "info": info,
            "count": count,
            "title": title
        }
        )


@router.get("/info/{ids}")
async def info_emp(ids: str, request: Request, company_name: str | None = Cookie(default=None)):
    """
    浏览单位员工
    """
    title = company_name
    db_title = title.upper().replace(" ", "")
    _empinfo = EmpInfo(db_title)

    info = _empinfo.emp_one(ids)
    emp_name = info["name"]
    return templates.TemplateResponse(
        "emp.html",
        {
            "request": request,
            "info": info,
            "emp_name": emp_name,
            "title": title
        }
    )


# @user.route("/edit/<ids>", methods=["GET", "POST"])
# def edit_emp(ids: str):
#     """
#     修改员工资料, 只是修改 ic, contact, address, pay
#     """
#     title = _cookie.get_cookie("userID")
#     db_title = title.upper().replace(" ", "")
#     _empinfo = EmpInfo(db_title)

#     form = EditForm()
#     get_emp = _empinfo.emp_one(ids)

#     if form.validate_on_submit():
#         img_employee = form.img_employee.data
#         ic_card = form.ic.data
#         contact = form.contact.data
#         address = form.address.data
#         pay = form.pay_hour.data

#         _empinfo.emp_edit(ids, ic_card, contact, address, pay, img_employee)

#         return redirect(url_for("user.all_emp"))
#     return render_template("edit.html", form=form, edit_emp=get_emp, title=title)


# @user.route("/delete/<ids>")
# def delete_emp(ids: str):
#     """
#     删除员工资料
#     """
#     title = _cookie.get_cookie("userID")
#     db_title = title.upper().replace(" ", "")
#     _empinfo = EmpInfo(db_title)
    
#     _empinfo.emp_delete(ids)
#     return redirect(url_for("user.all_emp"))


@router.get("/all_list", response_class=HTMLResponse)
def all_list(ids: str, request: Request, company_name: str | None = Cookie(default=None)):
    """
    当月发工资列表
    """
    title = company_name
    db_title = title.upper().replace(" ", "")

    emp_one = _mongodb.work_hour_collection(db_title).find_one({"_id": ids})  # 寻找月份工人列表
    emp_output = emp_one["emp_work_hours"]
    sort_emp_dict = dict(sorted(emp_output.items()))

    # 呈现所有员工总数工资
    salary = []
    for _, value in emp_output.items():
        output_value = value
        salary.append(output_value["total_salary"])

    # 名单总数
    total_emp_on_list = len(emp_output)

    # 工资总数
    total_cash = f"RM {sum(salary):,.2f}"

    # 取文件月份
    output_month = ids.split(" ")[0]

    # 所有mongoDB资料
    all_documents = _mongodb.work_hour_collection(db_title).find({})
    document_id = [x["_id"] for x in all_documents]

    return templates.TemplateResponse(
        "list.html",
        {
            "request": request,
            "title": title,
            "emp": sort_emp_dict,
            "document_id": document_id,
            "output_id": output_month,
            "total_cash": total_cash,
            "total_emp_on_list": total_emp_on_list,
        }
    )