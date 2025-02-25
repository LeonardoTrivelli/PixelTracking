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
    prefix="/campaign",
    tags=["Campaign"]
)

@router.post('/', status_code=status.HTTP_201_CREATED, tags=["Campaign"])
def add(
    request: schemas.AddCampaign,
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

    # Check if user is active
    if user.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active.")
    
    # Check if an active campaign has the same name
    campaign = db.query(models.Campaigns).filter(models.Campaigns.campaign_name == request.campaign_name and models.Campaigns.deleted_datetime == None).first()
    if campaign and not campaign.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Campaign with name {request.campaign_name} already exists, deactivate it before creating another one with the same name.")

    new_campaign = models.Campaigns(
        campaign_name = request.campaign_name,
        campaign_description = request.campaign_description,
        start_datetime = request.start_datetime,
        end_datetime = request.end_datetime
    )

    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)

    response = JSONResponse(
        content={
            "message": "Campaign created successfully",
            "campaign_id": new_campaign.id,
            "campaign_name": new_campaign.campaign_name
        },
        status_code=status.HTTP_201_CREATED
    )

    return response

@router.delete('/{campaign_id}', status_code=status.HTTP_200_OK, tags=["Campaign"])
def delete(
    campaign_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):
    """
    Delete a campaign
    :param campaign_id: int
    :param db: Session
    :param token: str

    :return: JSONResponse(message)
    """

    account_name = utils.verify_token(token)

    user = db.query(models.Users).filter(models.Users.account_name == account_name).first()

    # Check if user is active
    if user.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active.")
    
    campaign = db.query(models.Campaigns).filter(models.Campaigns.id == campaign_id).first()

    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Campaign with id {campaign_id} not found")

    campaign.deleted_datetime = datetime.datetime.now()

    db.commit()

    db.refresh(campaign)

    response = JSONResponse(
        content={"message": f"Campaign with id {campaign_id} has been deleted"},
        status_code=status.HTTP_200_OK
    )

    return response

@router.get('/', status_code=status.HTTP_200_OK, tags=["Campaign"])
def get_campaigns(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):
    """
    Get all campaigns
    :param db: Session
    :param token: str

    :return: List[schemas.Campaign]
    """

    account_name = utils.verify_token(token)

    user = db.query(models.Users).filter(models.Users.account_name == account_name).first()

    # Check if user is active
    if user.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active.")
    
    campaigns = db.query(models.Campaigns).all()

    return campaigns

@router.get('/{campaign_id}', status_code=status.HTTP_200_OK, tags=["Campaign"])
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):
    """
    Get a campaign
    :param campaign_id: int
    :param db: Session
    :param token: str

    :return: schemas.Campaign
    """

    account_name = utils.verify_token(token)

    user = db.query(models.Users).filter(models.Users.account_name == account_name).first()

    # Check if user is active
    if user.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active.")
    
    campaign = db.query(models.Campaigns).filter(models.Campaigns.id == campaign_id).first()

    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Campaign with id {campaign_id} not found")

    return campaign

@router.put('/{campaign_id}', status_code=status.HTTP_200_OK, tags=["Campaign"])
def update(
    campaign_id: int,
    request: schemas.UpdateCampaign,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):
    """
    Update a campaign
    :param campaign_id: int
    :param request: schemas.UpdateCampaign
    :param db: Session
    :param token: str

    :return: schemas.Campaign
    """

    account_name = utils.verify_token(token)

    user = db.query(models.Users).filter(models.Users.account_name == account_name).first()

    # Check if user is active
    if user.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active.")
    
    campaign = db.query(models.Campaigns).filter(models.Campaigns.id == campaign_id).first()

    if not campaign:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Campaign with id {campaign_id} not found")

    campaign.campaign_name = request.campaign_name
    campaign.campaign_description = request.campaign_description
    campaign.start_datetime = request.start_datetime
    campaign.end_datetime = request.end_datetime

    db.commit()

    db.refresh(campaign)

    return campaign
