from sqlmodel import SQLModel, Field, Column
from app.utils import snowflake_generator, get_timestamp
from sqlalchemy import BigInteger

class Chat(SQLModel, table=True):
    __tablename__ = "chat"
    id: int = Field(
        sa_column=Column(BigInteger, primary_key=True, autoincrement=False),
        default_factory=snowflake_generator,
    )
    name: str
    message: str
    created_at: int = Field(default_factory=get_timestamp)