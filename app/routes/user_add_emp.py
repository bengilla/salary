from datetime import datetime
from fastapi import (
    APIRouter,
    Cookie,
    Request,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

# library from own
from models.form import CreateForm
from models.image import ImageConvert
from models.mongo import MongoDB
from models.jwt_token import Token

add_emp_router = APIRouter()
templates = Jinja2Templates(directory="templates")

# mongodb
_db = MongoDB()

# normal get date now
_date_now = datetime.now()

# token
_token = Token()


# add employee info ------------------------------
@add_emp_router.get("/add", tags=["Emp add employee"], response_class=HTMLResponse)
async def add_emp(
    request: Request,
    access_token: str | None = Cookie(default=None),
) -> _TemplateResponse:
    """add employee info page"""

    try:
        get_token = _token.verify_access_token(access_token)
        return templates.TemplateResponse(
            "add.html",
            {
                "request": request,
                "title": get_token["name"],
            },
        )
    except:
        raise HTTPException(status_code=404, detail="Not Found")


@add_emp_router.post("/add", tags=["Emp add employee"], include_in_schema=False)
async def add_emp(
    request: Request,
    access_token: str | None = Cookie(default=None),
    add_emp_form: CreateForm = Depends(CreateForm.create),
) -> RedirectResponse:
    """post employee info to server"""

    # Image concert and resize
    if add_emp_form.img_emp.filename:
        image_data = ImageConvert().img_base64(add_emp_form.img_emp.file)
    else:
        empty_image = "./static/images/no-data.jpg"
        image_data = ImageConvert().img_base64(empty_image)

    new_emp = {
        "_id": add_emp_form.name.replace(" ", "").lower(),
        "img_employee": image_data,
        "name": add_emp_form.name.title(),
        "pay_hour": add_emp_form.pay_hour,
        "ic": add_emp_form.ic,
        "dob": add_emp_form.dob,
        "nationality": add_emp_form.nationality,
        "gender": add_emp_form.gender,
        "contact": add_emp_form.contact,
        "address": add_emp_form.address,
        "sign_date": _date_now.date().strftime("%d-%m-%Y"),
    }

    get_token = _token.verify_access_token(access_token)
    _db.emp_info_collection(_token.cookie_2_dbname(get_token["name"])).insert_one(
        new_emp
    )
    redirect_url = request.url_for("mainpage")
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)