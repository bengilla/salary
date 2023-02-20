from config.settings import settings

from datetime import datetime, timedelta
from jose import jwt, JWTError


class Token:
    def create_access_token(self, company_name: str):
        data: dict = {"name": company_name}
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=60)
        to_encode.update({"exp": expire})

        encode_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encode_jwt

    def verify_access_token(self, token: str):
        decode_jwt = jwt.decode(
            token, settings.SECRET_KEY, algorithms=settings.ALGORITHM
        )
        return decode_jwt

    def cookie_2_dbname(self, cookie_name: str) -> str:
        return cookie_name.upper().replace(" ", "")

    def jwt_error(self):
        return JWTError
