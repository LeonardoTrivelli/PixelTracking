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
    prefix="/pixel",
    tags=["Pixel"]
)

@router.post('/', status_code=status.HTTP_201_CREATED, tags=["Pixel"])
def add(
    request: schemas.AddPixel,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)):
    """
    Add a new pixel to contact
    :param request: schemas.AddPixel
    :param db: Session
    :param token: str

    :return: schemas.AddPixel
    """

    account_name = utils.verify_token(token)

    user = db.query(models.Users).filter(models.Users.account_name == account_name).first()

    # Check if user is active
    if user.deleted_datetime:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active.")
    
    # Check if the contact exists
    contact = db.query(models.Contacts).filter(models.Contacts.uuid == request.contact_uuid).first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Contact with uuid {request.contact_uuid} not found.")
    
    # Check if contact pixel exists, if it does, raise an error
    contact_pixel = db.query(models.Pixels).filter((models.Pixels.contact_uuid == request.contact_uuid) & (models.Pixels.contact_pixel_number == request.contact_pixel_number)).first()

    if contact_pixel:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Contact with uuid {request.contact_uuid} already has pixel number {request.contact_pixel_number}.")

    new_pixel = models.Pixels(
        uuid = utils.generate_uuid4(),
        contact_uuid = request.contact_uuid,
        contact_pixel_number = request.contact_pixel_number
    )

    db.add(new_pixel)
    db.commit()
    db.refresh(new_pixel)

    response = JSONResponse(
        content={
            "message": "Pixel created successfully",
            "uuid": new_pixel.uuid
        },
        status_code=status.HTTP_201_CREATED
    )

    return response

@router.get('/{uuid}', tags=["Pixel"])
def get(
    request: Request,
    uuid: str,
    db: Session = Depends(get_db)):
    """
    Get a pixel by uuid
    :param uuid: str
    :param db: Session

    :return: schemas.GetPixel
    """

    utils.write_pixel()

    # Check if the pixel exists in redis
    from_redis = utils.get_from_redis(key=uuid)

    if from_redis:
        return FileResponse("tracking_pixel.gif", media_type="image/gif")
    else:
        utils.save_to_redis(key=uuid, value=request.client.host)

        # Check if pixel exists
        pixel = db.query(models.Pixels).filter(models.Pixels.uuid == uuid).first()
        if not pixel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pixel with uuid {uuid} not found.")
    
        # Check if views already exists
        views = db.query(models.Views).filter(models.Views.pixel_uuid == pixel.uuid).all()
        if not views:
            # Add a View
            new_view = models.Views(
                view_datetime = datetime.datetime.utcnow(),
                pixel_uuid = pixel.uuid
            )
    
            db.add(new_view)
            db.commit()
            db.refresh(new_view)

        return FileResponse("tracking_pixel.gif", media_type="image/gif")
    

@router.get('/', tags=["Pixel"])
def get_all(
    db: Session = Depends(get_db)):
    """
    Get all pixels
    :param db: Session

    :return: schemas.GetPixel
    """
    pixels = db.query(models.Pixels).all()
    
    return pixels