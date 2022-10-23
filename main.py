"""
Project for TBROS employees salary calculator and employee person info
"""

from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for

# Library from own
# from camera import Camera
from emp_mongodb import EmpInfo
from excel_main import EmpSalary
from forms import CreateForm, EditForm
from mongodb import MongoDB

# 设置
app = Flask(__name__)
app.config["SECRET_KEY"] = "tbrosventures"

# Work List MongoDB connect
_work_list_db = MongoDB().work_hour_collection()

# Get Emp info from MongoDB
_empinfo = EmpInfo()

# Normal get date now
_date_now = datetime.now()


@app.route("/", methods=["GET", "POST"])
def index():
    """
    链接至 index.html, 同时也输出日期
    """
    # Get ID from list from data
    find_all_id = _work_list_db.find({})
    all_id = [x["_id"] for x in find_all_id]
    err_title = ""
    err_msg = ""
    err_exception_msg = ""

    if request.method == "POST":
        file_input = request.files["file"]
        try:
            emp_salary = EmpSalary(file_input)
            if len(emp_salary.not_register) == 0:  # pylint: disable=E1101
                return render_template("complete.html")
            else:
                err_title = "This all members not in website:"
                err_msg = emp_salary.not_register  # pylint: disable=E1101
        except Exception as err:  # pylint: disable=W0703
            err_title = "Wrong file type!!!, please select again"
            err_exception_msg = err

    return render_template(
        "index.html",
        date=_date_now,
        all_id=all_id,
        err_title=err_title,
        err_msg=err_msg,
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
    if form.validate_on_submit():
        create_emp = _empinfo.emp_create()
        if create_emp:
            return redirect("/all")
        else:
            msg = "Employee Exists, IC / PASSPORT is duplicate"

    return render_template("add.html", form=form, msg=msg)


@app.route("/all")
def all_emp():
    """浏览全部员工"""
    count = 0
    for _ in _empinfo.emp_info():
        count += 1

    info = _empinfo.emp_info()
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
        ic_card = form.ic.data
        contact = form.contact.data
        address = form.address.data
        pay = form.pay_hour.data

        _empinfo.emp_edit(ids, ic_card, contact, address, pay)

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
    emp_one = _work_list_db.find_one({"_id": ids})
    emp_output = emp_one["emp_work_hours"]

    # 呈现所有员工总数工资
    salary = []
    for _, value in emp_output.items():
        output_value = value
        salary.append(output_value["total_salary"])

<<<<<<< HEAD
    # 名单总数
    total_emp_on_list = len(emp_output)
    # 工资总数
=======
>>>>>>> parent of 8a3babf (add total employee at list.html)
    total_cash = f"RM {sum(salary):,.2f}"

    # 月份列表转换
    month_list = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    # 取文件月份
    output_month = int(ids.split("-")[0])
    # 取文件日期
    output_day = int(ids.split("-")[1])
    print(output_month, output_day)
    # 呈现月份，把数字转换成英文
    output_id = month_list[output_month - 1]

    # 所有mongoDB资料
    all_documents = _work_list_db.find({})
    document_id = [x["_id"] for x in all_documents]

    return render_template(
        "list.html",
        emp=emp_output,
        document_id=document_id,
        output_id=output_id,
        total_cash=total_cash,
    )


# @app.route("/camera")
# def camera():
#     """Testing Camera"""
#     from camera import Camera

#     camera = Camera()
#     return camera.run_camera()


if __name__ == "__main__":
    app.run(debug=True)
