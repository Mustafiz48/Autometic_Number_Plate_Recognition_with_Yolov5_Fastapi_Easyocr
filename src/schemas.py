from pydantic import BaseModel


class CarBase(BaseModel):
    license_number: str


class CarCreate(CarBase):
    pass


class Car(CarBase):
    id: int
    is_allowed: bool
    user_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    name: str
    phone: str
    designation: str
    department: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    car: list[Car] = []

    class Config:
        orm_mode = True



class Guest_Base(BaseModel):
    name: str
    phone: str
    license_number: str
    reference: str

class Guest_Create(Guest_Base):
    pass

class Guest(Guest_Base):
    id: int
    class Config:
        orm_mode = True