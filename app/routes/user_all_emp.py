"""All Employee Section"""
from typing import Optional
from fastapi import (
    APIRouter,
    Cookie,
    Request,
    Form,
    HTTPException,
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

# library from own
from models.mongo import MongoDB
from models.jwt_token import Token

all_emp_router = APIRouter()
templates = Jinja2Templates(directory="templates")


# token
_token = Token()


# list all employee info ------------------------------
@all_emp_router.get("/all", tags=["Emp all employee"], response_class=HTMLResponse)
async def all_emp(
    request: Request, access_token: Optional[str] = Cookie(default=None)
) -> _TemplateResponse:
    """list all employee info"""

    try:
        get_token = _token.verify_access_token(access_token)
        company_name = _token.cookie_2_dbname(get_token["name"])
        _db = MongoDB(company_name)

        list_emp_info = _db.emp_info_collection().find({})

        list_emp_info = list(list_emp_info.sort("_id", 1))
        list_emp_name = [name["name"].lower() for name in list_emp_info]
        list_count = len(list_emp_info)
        return templates.TemplateResponse(
            "all.html",
            {
                "request": request,
                "info": list_emp_info,
                "name": list_emp_name,
                "count": list_count,
                "title": get_token["name"],
                "db": _db.status(),
            },
        )
    except:
        raise HTTPException(status_code=404, detail="Not Found")


@all_emp_router.post("/all", tags=["Emp all employee"], include_in_schema=False)
async def all_emp_post(emp_name: str = Form(None)):
    """all emp post"""
    return {"employee name": emp_name}
