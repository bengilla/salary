"""
Password Section
"""

import bcrypt


class Password:
    """Hash Password"""

    def __init__(self) -> None:
        pass

    def create_password(self, password):
        """Create Password"""
        str_password = str(password)
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(str_password.encode("utf-8"), salt)
        return hashed_password.decode()

    def check_password(self, password, hashed_password):
        """Check Password"""
        encode_hashed = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password.encode("utf-8"), encode_hashed)