from sqlalchemy import Column, Integer, String,Enum,ARRAY
from database import SessionLocal, engine, Base
from database import DATABASE_URL



class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    price = Column(Integer)
    year_published = Column(Integer)
    department = Column(String)

books=Book

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String(length=255))
    role = Column(String(length=50))
    department=Column(String(length=255))

