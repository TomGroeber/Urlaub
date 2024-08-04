from sqlalchemy import create_engine, Column, Integer, String, Date, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///vacation_manager.db')

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    vacation_days = Column(Integer)
    role = Column(String)

class Vacation(Base):
    __tablename__ = 'vacations'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String, default='pending')
    note = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)
