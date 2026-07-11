from typing import Annotated

from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from fastapi import HTTPException, Depends
from dotenv import dotenv_values
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError


configure_env = dotenv_values(".env")

SECRET_KEY = configure_env['SECRET_KEY'] or 'abcde_super_secret_test_key_12345'
ALGORITHM = "HS256"

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY missing from environment configuration!")

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login/token")

def get_hash(password):
  if not password or not password.strip():
    raise HTTPException(status_code=422, detail="Password cannot be blank.")
  return password_hash.hash(password)


def check_password(password,hashed):

    return password_hash.verify(password, hashed)


def create_access_token(data:dict, expires_delta:timedelta | None = None):
  to_encode = data.copy()

  if expires_delta:
    expire = datetime.now(timezone.utc) + expires_delta
  else:
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)

  to_encode.update({"exp":expire})
  
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

  return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
  credentials_exceptions = HTTPException(
    status_code=401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}
  )

  try:
    payload = jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])
    email = payload.get("sub")

    if email is None:
      raise credentials_exceptions
    return email
  except InvalidTokenError:
      raise credentials_exceptions
  
