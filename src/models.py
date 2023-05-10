from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    license_number = Column(String(512), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="car")


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), index=True)
    phone = Column(String(64), index=True)
    designation = Column(String(64), index=True)
    department = Column(String(64), index=True)
    car = relationship("Car", back_populates="owner")


class Guest(Base):
    __tablename__ = "guest"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), index=True)
    phone = Column(String(64), index=True)
    license_number = Column(String(512), index=True)

    
