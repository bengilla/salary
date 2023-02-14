from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

class Password:
    def get_password_hash(self, password: str) -> str:
        """Create Password"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> str:
        """Check Password"""
        return pwd_context.verify(plain_password, hashed_password)
