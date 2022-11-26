"""
Project for TBROS employees salary calculator and employee person info
"""

from datetime import datetime

from flask import (Flask, make_response, redirect, render_template, request,
                   url_for)

# Library from own
from emp.emp_mongodb import EmpInfo
from excels import EmpSalary
from modules.form import CreateForm, EditForm, LoginForm, RegisterForm
from modules.pass_check import Password
from mongodb import MongoDB

# 设置
app = Flask(__name__)
app.config["SECRET_KEY"] = "tbrosventures"

# Work List MongoDB connect
_work_list_db = MongoDB().work_hour_collection()
_members = MongoDB().user_collection()

# Get Emp info from MongoDB
_empinfo = EmpInfo()

# Normal get date now
_date_now = datetime.now()

# Password
_pass = Password()


@app.route("/", methods=["GET", "POST"])
def index():
    """
    链接至 index.html, 同时也输出日期
    """
    # Get ID from list from data
    find_all_id = _work_list_db.find({})
    all_id = [x["_id"] for x in find_all_id]
    err_title = ""
    not_register_emp = ""
    err_exception_msg = ""

    if request.method == "POST":
        file_input = request.files["file"]
        try:
            emp_salary = EmpSalary(file_input)
            if len(emp_salary.not_register) == 0:  # pylint: disable=E1101
                return render_template("complete.html")
            else:
                err_title = "This all members not in website:"
                not_register_emp = emp_salary.not_register  # pylint: disable=E1101
        except Exception as err:  # pylint: disable=W0703
            err_title = "You have error message:"
            err_exception_msg = err

    return render_template(
        "index.html",
        date=_date_now,
        all_id=all_id,
        err_title=err_title,
        err_emp=not_register_emp,
        err_exception_msg=err_exception_msg,
    )

@app.route("/user", methods=["GET", "POST"])
def user():
    """
    链接至 index.html, 同时也输出日期
    """
    # Get ID from list from data
    find_all_id = _work_list_db.find({})
    all_id = [x["_id"] for x in find_all_id]
    err_title = ""
    not_register_emp = ""
    err_exception_msg = ""

    if request.method == "POST":
        file_input = request.files["file"]
        try:
            emp_salary = EmpSalary(file_input)
            if len(emp_salary.not_register) == 0:  # pylint: disable=E1101
                return render_template("complete.html")
            else:
                err_title = "This all members not in website:"
                not_register_emp = emp_salary.not_register  # pylint: disable=E1101
        except Exception as err:  # pylint: disable=W0703
            err_title = "You have error message:"
            err_exception_msg = err

    return render_template(
        "user.html",
        date=_date_now,
        all_id=all_id,
        err_title=err_title,
        err_emp=not_register_emp,
        err_exception_msg=err_exception_msg,
    )

@app.route("/add", methods=["GET", "POST"])
def add_emp():
    """
    建立员工资料，如果员工已存在就会显示 msg
    如果建立成功转至 all.html
    form = form.py
    """
    form = CreateForm()
    msg = ""
    if request.method == "POST":
        create_emp = _empinfo.emp_create()
        if create_emp:
            return redirect("/all")
        else:
            msg = "Employee Exists"

    return render_template("add.html", form=form, msg=msg)


@app.route("/all")
def all_emp():
    """浏览全部员工"""
    count = 0
    for _ in _empinfo.emp_info():
        count += 1

    info_from_db = _empinfo.emp_info()
    info = info_from_db.sort("_id", 1)

    return render_template("all.html", info=info, count=count)


@app.route("/info/<ids>")
def info_emp(ids: str):
    """浏览单位员工"""
    info = _empinfo.emp_one(ids)
    emp_name = info["name"]
    return render_template("emp.html", info=info, emp_name=emp_name)


@app.route("/edit/<ids>", methods=["GET", "POST"])
def edit_emp(ids: str):
    """修改员工资料, 只是修改 ic, contact, address, pay"""
    form = EditForm()
    get_emp = _empinfo.emp_one(ids)

    if request.method == "POST":
        img_employee = form.img_employee.data
        ic_card = form.ic.data
        contact = form.contact.data
        address = form.address.data
        pay = form.pay_hour.data

        _empinfo.emp_edit(ids, ic_card, contact, address, pay, img_employee)

        return redirect(url_for("all_emp"))
    return render_template("edit.html", form=form, edit_emp=get_emp)


@app.route("/delete/<ids>")
def delete_emp(ids: str):
    """删除员工资料"""
    _empinfo.emp_delete(ids)
    return redirect(url_for("all_emp"))


@app.route("/all_list/<ids>", methods=["GET"])
def all_list(ids: str):
    """当月发工资列表"""
    emp_one = _work_list_db.find_one({"_id": ids})  # 寻找月份工人列表
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
    all_documents = _work_list_db.find({})
    document_id = [x["_id"] for x in all_documents]

    return render_template(
        "list.html",
        emp=sort_emp_dict,
        document_id=document_id,
        output_id=output_month,
        total_cash=total_cash,
        total_emp_on_list=total_emp_on_list,
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register"""
    form = RegisterForm()
    get_emp = _members.find({})
    msg = ""

    # From register.html Form
    username = form.username.data
    password = form.password.data
    company_name = form.company_name.data

    # Members in list
    check_members_count = [list_member for list_member in get_emp]

    # Password to hash
    generate_password = _pass.create_password(password)

    # dict mongodb
    new_members = {
        "username": username,
        "password": generate_password,
        "company_name": str(company_name).upper()
    }

    if request.method == "POST":
        if len(check_members_count) == 0:
            _members.insert_one(new_members)
            return redirect(url_for('index'))
        else:
            for check_user in check_members_count:
                if check_user['username'] == username:
                    msg = "Members is exists"
                else:
                    _members.insert_one(new_members)
                    return redirect(url_for('index'))

    return render_template("register.html", form=form, msg=msg)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login"""
    form = LoginForm()
    check_members = _members.find({})
    msg = ""

    if request.method == "POST":
        get_username = form.username.data
        get_password = form.password.data

        for member in check_members:
            com = member['company_name'].split(" ")

            if member['username'] == get_username and _pass.check_password(get_password, member['password']):
                resp = make_response(redirect(url_for('index')))
                resp.set_cookie('userID', "".join(com))
                return resp
            else:
                msg = "Members doesn't exists"
        
    return render_template("login.html", form=form, msg=msg)


if __name__ == "__main__":
    app.run(debug=True)
