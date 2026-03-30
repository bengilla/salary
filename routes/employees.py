"""
Employee management routes
"""

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required

from forms import CreateForm, EditForm
from services import EmployeeService

employees_bp = Blueprint("employees", __name__)


@employees_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Create new employee"""
    form = CreateForm()
    msg = ""
    if form.validate_on_submit():
        service = EmployeeService()
        success = service.create(
            name=form.name.data,
            ic=form.ic.data,
            pay_hour=form.pay_hour.data,
            img_employee=form.img_employee.data,
            dob=form.dob.data or "",
            nationality=form.nationality.data or "",
            gender=form.gender.data or "",
            contact=form.contact.data or "",
            address=form.address.data or "",
        )
        if success:
            return redirect(url_for("employees.list_employees"))
        msg = "Employee Exists"
    return render_template("add.html", form=form, msg=msg)


@employees_bp.route("/all")
@login_required
def all():
    """Redirect to all employees list"""
    return redirect(url_for("employees.list_employees"))


@employees_bp.route("/all_employees")
@login_required
def list_employees():
    """List all employees"""
    service = EmployeeService()
    employees = list(service.list_all())
    employees.sort(key=lambda x: x["_id"])
    return render_template(
        "emp.html",
        info=employees,
        emp_name="All Employees",
        count=len(employees),
    )


@employees_bp.route("/info/<emp_id>")
@login_required
def info(emp_id: str):
    """View single employee"""
    service = EmployeeService()
    emp = service.get_one(emp_id)
    if emp is None:
        return redirect(url_for("employees.list_employees"))
    return render_template("emp.html", info=emp, emp_name=emp["name"])


@employees_bp.route("/edit/<emp_id>", methods=["GET", "POST"])
@login_required
def edit(emp_id: str):
    """Edit employee information"""
    form = EditForm()
    service = EmployeeService()
    emp = service.get_one(emp_id)

    if request.method == "POST":
        service.update(
            emp_id=emp_id,
            ic_card=form.ic.data,
            contact=form.contact.data,
            address=form.address.data,
            pay=form.pay_hour.data,
            img_employee=form.img_employee.data if form.img_employee.data else None,
        )
        return redirect(url_for("employees.list_employees"))

    return render_template("edit.html", form=form, edit_emp=emp)


@employees_bp.route("/delete/<emp_id>")
@login_required
def delete(emp_id: str):
    """Delete employee"""
    service = EmployeeService()
    service.delete(emp_id)
    return redirect(url_for("employees.list_employees"))
