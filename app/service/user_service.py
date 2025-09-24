from app.model.user import User
from app.model import engine
from sqlmodel import Session, select
from pydantic import BaseModel


class UserService:
    def __init__(self):
        pass

    @staticmethod
    def create_user(user_to_create: User) -> User:
        with Session(engine) as session:
            session.add(user_to_create)
            session.commit()
            session.refresh(user_to_create)
        return user_to_create
