# from passlib.context import CryptContext
#
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)
#
# def get_password_hash(password):
#     return pwd_context.hash(password)
#
# result = get_password_hash("beng")
# print(result)
#
# back = verify_password("beng", result)
# print(back)

# ---------------------------------------------------
# class User(BaseModel):
#     username: str
#     email: Union[str, None] = None
#     full_name: Union[str, None] = None
#     disabled: Union[bool, None] = None
#
# dicts = [
#     {'name': 'Michelangelo',
#      'food': 'PIZZA'},
#     {'name': 'Garfield',
#      'food': 'lasanga'},
#     {'name': 'Walter',
#      'food': 'pancakes'},
#     {'name': 'Galactus',
#      'food': 'worlds'}
# ]
#
# string = "Hi, I'm {name} and I love to eat {food}!"
#
# def string_factory(dicts, string):
#   formatted = []
#   for data in dicts:
#     new_dict = data
#     formatted.append(string.format(**new_dict))
#   return formatted
#
#
# print(string_factory(dicts, string))
#
# ppl = {"name": "Beng", "age": "48"}
# result = "I'm {name} and i'm {age}"
# a = result.format(**ppl)
# print(a)
# ---------------------------------------------------
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

data = {"name": "bengilla", "title": "TBROS Ventures Sdn Bhd"}

token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
print(token)

# def decode_token():
#     token_get = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYmVuZ2lsbGEiLCJ0aXRsZSI6IlRCUk9TIFZlbnR1cmVzIFNkbiBCaGQifQ.USBGb0InUeL2cxNW2afrKJvWl0Cepv6TFKsqysrU"
#     try:
#         get_token = jwt.decode(token_get, SECRET_KEY, algorithms=ALGORITHM)
#         print(get_token)
#     except JWTError as err:
#         print(err)
#
# decode_token()
