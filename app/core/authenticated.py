from pwdlib import PasswordHash
from fastapi import HTTPException, Cookie
from dotenv import dotenv_values
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema
import re


configure_env = dotenv_values(".env")

SECRET_KEY = configure_env.get('SECRET_KEY','abcde_super_secret_test_key_12345')
ALGORITHM = "HS256"
SECRET_KEY_EMAIL = configure_env.get('SECRET_KEY_EMAIL','abcde_super_secret_test_key_12345')
TESTING = configure_env.get('TESTING', 'true')

conf = ConnectionConfig(
   MAIL_USERNAME=configure_env.get('MAIL_USERNAME', ''),
   MAIL_PASSWORD = configure_env.get('MAIL_PASSWORD', ''),
   MAIL_FROM = configure_env.get('MAIL_USERNAME', 'noreply@example.com'),
   MAIL_PORT=587,
   MAIL_SERVER="smtp.gmail.com",
   MAIL_STARTTLS=True,
   MAIL_SSL_TLS=False,
   USE_CREDENTIALS=True,
   VALIDATE_CERTS=True
)

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY Depends missing from environment configuration!")

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


async def send_email(email:str):

  if not email or not email.strip():
    return None

  pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

  if not re.match(pattern, email):
     return 'Invalid Format'

  is_testing = TESTING.lower() == "true"

  if is_testing:
     print(f"Test Mode - Email not sent")
     return 'Test Mode'


  expire = datetime.now(timezone.utc) + timedelta(hours=24)
  
  token_data = {
      "email":email,
      "exp":expire,
      "type":"email_verification"
   }

  token = jwt.encode(token_data, SECRET_KEY_EMAIL, algorithm=ALGORITHM)
  template = f'''
            <!DOCTYPE html>
                <html lang="eng">
                  <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                  </head>
                  <body>
                    <h3>Verifique Seu Email!</h3>
                    <p>Voce Cadastrou em nosso Site Pode Falar, por favor Verifique seu email</p>
                    <br/>
                    <a href="http://127.0.0.1:8000/user/verification/?token={token}" target="_blank" 
                    style="background-color:#1c1f23; 
                    color:#FFFFFF; 
                    border-radius: 8px;
                    padding:12px 24px;
                    text-decoration: none;
                    font-weight: bold;
                    font-family: Arial, sans-serif;">Verificar o email!</a>
                  </body>
                </html>

              '''

  message = MessageSchema(
     subject="Pode Falar - verifique sua conta",
     recipients=[email],
     body=template,
     subtype='html'
  )

  fm = FastMail(conf)

  await fm.send_message(message=message)


async def decode_token_email(token:str):
   payload = jwt.decode(token, SECRET_KEY_EMAIL, algorithms=ALGORITHM)

   return payload