from datetime import datetime
from fastapi import (
    APIRouter,
    Cookie,
    Request,
    HTTPException,
)
from fastapi.templating import Jinja2Templates

# library from own
from models.mongo import MongoDB
from models.jwt_token import Token

salary = APIRouter()
templates = Jinja2Templates(directory="templates")

# token
_token = Token()

# normal get date now
_date_now = datetime.now()


# employee salary info ------------------------------
@salary.get("/salary-list", tags=["Emp employee salary list"])
async def salary_list(
    *, request: Request, access_token: str | None = Cookie(default=None)
):
    """salary list select year section"""

    try:
        get_token = _token.verify_access_token(access_token)
        company_name = _token.cookie_2_dbname(get_token["name"])
        _db = MongoDB(company_name)

        year_collection = _db.collection_name()
        return templates.TemplateResponse(
            "salary-list.html",
            {
                "request": request,
                "date": _date_now,
                "title": get_token["name"],
                "year_collection": year_collection,
                "db": _db.status(),
            },
        )
    except:
        raise HTTPException(status_code=404, detail="Not Found")


@salary.get("/all_list/{year}/{ids}", tags=["Emp employee salary list"])
async def all_list(
    *,
    request: Request,
    access_token: str | None = Cookie(default=None),
    ids: str,
    year: str,
):
    """list every month of employee salary 2"""

    # drop down list
    try:
        get_token = _token.verify_access_token(access_token)
        company_name = _token.cookie_2_dbname(get_token["name"])
        _db = MongoDB(company_name)

        def drop_down_list():
            date_list = _db.collection_name()
            for key, value in date_list.items():
                if key == year:
                    return value

        # get single salary list
        work_hour_collection = _db.emp_work_hour_collection(year)

        one_salary_list = work_hour_collection.find_one({"date": ids})
        salary_output = one_salary_list["emp_work_hours"]
        sort_emp_dict = dict(sorted(salary_output.items()))

        # get total amounts
        total_amounts = one_salary_list["total_amounts"]
        total_cash = f"RM {total_amounts:,.2f}"

        # get month title
        output_month = one_salary_list["date"].split("-")[1]

        return templates.TemplateResponse(
            "list.html",
            {
                "request": request,
                "title": get_token["name"],
                "emp": sort_emp_dict,
                "drop_down": drop_down_list(),
                "year": year,
                "month": output_month,
                "total_cash": total_cash,
                "total_emp_on_list": len(salary_output),
                "db": _db.status(),
            },
        )
    except:
        raise HTTPException(status_code=404, detail="Not Found")
