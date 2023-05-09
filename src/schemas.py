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


class New_User(BaseModel):
    name: str
    phone: str
    designation: str
    department: str

    class Config:
        orm_mode = True