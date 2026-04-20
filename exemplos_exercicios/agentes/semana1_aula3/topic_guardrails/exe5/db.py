from sqlalchemy import create_engine

DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5432/suporte_ai"


def get_engine():
    return create_engine(DB_URL)