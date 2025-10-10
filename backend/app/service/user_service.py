from app.model.user import User
from app.model import engine
from sqlmodel import Session, select
import bcrypt

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

    @staticmethod
    def hash_the_password(password: str) -> bytes:
        password = bytes(password, "utf-8")
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        return hashed_password

    @staticmethod
    def verify_password(password: str, hashed_password: bytes) -> bool:
        password = bytes(password, "utf-8")
        return bcrypt.checkpw(password, hashed_password)

    @staticmethod
    def get_user_by_username(username: str) -> User | None:
        with Session(engine) as session:
            statement = select(User).where(User.username == username)
            result = session.exec(statement).first()  # fetch one row or None
        return result
