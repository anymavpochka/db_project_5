from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
import connection_to_db
from connection_to_db import engine
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Users(Base):

    __tablename__ = 'Users'

    email = Column(String(30), primary_key=True)
    password = Column(String(80))
    name = Column(String(30))
    birthday = Column(Date)
    total_order_amount = Column(Integer)
    discount = Column(Integer)
    UniqueConstraint(email)

class Menu(Base):

    __tablename__ = 'Menu'

    item_id = Column(Integer, primary_key=True)
    item = Column(String(30))
    price = Column(Integer)
    promotion = Column(Integer)


class Reservation(Base):

    __tablename__ = 'Reservation'

    reserv_id = Column(Integer, primary_key=True)
    email = Column(String(30))
    name = Column(String(30))
    table = Column(Integer)
    date = Column(Date)
    time = Column(String(30))
    reserv_status = Column(Integer)
    UniqueConstraint(email)


class Review(Base):

    __tablename__ = 'Review'

    comment_id = Column(Integer, primary_key=True)
    email = Column(String(30))
    name = Column(String(30))
    comment = Column(String(70))
    date = Column(String(30))


class Order(Base):
    __tablename__ = 'Order'

    order_id = Column(Integer, primary_key=True)
    email = Column(String(30))
    item_id = Column(Integer)
    item = Column(String(30))
    table = Column(Integer)
    order_status = Column(Integer)


class Prediction(Base):
    __tablename__ = 'Prediction'

    id = Column(Integer, primary_key=True)
    date = Column(String(30))
    number = Column(Integer)


Base.metadata.create_all(engine)
