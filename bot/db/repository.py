import os

from .models import UserModel, RequestModel, OrderModel
from .utils import get_or_create
from .engine import Session


class UserRepository:
    @staticmethod
    def create_admin():
        ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID")

        if ADMIN_TELEGRAM_ID is None:
            raise ValueError("Не указан ID администратора в .env файле.")

        with Session() as session:
            admin_user, _ = get_or_create(
                session, UserModel,
                telegram_id=ADMIN_TELEGRAM_ID, is_admin=True
            )

        return admin_user

    @staticmethod
    def get_user_by_page(page: int):
        with Session() as session:
            user = session.query(UserModel).filter(
                UserModel.is_admin == False
            ).offset((page - 1) * 1).limit(1).first()
            count = session.query(UserModel).filter(
                UserModel.is_admin == False
            ).count()
            
            next = session.query(UserModel).filter(
                UserModel.is_admin == False
            ).offset(page * 1).limit(1).first()
            next_page = None
            
            if next:
                next_page = page + 1
            
            prev = session.query(UserModel).filter(
                UserModel.is_admin == False
            ).offset((page - 2) * 1).limit(1).first()
            prev_page = None
            
            if prev:
                prev_page = page - 1
            
        return user, count, next_page, prev_page
    
    @staticmethod
    def create_user(telegram_id: int, username: str):
        with Session() as session:
            user, _ = get_or_create(session, UserModel, telegram_id=telegram_id, username=username)

        return user
    
    @staticmethod
    def delete_user(user_id: int):
        with Session() as session:
            session.query(UserModel).filter(UserModel.id == user_id).delete()
            session.commit()

    @staticmethod
    def get_admins():
        with Session() as session:
            admins = session.query(UserModel).filter(UserModel.is_admin == True).all()
        
        return admins

    @staticmethod
    def get_user_by_id(user_id):
        with Session() as session:
            user = session.query(UserModel).filter(
                UserModel.id == user_id,
            ).first()
        
        return user
    
    @staticmethod
    def get_user_by_tg_id(telegram_id):
        with Session() as session:
            user = session.query(UserModel).filter(
                UserModel.telegram_id == telegram_id,
            ).first()
        
        return user
    
    @staticmethod
    def get_users():
        with Session() as session:
            users = session.query(UserModel).all()
        
        return users


class RequestRepository:
    @staticmethod
    def get_or_create_request(telegram_id, username):
        with Session() as session:
            request, status = get_or_create(session, RequestModel, telegram_id=telegram_id, username=username)
            
        return request, status

    @staticmethod
    def get_request_by_page(page: int):
        with Session() as session:
            request = session.query(RequestModel).offset((page - 1) * 1).limit(1).first()
            count = session.query(RequestModel).count()
            
            next = session.query(RequestModel).offset(page * 1).limit(1).first()
            next_page = None
            
            if next:
                next_page = page + 1
            
            prev = session.query(RequestModel).offset((page - 2) * 1).limit(1).first()
            prev_page = None
            
            if prev:
                prev_page = page - 1
            
        return request, count, next_page, prev_page
    
    @staticmethod
    def get_request_by_id(request_id: int):
        with Session() as session:
            request = session.query(RequestModel).filter(RequestModel.id == request_id).first()

        return request

    @staticmethod
    def accept_request(request_id: int):
        with Session() as session:
            request = session.query(RequestModel).filter(RequestModel.id == request_id).first()
            UserRepository.create_user(request.telegram_id, request.username)
            
            session.delete(request)
            session.commit()
    
    @staticmethod
    def decline_request(request_id: int):
        with Session() as session:
            request = session.query(RequestModel).filter(RequestModel.id == request_id).first()
            session.delete(request)
            session.commit()


class OrderRepository:
    @staticmethod
    def create_order(order_id: int, **kwargs):
        with Session() as session:
            order = OrderModel(
                order_id=order_id,
                **kwargs,
                is_new=True
            )
            session.add(order)
            session.commit()
            
            order = session.query(OrderModel).filter(OrderModel.order_id == order_id).first()
            
        return order
            
    @staticmethod
    def get_order_by_id(order_id: int):
        with Session() as session:
            order = session.query(OrderModel).filter(
                OrderModel.id == order_id
            ).first()
        
        return order
    
    @staticmethod
    def get_new_orders():
        with Session() as session:
            orders = session.query(OrderModel).filter(
                OrderModel.is_new == True
            ).order_by("-id").all()
        
        return orders
    
    @staticmethod
    def get_awaiting_delivery_orders():
        with Session() as session:
            orders = session.query(OrderModel).filter(
                OrderModel.is_awaiting_delivery == True
            ).order_by("-id").all()
        
        return orders
    
    @staticmethod
    def get_in_delivery_orders():
        with Session() as session:
            orders = session.query(OrderModel).filter(
                OrderModel.is_in_delivery == True
            ).order_by("-id").all()
        
        return orders
    
    @staticmethod
    def get_delivered_orders():
        with Session() as session:
            orders = session.query(OrderModel).filter(
                OrderModel.is_delivered == True
            ).order_by("-id").all()
        
        return orders

    @staticmethod
    def change_order_status(order_id: int, status_name: str, status: bool):
        with Session() as session:
            order = session.query(OrderModel).filter(OrderModel.id == order_id).first()

            order.is_new = False
            order.is_awaiting_delivery = False
            order.is_in_delivery = False
            order.is_delivered = False

            setattr(order, status_name, status)

            session.commit()
            
        return order
