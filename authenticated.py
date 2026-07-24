from pwdlib import PasswordHash
from fastapi import HTTPException, Cookie
from dotenv import dotenv_values
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError


configure_env = dotenv_values(".env")

SECRET_KEY = configure_env.get('SECRET_KEY','abcde_super_secret_test_key_12345')
ALGORITHM = "HS256"

if not SECRET_KEY:
    raise RuntimeError("SECRET_KDependsEY missing from environment configuration!")

password_hash = PasswordHash.recommended()

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


async def get_current_user(access_token: str | None = Cookie(None, alias="access_token")):

  credentials_exceptions = HTTPException(
    status_code=401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}
  )


  if not access_token:
      raise credentials_exceptions
  
  try:

    token = access_token.replace("Bearer", "").strip() if access_token.startswith("Bearer") else access_token

    payload = jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])

    email = payload.get("sub")

    if email is None:
      raise credentials_exceptions
    return email
  except InvalidTokenError:
      raise credentials_exceptions
  
