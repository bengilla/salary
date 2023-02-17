from fastapi import (
    APIRouter,
    Cookie,
    Request,
    HTTPException,
    status
)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

# library from own
from models.mongo import MongoDB
from models.jwt_token import Token

delete_emp_router = APIRouter()
templates = Jinja2Templates(directory="templates")

# mongodb
_db = MongoDB()

# token
_token = Token()

# delete employee ------------------------------
@delete_emp_router.get(
    "/delete/{ids}", tags=["Emp delete employee"], response_class=RedirectResponse
)
def delete_emp(
        *, request: Request, company_name: str | None = Cookie(default=None), ids: str
) -> RedirectResponse:
    """delete employee"""

    # delete emp info
    _db.emp_info_collection(_token.cookie_2_dbname(company_name)).delete_one({"_id": ids})

    if company_name:
        redirect_url = request.url_for("all_emp")
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    else:
        raise HTTPException(status_code=404, detail="Not Found")
