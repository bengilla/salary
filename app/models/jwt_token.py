"""Jwt Token"""
from datetime import datetime, timedelta
from jose import jwt, JWTError

from config.settings import settings


class Token:
    """把讯息转成Token, 然后存在Cookie里"""

    def create_access_token(self, company_name: str):
        """生成Token"""
        data: dict = {"name": company_name}
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=int(settings.TOKEN_TIMEOUT))
        to_encode.update({"exp": expire})

        encode_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encode_jwt

    def verify_access_token(self, token: str):
        """识别Token"""
        decode_jwt = jwt.decode(
            token, settings.SECRET_KEY, algorithms=settings.ALGORITHM
        )
        return decode_jwt

    def cookie_2_dbname(self, cookie_name: str) -> str:
        """把cookie转成名字(公司名字)"""
        return cookie_name.upper().replace(" ", "")

    def jwt_error(self):
        """如果Token错误"""
        return JWTError
