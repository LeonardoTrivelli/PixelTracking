from fastapi import FastAPI
import models as models
from database import engine
from routers import users, logins, campaigns, groups, contacts, pixels, views
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTasks
from database import get_db
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import utils
import time
import datetime
import json
import database


# Create fast api instance
app = FastAPI(
    title="Pixel Tracker API",
    description="This is a simple API to track email openings of marketing campaigns.",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Your Name",
        "url": "https://your-company.com",
        "email": "your-email@your-domain.com"
    }
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
models.Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(logins.router)
app.include_router(users.router)
app.include_router(groups.router)
app.include_router(campaigns.router)
app.include_router(contacts.router)
app.include_router(pixels.router)
app.include_router(views.router)



@app.on_event("startup")
async def startup_event():
    """
    Initialize the database with a default user
    """
    try:
        SessionLocal = database.SessionLocal
        db = SessionLocal()

        with open('sample.json') as f:
            d = json.load(f)
            print(d)

        ls_admin_users = d["ls_admin_users"]
        ls_campaigns = d["ls_campaigns"]
        ls_groups = d["ls_groups"]
        ls_contacts = d["ls_contacts"]
        ls_pixels = d["ls_pixels"]
        
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

        for campaign in ls_campaigns:
            new_campaign = models.Campaigns(
                user_id = campaign["user_id"],
                campaign_name = campaign["campaign_name"],
                campaign_description = campaign["campaign_description"],
                created_datetime = datetime.datetime.strptime(campaign["created_datetime"], "%Y-%m-%d %H:%M:%S"),
                deleted_datetime = None,
                start_datetime = datetime.datetime.strptime(campaign["start_datetime"], "%Y-%m-%d %H:%M:%S"),
                end_datetime = datetime.datetime.strptime(campaign["end_datetime"], "%Y-%m-%d %H:%M:%S"),
            )

            db.add(new_campaign)
            db.commit()
            db.refresh(new_campaign)
        
        for group in ls_groups:
            new_group = models.Groups(
                campaign_id = group["campaign_id"],
                user_id = group["user_id"],
                campaign_group_id = group["campaign_group_id"],
                group_name = group["group_name"],
                group_description = group["group_description"],
                created_datetime = datetime.datetime.strptime(group["created_datetime"], "%Y-%m-%d %H:%M:%S"),
                deleted_datetime = None
            )
            db.add(new_group)
            db.commit()
            db.refresh(new_group)
        
        for contact in ls_contacts:
            new_contact = models.Contacts(
                uuid = contact["uuid"],
                campaign_id = contact["campaign_id"],
                group_id = contact["group_id"],
                scheduled_datetime = datetime.datetime.strptime(contact["scheduled_datetime"], "%Y-%m-%d %H:%M:%S")
            )
            db.add(new_contact)
            db.commit()
            db.refresh(new_contact)
        
        for pixel in ls_pixels:
            new_pixel = models.Pixels(
                uuid = pixel["uuid"],
                contact_uuid = pixel["contact_uuid"],
                contact_pixel_number = pixel["contact_pixel_number"]
            )
            db.add(new_pixel)
            db.commit()
            db.refresh(new_pixel)
    except Exception as e:
        print(f"Error in insert: {e}")