from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from typing import Optional
import datetime

class AddUser(BaseModel):
    name: str
    surname: str
    account_name: str
    password: str
    email: str
    grant_id: int

class AddCampaign(BaseModel):
    campaign_name: str
    campaign_description: str
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime

class AddContact(BaseModel):
    uuid: str
    campaign_id: int
    group_id: int
    scheduled_datetime: datetime.datetime

class UpdateContact(BaseModel):
    campaign_id: int
    group_id: int
    scheduled_datetime: datetime.datetime

class AddGroup(BaseModel):
    campaign_id: int
    group_name: str
    group_description: str
    campaign_group_id: int

class UpdateGroup(BaseModel):
    campaign_group_id: int
    group_name: str
    group_description: str
    campaign_group_id: int

class UpdateCampaign(BaseModel):
    campaign_name: str
    campaign_description: str
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime

class AddPixel(BaseModel):
    contact_uuid: str
    contact_pixel_number: int

class AddView(BaseModel):
    view_datetime: datetime.datetime
    pixel_uuid: str