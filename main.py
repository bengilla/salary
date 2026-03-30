"""
Project for TBROS employees salary calculator and employee person info
"""

import datetime
import os
import traceback

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

# Library from own
from emp.emp_mongodb import EmpInfo
from excels import EmpSalary
from forms.form import CreateForm, EditForm
from mongodb import MongoDB

# 设置
load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "tbrosventures")

# Simple users - username: password
USERS = {
    os.getenv("LOGIN_USERNAME", "tbros"): os.getenv("LOGIN_PASSWORD", "password")
}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    if user_id in USERS:
        return User(user_id)
    return None

# Work List MongoDB connect
_work_list_db = MongoDB().work_hour_collection()
_mongodb = MongoDB()

# Get Emp info from MongoDB
_empinfo = EmpInfo()

# Normal get date now
start_datetime = datetime.datetime.now()
end_datetime = start_datetime + datetime.timedelta(minutes=25)
if start_datetime == end_datetime:
    end = end_datetime + datetime.timedelta(minutes=25)
_date_now = start_datetime


@app.route("/", methods=["GET", "POST"])
@login_required
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
    err_traceback = ""

    if request.method == "POST":
        file_input = request.files["file"]
        try:
            emp_salary = EmpSalary(file_input)
            return redirect(url_for("all_work_lists"))
        except Exception as err:  # pylint: disable=W0703
            err_title = "You have error message:"
            err_exception_msg = str(err)
            err_traceback = traceback.format_exc()

    return render_template(
        "index.html",
        date=_date_now,
        all_id=all_id,
        err_title=err_title,
        err_emp=not_register_emp,
        err_exception_msg=err_exception_msg,
        err_traceback=err_traceback,
    )


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_emp():
    """
    建立员工资料，如果员工已存在就会显示 msg
    如果建立成功转至 all.html
    form = form.py
    """
    form = CreateForm()
    msg = ""
    if form.validate_on_submit():
        create_emp = _empinfo.emp_create()
        if create_emp:
            return redirect("/all")
        else:
            msg = "Employee Exists"

    return render_template("add.html", form=form, msg=msg)


@app.route("/all")
@login_required
def all_emp():
    """浏览所有工资列表"""
    return redirect(url_for("all_work_lists"))


@app.route("/all_employees")
@login_required
def all_employees():
    """浏览全部员工"""
    info_from_db = _empinfo.emp_info()
    info = info_from_db.sort("_id", 1)
    info_list = list(info)
    count = len(info_list)

    return render_template(
        "emp.html", info=info_list, emp_name="All Employees", count=count
    )


@app.route("/all_work_lists")
@login_required
def all_work_lists():
    """浏览所有年份的工作时间列表"""
    all_documents = []
    for coll in _mongodb.all_work_hour_collections():
        docs = coll.find({})
        for doc in docs:
            all_documents.append(doc)

    return render_template("all_work_lists.html", documents=all_documents)


@app.route("/info/<ids>")
@login_required
def info_emp(ids: str):
    """浏览单位员工"""
    info = _empinfo.emp_one(ids)
    if info is None:
        return redirect(url_for("all_emp"))
    emp_name = info["name"]
    return render_template("emp.html", info=info, emp_name=emp_name)


@app.route("/edit/<ids>", methods=["GET", "POST"])
@login_required
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
@login_required
def delete_emp(ids: str):
    """删除员工资料"""
    _empinfo.emp_delete(ids)
    return redirect(url_for("all_emp"))


@app.route("/all_list/<ids>", methods=["GET"])
@login_required
def all_list(ids: str):
    """当月发工资列表"""
    emp_one = _mongodb.find_in_all_years(ids)
    if emp_one is None:
        return redirect(url_for("all_emp"))
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
    output_month = emp_one.get("date", "")

    # 所有mongoDB资料 (所有年份)
    all_documents = []
    for coll in _mongodb.all_work_hour_collections():
        docs = coll.find({})
        for doc in docs:
            all_documents.append(doc)
    document_date = [x.get("date", "") for x in all_documents]

    return render_template(
        "list.html",
        emp=sort_emp_dict,
        document_id=document_date,
        output_id=output_month,
        total_cash=total_cash,
        total_emp_on_list=total_emp_on_list,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in USERS and USERS[username] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for("index"))
        error = "Invalid username or password"
    return render_template("login.html", error=error)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
# Test deployment - 2026-03-30
