import psycopg2
from fastapi import APIRouter, Depends
from sqlmodel import SQLModel, create_engine
from app.config import settings
from app.model.user import User

try:
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        dbname=settings.DB_NAME,
        password=settings.DB_PASSWORD,
        port=int(settings.DB_PORT),
    )

    conn.autocommit = True

    with conn.cursor() as cur:
        cur.execute("SELECT 1 from pg_database where datname = %s", (settings.DB_NAME,))
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {settings.DB_NAME};")
            cur.execute(
                f"GRANT ALL PRIVILEGES ON DATABASE {settings.DB_NAME} TO {settings.DB_USER};"
            )
        else:
            print(f"Database {settings.DB_NAME} already exists.")

finally:
    conn.close()

DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_engine(DATABASE_URL, connect_args={"options": "-c timezone=utc"})
SQLModel.metadata.create_all(engine)
