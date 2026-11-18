from fastapi import APIRouter, Depends, HTTPException,Response, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from app.core.db  import dep_db
from app.core.authenticated import create_access_token, get_current_user, decode_token_email,send_email
from app.crud import user_create, login, user_me, mark_verify_email
from app.profile import UserLogin, UserCreate, Profile, UserMe
from datetime import timedelta
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError


ACCESS_TOKEN_EXPIRE_MINUTES = 30
router = APIRouter(
    prefix="/user",
    tags=["Users"]               )

@router.post('/register', response_model=Profile)
async def create_profile(user:UserCreate,background_tasks:BackgroundTasks,db:Session = Depends(dep_db)):

    try:
        result = user_create(user=user,db=db)

        if isinstance(result, dict) and "message" in result:
            raise HTTPException(status_code=400, detail=result["message"])

        background_tasks.add_task(send_email, result.email)
        return result
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

@router.get('/verification', response_class=HTMLResponse)
async def verify(token:str, db:Session = Depends(dep_db)):
    try:
        payload = await decode_token_email(token=token)

        email = payload.get("email")
        token_type = payload.get("type")

        if not email or token_type != 'email_verification':
            return HTMLResponse(
                content='<h3>Link inválido ou propósito do token incorreto.</h3>',
                status_code=400
            )
        result = mark_verify_email(email=email, db=db)

        status_code = 200 if result.get("success") else 400

        template = f'''
                        <!DOCTYPE html>
                            <html lang="eng">
                                <head>
                                <meta charset="UTF-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                </head>
                                <body>
                                <h3>{result["message"]}</h3>
                                </body>
                            </html>
                    '''
        return HTMLResponse(content=template, status_code=status_code)
    except ExpiredSignatureError:
        error_template = '<h3>O link de verificação expirou. Por favor, solicite um novo.</h3>'
        return HTMLResponse(content=error_template, status_code=400)

    except InvalidTokenError:
        error_template = '<h3>Token inválido. Verifique o link enviado.</h3>'
        return HTMLResponse(content=error_template, status_code=400)




@router.post('/login/token')
def user_login(response:Response,form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db:Session = Depends(dep_db)):
    user = UserLogin(email=form_data.username, password = form_data.password)

    authenticated_user = login(user=user, db=db)

    if authenticated_user is None:
        raise HTTPException(status_code=401, detail="Email or Password is wrong")

    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))

    access_token = create_access_token(data={"sub":authenticated_user.email}, expires_delta=access_token_expires)

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )


    return {"message": "Login successful","email": authenticated_user.email,"name":authenticated_user.name,"id":authenticated_user.id}

@router.post('/logout')
def logout(response:Response):
    response.delete_cookie(key="access_token", path="/", httponly=True,samesite='lax', secure=False)

    return{"message":"Successfully logged out!!"}

@router.get('/me', response_model=UserMe)
def get_user(db:Session = Depends(dep_db), current_user: str = Depends(get_current_user)):
    user = user_me(email=current_user, db=db)
    if user is None:
        raise HTTPException(status_code=401, detail="You need to be authenticated.")
    return user

