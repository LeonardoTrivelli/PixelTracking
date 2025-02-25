from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
import datetime
from database import Base
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    uuid = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    surname = Column(String(255),nullable=False)
    account_name = Column(String(255), nullable=False, unique=True)
    salt = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    grant_id = Column(Integer, nullable=False, default=0)
    created_datetime = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    deleted_datetime = Column(DateTime, nullable=True, default=None)
    ## Users Relationship
    logins = relationship("Logins", back_populates="users")

class Logins(Base):
    __tablename__ = 'logins'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    login_datetime = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    login_status = Column(Integer, nullable=False, default=0)
    token = Column(String(255), nullable=True, default=None)
    token_expiry = Column(DateTime, nullable=True, default=None)

    users = relationship("Users", back_populates="logins")

class Campaigns(Base):
    __tablename__ = 'campaigns'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    campaign_name = Column(String(255), nullable=False)
    campaign_description = Column(Text, nullable=False, default=None)
    created_datetime = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    deleted_datetime = Column(DateTime, nullable=True, default=None)
    start_datetime = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    end_datetime = Column(DateTime, nullable=False, default=(datetime.datetime.utcnow() + datetime.timedelta(days=30)))

    groups = relationship("Groups", back_populates="campaigns")
    contacts = relationship("Contacts", back_populates="campaigns")

class Groups(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=False)
    campaign_group_id = Column(Integer, nullable=False)
    group_name = Column(String(255), nullable=False)
    group_description = Column(Text, nullable=True, default=None)
    created_datetime = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    deleted_datetime = Column(DateTime, nullable=True, default=None)

    campaigns = relationship("Campaigns", back_populates="groups")
    contacts = relationship("Contacts", back_populates="groups")

class Contacts(Base):
    __tablename__ = 'contacts'
    uuid = Column(String(255), primary_key=True, index=True, autoincrement=False, nullable=False)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    scheduled_datetime = Column(DateTime, nullable=False)

    groups = relationship("Groups", back_populates="contacts")
    campaigns = relationship("Campaigns", back_populates="contacts")
    pixels = relationship("Pixels", back_populates="contacts")

class Pixels(Base):
    __tablename__ = 'pixels'
    uuid = Column(String(255), primary_key=True, index=True, autoincrement=False, nullable=False)
    contact_uuid = Column(String(255), ForeignKey('contacts.uuid'), nullable=False)
    contact_pixel_number = Column(Integer, nullable=False)

    contacts = relationship("Contacts", back_populates="pixels")
    views = relationship("Views", back_populates="pixels")

class Views(Base):
    __tablename__ = 'views'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    view_datetime = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    pixel_uuid = Column(String(255), ForeignKey('pixels.uuid'), nullable=False)

    pixels = relationship("Pixels", back_populates="views")
