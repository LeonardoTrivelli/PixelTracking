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
#import pytz


router = APIRouter(
    prefix="/contact",
    tags=["Contact"]
)

@router.post('/', status_code=status.HTTP_201_CREATED, tags=["Contact"])
def add(
    request: schemas.AddContact,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):
    """
    Add a new contact to a group
    :param request: schemas.AddContact
    :param db: Session
    :param token: str

    :return: schemas.AddContact
    """

    account_name = utils.verify_token(token)

    user = db.query(models.Users).filter(models.Users.account_name == account_name).first()

    # Check if user is active
    if user.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active.")
    
    # Check if the group exists
    group = db.query(models.Groups).filter(models.Groups.id == request.group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Group with id {request.group_id} not found.")
    
    # Check if the group is active
    if group.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Group is not active.")
    
    # Check if campaign exists
    campaign = db.query(models.Campaigns).filter(models.Campaigns.id == request.campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Campaign with id {group.campaign_id} not found.")
    
    # Check if campaign is active
    campaign = db.query(models.Campaigns).filter(models.Campaigns.id == request.campaign_id).first()
    if campaign.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Campaign is not active")
    
    # Check if the scheduled datetime is in the future
    #if request.scheduled_datetime < datetime.datetime.now(tz=pytz.utc):
    #    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scheduled datetime must be in the future.")

    new_contact = models.Contacts(
        uuid = request.uuid,
        campaign_id = request.campaign_id,
        group_id = request.group_id,
        scheduled_datetime = request.scheduled_datetime
    )

    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    response = JSONResponse(
        content={
            "message": "Contact created successfully",
            "contact_id": new_contact.uuid
        },
        status_code=status.HTTP_201_CREATED
    )

    return response

@router.delete('/{uuid}', status_code=status.HTTP_200_OK, tags=["Contact"])
def delete(
    uuid: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):
    """
    Delete a contact
    :param uuid: str
    :param db: Session
    :param token: str

    :return: JSONResponse(message)
    """

    account_name = utils.verify_token(token)

    user = db.query(models.Users).filter(models.Users.account_name == account_name).first()

    # Check if user is active
    if user.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active.")
    
    contact = db.query(models.Contacts).filter(models.Contacts.uuid == uuid).first()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact with id {uuid} not found")

    db.delete(contact)

    db.commit()

    response = JSONResponse(
        content={"message": f"Contact with id {uuid} has been deleted"},
        status_code=status.HTTP_200_OK
    )

    return response

@router.get('/', status_code=status.HTTP_200_OK, tags=["Contact"])
def get_all(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):
    """
    Get all contacts
    :param db: Session
    :param token: str

    :return: List[schemas.GetContact]
    """

    account_name = utils.verify_token(token)

    user = db.query(models.Users).filter(models.Users.account_name == account_name).first()

    # Check if user is active
    if user.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active.")
    
    contacts = db.query(models.Contacts).all()

    return contacts

@router.get('/{uuid}', status_code=status.HTTP_200_OK, tags=["Contact"])
def get(
    uuid: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):
    """
    Get a contact by id
    :param uuid: str
    :param db: Session
    :param token: str

    :return: schemas.GetContact
    """

    account_name = utils.verify_token(token)

    user = db.query(models.Users).filter(models.Users.account_name == account_name).first()

    # Check if user is active
    if user.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active.")
    
    contact = db.query(models.Contacts).filter(models.Contacts.uuid == uuid).first()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact with id {uuid} not found")

    return contact

@router.get('/group/{group_id}', status_code=status.HTTP_200_OK, tags=["Contact"])
def get_by_group(
    group_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):
    """
    Get all contacts by group
    :param group_id: int
    :param db: Session
    :param token: str

    :return: List[schemas.GetContact]
    """

    account_name = utils.verify_token(token)

    user = db.query(models.Users).filter(models.Users.account_name == account_name).first()

    # Check if user is active
    if user.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active.")
    
    contacts = db.query(models.Contacts).filter(models.Contacts.group_id == group_id).all()

    return contacts

@router.get('/campaign/{campaign_id}', status_code=status.HTTP_200_OK, tags=["Contact"])
def get_by_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):
    """
    Get all contacts by campaign
    :param campaign_id: int
    :param db: Session
    :param token: str

    :return: List[schemas.GetContact]
    """

    account_name = utils.verify_token(token)

    user = db.query(models.Users).filter(models.Users.account_name == account_name).first()

    # Check if user is active
    if user.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active.")
    
    contacts = db.query(models.Contacts).filter(models.Contacts.campaign_id == campaign_id).all()

    return contacts