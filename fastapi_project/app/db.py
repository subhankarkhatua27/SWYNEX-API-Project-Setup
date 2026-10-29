import os
import logging
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

logger = logging.getLogger("swynex_api")

# Ensure .env is loaded from the app folder or project root
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./users.db"

# Translate Render / legacy PostgreSQL URI schemes to psycopg v3 driver format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# Configure connection parameters
connect_args = {}
engine_kwargs = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    engine_kwargs["connect_args"] = connect_args
else:
    # Recommended production settings for PostgreSQL on cloud hosts like Render
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300

engine = create_engine(DATABASE_URL, **engine_kwargs)
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


def init_db():
    """Initializes database schema and ensures all tables are created."""
    Base.metadata.create_all(bind=engine)


# Attempt table initialization on load; catch exceptions if DB is initializing
try:
    init_db()
except Exception as e:
    logger.warning(f"Initial schema migration deferred: {e}")
