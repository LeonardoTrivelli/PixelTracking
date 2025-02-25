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
import json

load_dotenv('.env')

router = APIRouter(
    prefix="/init",
    tags=["Init"]
)

    
@router.get("/")
def init(db: Session = Depends(get_db)):
    """
    Initialize the database with a default user
    """
    try:
        with open('admin.json') as f:
            d = json.load(f)
            print(d)

        ls_admin_users = d["ls_admin_users"]

    except Exception as e:
        return JSONResponse(content={"detail": f"Error reading file, error: {e}, please put the formatted file."}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    for admin_user in ls_admin_users:

        if db.query(models.Users).filter(models.Users.account_name == admin_user["account_name"]).first():
            continue
        else:
            str_salt = utils.salt_generator() 

            # Hash sensitive data single-direction
            password = utils.pwd_context.hash(str_salt+admin_user["password"])

            # Encrypt sensitive data two-direction
            enc_email = utils.encrypt_value(admin_user["email"])
            enc_name = utils.encrypt_value(admin_user["name"])
            enc_surname = utils.encrypt_value(admin_user["surname"])

            # Create a new user
            new_user = models.Users(
                name = enc_name,
                surname = enc_surname,
                uuid = utils.generate_uuid4(),
                account_name = admin_user["account_name"],
                email = enc_email,
                grant_id = admin_user["grant_id"],
                salt = str_salt,
                password = password
            )
            # Add the user to the database
            db.add(new_user)
            # Commit the transaction
            db.commit()
            # Refresh the user model
            db.refresh(new_user)
            
    response = JSONResponse(content={"detail": "Database initialized"})

    return response
