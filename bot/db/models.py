from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column, func,
    Integer, DateTime, Boolean, String
)


Base = declarative_base()


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer)
    username = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False)
    enable_notifications = Column(Boolean, default=True)
    join_date = Column(DateTime, default=func.now())


class RequestModel(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer)
    username = Column(String(255))
    created_at = Column(DateTime, default=func.now())


class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer)
    products = Column(String)

    receiving = Column(String(255))
    address = Column(String(255), nullable=True)
    code = Column(String(255), nullable=True)
    apartment_number = Column(Integer, nullable=True)
    floor_number = Column(Integer, nullable=True)
    intercom = Column(Integer, nullable=True)

    is_new = Column(Boolean, default=True)
    is_awaiting_delivery = Column(Boolean, default=False)
    is_in_delivery = Column(Boolean, default=False)
    is_delivered = Column(Boolean, default=False)

    created_at = Column(DateTime, default=func.now())
