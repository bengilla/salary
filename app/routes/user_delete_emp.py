from typing import Optional
from fastapi import APIRouter, Cookie, Request, HTTPException, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

# library from own
from models.mongo import MongoDB
from models.jwt_token import Token

delete_emp_router = APIRouter()
templates = Jinja2Templates(directory="templates")

# token
_token = Token()


# delete employee ------------------------------
@delete_emp_router.post(
    "/delete/{ids}", tags=["Emp delete employee"], response_class=RedirectResponse
)
def delete_emp(
    *,
    request: Request,
    access_token: Optional[str] = Cookie(default=None),
    ids: str,
    access: str = Form(None)
) -> RedirectResponse:
    """delete employee"""

    # delete emp info
    try:
        get_token = _token.verify_access_token(access_token)
        company_name = _token.cookie_2_dbname(get_token["name"])
        _db = MongoDB(company_name)

        if access == "access":
            _db.emp_info_collection().delete_one({"_id": ids})
            redirect_url = request.url_for("all_emp")
            return RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
    except:
        raise HTTPException(status_code=404, detail="Not Found")
