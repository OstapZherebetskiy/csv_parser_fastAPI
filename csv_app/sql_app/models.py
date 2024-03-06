from sqlalchemy import Column, Integer, String, Date

from csv_app.sql_app.database import Base

GENDER_CHOICES = (
    ('female', 'Male'),
    ('male', 'Female'),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, index=True)
    firstname = Column(String, index=True)
    lastname = Column(String, index=True)
    gender = Column(String, index=True)
    category = Column(String, index=True)
    birthDate = Column(Date, index=True)
