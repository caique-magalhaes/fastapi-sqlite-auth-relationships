from pwdlib import PasswordHash
from fastapi import HTTPException

password_hash = PasswordHash.recommended()


def get_hash(password):
  if not password or not password.strip():
    raise HTTPException(status_code=422, detail="Password cannot be blank.")
  return password_hash.hash(password)


def check_password(password,hashed):

    return password_hash.verify(password, hashed)

