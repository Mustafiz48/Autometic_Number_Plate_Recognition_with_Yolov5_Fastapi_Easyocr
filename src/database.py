from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:@localhost:3306/test"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
# +"?charset=utf8mb4"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL+"?charset=utf8mb4",
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
