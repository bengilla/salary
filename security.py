import os

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import timedelta, datetime
from jose import jwt
from dotenv import load_dotenv
from typing import Optional
from dataclasses import dataclass
from enum import Enum

app = FastAPI()

# Test ------
# @dataclass()
# class User:
#     name: str = "beng"
#     age: int = 48
# def info(q: Optional[str] = None, name: Optional[str] = None, age: int = 0):
#     return {"q": q, "namne": name, "age": age}
#
# @app.get("/items/")
# async def result(info: dict = Depends(User)):
#     return info
# Test ------



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

user = {"username": "beng", "password": "$5$rounds=535000$W5NEHOaVhX/vEIFQ$z/GjZ2X/o/S51yewOcjixkbNr4u5S6TGL4tPDH5CRd9"}

def authenticate_user(username, password):
    if username == user["username"]:
        password_check = pwd_context.verify(password, user["password"])
        return password_check

def get_token_user(token: str = Depends(oauth2_scheme)):
    return token

def password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta):
    load_dotenv()
    to_encode = data.copy()

    expire = datetime.now() + expires_delta

    to_encode.update({"exp": expire})
    # print(to_encode)
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    if authenticate_user(username, password):
        access_token = create_access_token(data={"sub": username}, expires_delta=timedelta(minutes=30))
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Incorrect username and password")

@app.get("/")
async def index(token: str = Depends(oauth2_scheme)):
    return {"token": token}