"""
Salary management routes
"""

import datetime
import traceback

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required

from mongodb import get_mongodb
from services import SalaryBatchService
from services.salary_calculator import SalaryCalculator

salary_bp = Blueprint("salary", __name__)


@salary_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Upload Excel and calculate salaries"""
    db = get_mongodb()
    all_ids = [x["_id"] for x in db.work_hour_collection.find({})]
    err_title = ""
    err_msg = ""
    err_trace = ""

    if request.method == "POST":
        file_input = request.files["file"]
        version = request.form.get("version", "v0800")
        try:
            batch_service = SalaryBatchService(file_input, version)
            batch_service.process()
            batch_service.save_to_db()
            return redirect(url_for("salary.all_work_lists"))
        except Exception as err:
            err_title = "Error:"
            err_msg = str(err)
            err_trace = traceback.format_exc()

    return render_template(
        "index.html",
        date=datetime.datetime.now(),
        all_id=all_ids,
        err_title=err_title,
        err_msg=err_msg,
        err_trace=err_trace,
    )


@salary_bp.route("/all_work_lists")
@login_required
def all_work_lists():
    """List all salary batches"""
    db = get_mongodb()
    documents = []
    for coll in db.all_work_hour_collections():
        for doc in coll.find({}):
            documents.append(doc)
    return render_template("all_work_lists.html", documents=documents)


@salary_bp.route("/all_list/<batch_id>", methods=["GET", "POST"])
@login_required
def list(batch_id: str):
    """View salary batch details"""
    db = get_mongodb()
    batch = db.find_in_all_years(batch_id)
    if batch is None:
        return redirect(url_for("employees.list_employees"))

    version = request.form.get("version") or request.args.get("version") or "v0800"

    emp_data = batch["emp_work_hours"]
    sorted_emp = dict(sorted(emp_data.items()))

    if version and version != "original":
        sorted_emp = recalculate_emp_data(emp_data, version)

    salaries = [v["total_salary"] for v in sorted_emp.values()]
    total_cash = f"RM {sum(salaries):,.2f}"

    all_docs = []
    for coll in db.all_work_hour_collections():
        for doc in coll.find({}):
            all_docs.append(doc)

    return render_template(
        "list.html",
        emp=sorted_emp,
        document_id=[x.get("date", "") for x in all_docs],
        output_id=batch.get("date", ""),
        total_cash=total_cash,
        total_emp_on_list=len(sorted_emp),
        selected_version=version,
    )


def recalculate_emp_data(emp_data: dict, version: str) -> dict:
    """Recalculate employee data with new version"""
    result = {}
    for emp_name, emp_record in emp_data.items():
        pay_hour = emp_record["pay_hour"]
        daily_records = emp_record.get("output", [])

        total_salary = 0.0
        total_hours = 0.0
        new_records = []

        for day_record in daily_records:
            work_time = day_record.get("work_time", [])
            if work_time and len(work_time) >= 2:
                calc = SalaryCalculator([work_time], pay_hour, version)
                day_hours = calc._calculate_daily_hours(0)
                day_salary = day_hours * pay_hour
            else:
                day_hours = day_record.get("daily_work_hours", 0)
                day_salary = day_record.get("pay_perday", 0)

            total_salary += day_salary
            total_hours += day_hours

            new_records.append({
                "day": day_record.get("day", 0),
                "day_of_week": day_record.get("day_of_week", ""),
                "pay_perday": round(day_salary, 2),
                "work_time": work_time,
                "daily_work_hours": day_hours,
            })

        rounded_salary = round(total_salary / 10) * 10

        result[emp_name] = {
            "pay_hour": pay_hour,
            "total_salary": rounded_salary,
            "total_work_hours": round(total_hours, 2),
            "output": new_records,
        }

    return result
