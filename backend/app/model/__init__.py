import os
import psycopg2
import logging
from sqlmodel import SQLModel, create_engine
from app.config import settings
from app.model.user_model import User
from app.model.chat_model import ChatHistory, ChatMessage
from app.model.document_model import Document, GeminiFileSearchStore

logger = logging.getLogger(__name__)

# Skip database setup in test mode
if os.environ.get("TESTING") != "true":
    DEFAULT_DB = "postgres"  # always exists by default

    conn = None
    try:
        # Connect to default database first
        conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            user=settings.POSTGRES_USER,
            dbname=DEFAULT_DB,
            password=settings.POSTGRES_PASSWORD,
            port=int(settings.POSTGRES_PORT),
        )
        conn.autocommit = True

        with conn.cursor() as cur:
            # Check if target database exists
            cur.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (settings.POSTGRES_DB,),
            )
            if not cur.fetchone():
                # Use psycopg2.sql for safe identifier quoting
                from psycopg2 import sql

                cur.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(settings.POSTGRES_DB)
                    )
                )
                cur.execute(
                    sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                        sql.Identifier(settings.POSTGRES_DB),
                        sql.Identifier(settings.POSTGRES_USER),
                    )
                )
                logger.info(f"Database {settings.POSTGRES_DB} created.")
            else:
                logger.info(f"Database {settings.POSTGRES_DB} already exists.")
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise
    finally:
        if conn is not None:
            conn.close()

    # Now connect to your actual target database
    DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

    engine = create_engine(DATABASE_URL, connect_args={"options": "-c timezone=utc"})
    SQLModel.metadata.create_all(engine)
else:
    # In test mode, create a dummy engine (will be overridden by test fixtures)
    engine = None
