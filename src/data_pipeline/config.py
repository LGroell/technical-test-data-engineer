import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# env variables
API_URL = os.getenv("API_URL", "http://localhost:8000")
DB_URL = os.getenv("DB_URL", "sqlite:///music_database.db")

# logger config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# Create db session
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
