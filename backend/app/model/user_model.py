from sqlmodel import Field, SQLModel, Column, BigInteger
from app.utils import snowflake_generator, get_timestamp


class User(SQLModel, table=True):
    __tablename__ = "user"
    id: int = Field(
        sa_column=Column(BigInteger, primary_key=True, autoincrement=False),
        default_factory=snowflake_generator,
    )
    username: str
    password: bytes 
    is_superuser: bool
    created_at: int = Field(default_factory=get_timestamp)
