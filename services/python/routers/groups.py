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
    prefix="/group",
    tags=["Group"]
)

@router.post('/', status_code=status.HTTP_201_CREATED, tags=["Group"])
def add(
    request: schemas.AddGroup,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):
    """
    Add a new group to a campaign
    :param request: schemas.AddGroup
    :param db: Session
    :param token: str

    :return: schemas.AddGroup
    """

    account_name = utils.verify_token(token)

    user = db.query(models.Users).filter(models.Users.account_name == account_name).first()

    # Check if user is active
    if user.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active.")
    
    # Check if the campaign exists
    campaign = db.query(models.Campaigns).filter(models.Campaigns.id == request.campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Campaign with id {request.campaign_id} not found.")
    
    # Check if the campaign is active
    if campaign.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Campaign is not active.")

    new_group = models.Groups(
        campaign_id = request.campaign_id,
        group_name = request.group_name,
        group_description = request.group_description,
        campaign_group_id = request.campaign_group_id
    )

    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    response = JSONResponse(
        content={
            "message": f"Group created successfully for campaign {new_group.campaign_id}",
            "group_name": new_group.group_name,
            "group_description": new_group.group_description
        },
        status_code=status.HTTP_201_CREATED
    )

    return response

@router.delete('/{id}', tags=["Group"])
def delete(
    id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):

    """
    Delete a group
    :param id: int
    :param db: Session
    :param token: str

    Only master users can delete a group (devs, admins)

    :return: JSONResponse(message)
    """

    account_name = utils.verify_token(token)

    try:
        user = db.query(models.Users).filter(models.Users.account_name == account_name).first()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found: {e}, {account_name}")
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found, searched for {account_name}")

    group = db.query(models.Groups).filter(models.Groups.id == id).first()

    group.deleted_datetime = datetime.datetime.now()

    db.commit()

    db.refresh(group)

    response = JSONResponse(
        content={"message": f"Group with id {id} has been deleted"},
        status_code=status.HTTP_200_OK
    )

    return response

@router.get('/', status_code=status.HTTP_200_OK, tags=["Group"])
def get_groups(
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

    groups = db.query(models.Groups).all()

    return groups

@router.get('/{id}', status_code=status.HTTP_200_OK, tags=["Group"])
def get_group(
    id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):

    """
    Get a group by id
    :param id: int
    :param db: Session
    :param token: str

    :return: schemas.Group
    """

    account_name = utils.verify_token(token)

    user = db.query(models.Users).filter(models.Users.account_name == account_name).first()

    # Check if user is active
    if user.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active.")

    group = db.query(models.Groups).filter(models.Groups.id == id).first()

    return group

@router.put('/{id}', status_code=status.HTTP_200_OK, tags=["Group"])
def update(
    id: int,
    request: schemas.UpdateGroup,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):

    """
    Update a group
    :param id: int
    :param request: schemas.AddGroup
    :param db: Session
    :param token: str

    :return: schemas.Group
    """

    account_name = utils.verify_token(token)

    user = db.query(models.Users).filter(models.Users.account_name == account_name).first()

    # Check if user is active
    if user.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active.")

    group = db.query(models.Groups).filter(models.Groups.id == id).first()

    group.group_name = request.group_name
    group.group_description = request.group_description

    db.commit()

    db.refresh(group)

    response = JSONResponse(
        content={
            "message": f"Group with id {id} has been updated",
            "group_name": group.group_name,
            "group_description": group.group_description
        },
        status_code=status.HTTP_200_OK
    )

    return response