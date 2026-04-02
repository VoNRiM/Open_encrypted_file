from sqlalchemy import create_engine,text
from sqlalchemy.orm import declarative_base
from loguru import logger

logger.add("debug.log",
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message} | {function}",
           level="DEBUG",
           rotation="10 MB",
           retention=5,
           encoding="utf-8")

DATABASE_URL = "postgresql://postgres:12345@localhost:5432/postgres"
engine = create_engine(
    DATABASE_URL,
    echo=True
)
Base = declarative_base()

with engine.connect() as conn:
    conn.execute(text("commit"))
    try:
        conn.execute(text("CREATE DATABASE access_db"))
        logger.success("База данных создана")
    except Exception as e:
        if "already exists" in str(e):
            logger.info("Ошибка: База данных уже существует")
        else:
            logger.error(f"Неизвестная ошибка: {e}")
    try:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        conn.commit()
        logger.info("Добавление trgm")
    except Exception as e:
        logger.error(f"Неизвестная ошибка добавления trgm{e}")

