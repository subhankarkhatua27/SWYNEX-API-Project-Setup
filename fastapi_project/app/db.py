import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    from .tables import Base
except ImportError:
    try:
        from app.tables import Base
    except ImportError:
        from tables import Base

# Ensure .env is loaded from the app folder or project root
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Ensure tables exist
Base.metadata.create_all(bind=engine)