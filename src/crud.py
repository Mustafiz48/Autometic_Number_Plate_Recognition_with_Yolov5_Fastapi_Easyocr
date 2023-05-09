from sqlalchemy.orm import Session

import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()


def get_user_by_license(db: Session, license_number: str):
    return db.query(models.User).join(models.Car).filter(models.Car.license_number == license_number).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        name=user.name,
        phone=user.phone,
        designation=user.designation,
        department=user.department,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_cars(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Car).offset(skip).limit(limit).all()


def get_car_by_license(db: Session, license_number: str):
    return db.query(models.Car).filter(models.Car.license_number == license_number).first()


def create_user_car(db: Session, car: schemas.CarCreate, user_id: int):
    db_car = models.Car(**car.dict(), user_id=user_id)
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car
