import psycopg2
from sqlmodel import SQLModel, create_engine
from app.config import settings
from app.model.user_model import User
from app.model.chat_model import ChatHistory, ChatMessage
from app.model.document_model import Document

DEFAULT_DB = "postgres"  # always exists by default

conn = None
try:
    # Connect to default database first
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        dbname=DEFAULT_DB,
        password=settings.DB_PASSWORD,
        port=int(settings.DB_PORT),
    )
    conn.autocommit = True

    with conn.cursor() as cur:
        # Check if target database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (settings.DB_NAME,))
        if not cur.fetchone():
            cur.execute(f'CREATE DATABASE "{settings.DB_NAME}";')
            cur.execute(
                f'GRANT ALL PRIVILEGES ON DATABASE "{settings.DB_NAME}" TO "{settings.DB_USER}";'
            )
            print(f"Database {settings.DB_NAME} created.")
        else:
            print(f"Database {settings.DB_NAME} already exists.")
except Exception as e:
    print(f"Error setting up database: {e}")
    raise
finally:
    if conn is not None:
        conn.close()

# Now connect to your actual target database
DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_engine(DATABASE_URL, connect_args={"options": "-c timezone=utc"})
SQLModel.metadata.create_all(engine)
