from fastapi import APIRouter
from fastapi import status
from fastapi import HTTPException
from fastapi import Depends
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import get_db
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
import utils
import datetime
import utils
import models

load_dotenv('.env')

router = APIRouter(
    prefix="/login",
    tags=["Login"]
)

@router.post("/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    if not utils.authenticate_user(form_data.username, form_data.password, db = db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = datetime.timedelta(minutes=int(utils.API_ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = utils.create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
    try:
        user_id = db.query(models.Users).filter(models.Users.account_name == form_data.username).first().id
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Invalid credentials")
    
    #insert in logins table
    try:
        new_login = models.Logins(
            user_id = user_id,
            login_datetime = datetime.datetime.now(),
            login_status = 1,
            token=access_token,
            token_expiry=datetime.datetime.utcnow() + access_token_expires
        )

        db.add(new_login)
        db.commit()
        db.refresh(new_login)
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error while inserting in logins table")
    try:
        response = JSONResponse(
            content={
                "message": "Login successful",
                "user_id": user_id,
                "account_name": form_data.username,
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": utils.API_ACCESS_TOKEN_EXPIRE_MINUTES,
                "expiration_date": utils.serialize_datetime(datetime.datetime.utcnow() + access_token_expires)
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Error while generating response")

    return response
