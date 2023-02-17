from fastapi import APIRouter, Cookie, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

# library from own
from models.form import EditForm
from models.image import ImageConvert
from models.mongo import MongoDB
from models.jwt_token import Token

single_emp_router = APIRouter()
templates = Jinja2Templates(directory="templates")

# mongodb
_db = MongoDB()

# token
_token = Token()


# single employee info ------------------------------
@single_emp_router.get("/info/{ids}", tags=["Emp single employee"])
async def info_emp(
    *, request: Request, access_token: str | None = Cookie(default=None), ids: str
):
    """show single employee info"""

    try:
        get_token = _token.verify_access_token(access_token)
        emp_info = _db.emp_info_collection(_token.cookie_2_dbname(get_token["name"]))
        single_emp = emp_info.find_one({"_id": ids})

        return templates.TemplateResponse(
            "emp.html",
            {
                "request": request,
                "info": single_emp,
                "title": get_token["name"],
            },
        )
    except:
        raise HTTPException(status_code=404, detail="Not Found")


# single employee edit ------------------------------
@single_emp_router.get(
    "/edit/{ids}", tags=["Emp edit employee"], response_class=HTMLResponse
)
async def edit_emp(
    *, request: Request, access_token: str | None = Cookie(default=None), ids: str
) -> _TemplateResponse:
    """edit employee info"""

    # Get Employee info
    try:
        get_token = _token.verify_access_token(access_token)
        emp_info = _db.emp_info_collection(_token.cookie_2_dbname(get_token["name"]))
        single_emp = emp_info.find_one({"_id": ids})

        return templates.TemplateResponse(
            "edit.html",
            {"request": request, "edit_emp": single_emp, "title": get_token["name"]},
        )
    except:
        raise HTTPException(status_code=404, detail="Not Found")


@single_emp_router.post(
    "/edit/{ids}",
    tags=["Emp edit employee"],
    response_class=RedirectResponse,
    include_in_schema=False,
)
async def edit_emp(
    *,
    request: Request,
    access_token: str | None = Cookie(default=None),
    edit_emp_form: EditForm = Depends(EditForm.edit),
    ids: str,
) -> RedirectResponse:
    """post edit employee info"""

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
    get_token = _token.verify_access_token(access_token)
    _db.emp_info_collection(_token.cookie_2_dbname(get_token["name"])).update_one(
        {"_id": ids}, {"$set": edit_emp_form}
    )

    redirect_url = request.url_for("all_emp")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
