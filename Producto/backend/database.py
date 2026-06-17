# -*- coding: utf-8 -*-
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_USER = os.getenv('POSTGRES_USER', 'user_lexiscan')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password123')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB', 'lexiscan_db')

DATABASE_URL = os.getenv('DATABASE_URL') or (
    f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

# connect_args fuerza UTF-8 en la conexión con PostgreSQL,
# independientemente del locale del sistema operativo del equipo
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={'client_encoding': 'utf8'},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()
