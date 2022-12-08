"""
User Section
"""
from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for

# Library from own
from emp import EmpInfo
from excels import EmpSalary
from modules.cookie import Cookie
from modules.form import CreateForm, EditForm
from modules.mongo import MongoDB

user = Blueprint("user", __name__)

# # Work List MongoDB connect
_mongodb = MongoDB()

# Normal get date now
_date_now = datetime.now()

# Cookie
_cookie = Cookie()


@user.route("/user", methods=["GET", "POST"])
def mainpage():
    """
    链接至 index.html, 同时也输出日期
    """
    # Get cookie
    title = _cookie.get_cookie("userID")

    # Get ID from list from data
    get_mongo = _mongodb.work_hour_collection()
    find_all_id = get_mongo.find({})
    all_id = [x["_id"] for x in find_all_id]

    err_title = ""
    not_register_emp = ""
    err_exception_msg = ""

    if request.method == "POST":
        file_input = request.files["file"]
        try:
            emp_salary = EmpSalary(file_input)
            if len(emp_salary.find_no_emp()) == 0:
                return render_template("complete.html")
            else:
                err_title = "This all members not in website:"
                not_register_emp = emp_salary.find_no_emp()
        except Exception as err:  # pylint: disable=W0703
            err_title = "You have error message:"
            err_exception_msg = err

    return render_template(
        "user.html",
        date=_date_now,
        title=title,
        all_id=all_id,
        err_title=err_title,
        err_emp=not_register_emp,
        err_exception_msg=err_exception_msg,
    )


@user.route("/add", methods=["GET", "POST"])
def add_emp():
    """
    建立员工资料，如果员工已存在就会显示 error
    如果建立成功转至 all.html
    """
    _empinfo = EmpInfo()
    title = _cookie.get_cookie("userID")

    form = CreateForm()
    error = ""

    if request.method == "POST":
        create_emp = _empinfo.emp_create()
        if create_emp:
            return redirect("/all")
        else:
            error = "Employee Exists"

    return render_template("add.html", form=form, title=title, error=error)


@user.route("/all")
def all_emp():
    """
    浏览全部员工
    """
    _empinfo = EmpInfo()
    title = _cookie.get_cookie("userID")

    count = 0
    for _ in _empinfo.emp_info():
        count += 1

    info_from_db = _empinfo.emp_info()
    info = info_from_db.sort("_id", 1)

    return render_template("all.html", info=info, count=count, title=title)


@user.route("/info/<ids>")
def info_emp(ids: str):
    """
    浏览单位员工
    """
    _empinfo = EmpInfo()
    title = _cookie.get_cookie("userID")

    info = _empinfo.emp_one(ids)
    emp_name = info["name"]
    return render_template("emp.html", info=info, emp_name=emp_name, title=title)


@user.route("/edit/<ids>", methods=["GET", "POST"])
def edit_emp(ids: str):
    """
    修改员工资料, 只是修改 ic, contact, address, pay
    """
    _empinfo = EmpInfo()
    title = _cookie.get_cookie("userID")

    form = EditForm()
    get_emp = _empinfo.emp_one(ids)

    if request.method == "POST":
        img_employee = form.img_employee.data
        ic_card = form.ic.data
        contact = form.contact.data
        address = form.address.data
        pay = form.pay_hour.data

        _empinfo.emp_edit(ids, ic_card, contact, address, pay, img_employee)

        return redirect(url_for("user.all_emp"))
    return render_template("edit.html", form=form, edit_emp=get_emp, title=title)


@user.route("/delete/<ids>")
def delete_emp(ids: str):
    """
    删除员工资料
    """
    _empinfo = EmpInfo()
    _empinfo.emp_delete(ids)
    return redirect(url_for("user.all_emp"))


@user.route("/all_list/<ids>", methods=["GET"])
def all_list(ids: str):
    """
    当月发工资列表
    """
    title = _cookie.get_cookie("userID")

    emp_one = _mongodb.work_hour_collection().find_one({"_id": ids})  # 寻找月份工人列表
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
    all_documents = _mongodb.work_hour_collection().find({})
    document_id = [x["_id"] for x in all_documents]

    return render_template(
        "list.html",
        title=title,
        emp=sort_emp_dict,
        document_id=document_id,
        output_id=output_month,
        total_cash=total_cash,
        total_emp_on_list=total_emp_on_list,
    )


@user.errorhandler(404)
def page_not_found(e):
    """Page Not Found"""
    title = _cookie.get_cookie("userID")
    return render_template("404.html", title=title), 404


@user.errorhandler(AttributeError)
def not_login(e):
    """Not Login"""
    return render_template("attrerror.html")
