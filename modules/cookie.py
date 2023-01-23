"""
Cookie section
"""

import os
from typing import Any

from cryptography.fernet import Fernet


class Cookie:
    """Cookie Class"""

    def __init__(self) -> None:
        key = os.getenv("CRYPTO_KEY")
        self.fernet = Fernet(key)

    def empty_cookie(self, page: str, cookie_name: str) -> str:
        """Empty Cookie"""
        resp = make_response(redirect(url_for(page)))
        resp.set_cookie(cookie_name, "", expires=0)
        return resp

    def set_cookie(self, page: str, cookie_name: str, cookie_value: str) -> Any:
        """Make Cookie"""
        token = self.fernet.encrypt(cookie_value.encode())
        resp = make_response(redirect(url_for(page)))
        resp.set_cookie(cookie_name, token)
        return resp

    def get_cookie(self, cookie_name: str) -> str:
        """Read Cookie"""
        get_token = request.cookies.get(cookie_name).encode()
        return self.fernet.decrypt(get_token).decode()
