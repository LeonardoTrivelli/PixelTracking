from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from passlib.context import CryptContext
from fastapi.responses import JSONResponse
import string
import random
import utils
import datetime
from utils import oauth2_scheme
from fastapi import Request
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/view",
    tags=["View"]
)

@router.get('/', status_code=status.HTTP_200_OK, tags=["View"])
def get_views(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):

    """
    Get all groups
    :param db: Session
    :param token: str

    :return: List[schemas.Group]
    """

    account_name = utils.verify_token(token)

    user = db.query(models.Users).filter(models.Users.account_name == account_name).first()

    # Check if user is active
    if user.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active.")
    
    views = db.query(models.Views).all()

    return views