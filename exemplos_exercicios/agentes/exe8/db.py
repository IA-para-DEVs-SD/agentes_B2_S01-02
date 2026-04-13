import os
from sqlalchemy import create_engine

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5455")
DB_URL = f"postgresql+psycopg2://admin:admin123@{DB_HOST}:{DB_PORT}/suporte_ai"


def get_engine():
    return create_engine(DB_URL)
