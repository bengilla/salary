"""Password Section"""

import bcrypt


class Password:
    """Hash Password"""

    def create_password(self, password):
        """Create Password"""
        str_password = str(password)
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(str_password.encode('utf-8'), salt)
        return hashed_password.decode()

    def check_password(self, password, hashed_password):
        """Check Password"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
