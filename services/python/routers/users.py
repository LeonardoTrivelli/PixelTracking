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

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@router.post('/', status_code=status.HTTP_201_CREATED, tags=["User"])
def add(
    request: schemas.AddUser,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):
    """
    Create a new user
    :param request: schemas.CreateUser
    :param db: Session
    :param token: str

    :return: schemas.CreateUser
    """

    account_name = utils.verify_token(token)

    user = db.query(models.Users).filter(models.Users.account_name == account_name).first()

    if user.grant_id != 3:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to add a user.")

    user_id = user.id

    # Username must be unique
    if db.query(models.Users).filter(models.Users.account_name == request.account_name).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Username {request.account_name} already exists.")
    
    # Username must be unique
    if db.query(models.Users).filter(models.Users.email == request.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email {request.email} has been already registered.")

    # Check for email validity
    if not utils.validate_email(request.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email {request.email} is not valid.")

    str_salt = utils.salt_generator() 

    # Hash sensitive data single-direction
    request.password = utils.pwd_context.hash(str_salt+request.password)

    # Encrypt sensitive data two-direction
    enc_email = utils.encrypt_value(request.email)

    enc_name = utils.encrypt_value(request.name)

    enc_surname = utils.encrypt_value(request.surname)

    # Create a new user
    new_user = models.Users(
        name = enc_name,
        surname = enc_surname,
        uuid = utils.generate_uuid4(),
        account_name = request.account_name,
        email = enc_email,
        grant_id = request.grant_id,
        salt = str_salt,
        password = request.password
    )
    # Add the user to the database
    db.add(new_user)
    # Commit the transaction
    db.commit()
    # Refresh the user model
    db.refresh(new_user)

    response = JSONResponse(
        content={"message": "User created successfully"},
        status_code=status.HTTP_201_CREATED
    )

    return response

# Delete a User
@router.delete('/{id}', tags=["User"])
def delete(
    id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):

    """
    Delete a user
    :param id: int
    :param db: Session
    :param token: str

    Only master users can delete a user (devs, admins)

    :return: JSONResponse(message)
    """

    account_name = utils.verify_token(token)

    try:
        user = db.query(models.Users).filter(models.Users.account_name == account_name).first()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found: {e}, {account_name}")
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found, searched for {account_name}")

    if user.grant_id != 3:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to delete a user.")

    user = db.query(models.Users).filter(models.Users.id == id).first()

    user.deleted_datetime = datetime.datetime.now()

    db.commit()

    db.refresh(user)

    response = JSONResponse(
        content={"message": f"User with id {id} has been deleted"},
        status_code=status.HTTP_200_OK
    )

    return response
