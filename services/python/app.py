from fastapi import FastAPI
import models as models
#import schemas as schemas
from database import engine
#from routers import login
from routers import init, users, logins, campaigns, groups, contacts, pixels
from fastapi.middleware.cors import CORSMiddleware

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
app.include_router(init.router)
app.include_router(groups.router)
app.include_router(campaigns.router)
app.include_router(contacts.router)
app.include_router(pixels.router)