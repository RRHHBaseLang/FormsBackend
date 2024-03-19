from fastapi import HTTPException
import os
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
import time


def establish_connection():
    return create_engine(
        f'{os.getenv("DATABASE_URL") or "postgresql://postgres:postgres@localhost/blforms"}',
        connect_args={'sslmode': 'allow'}

    )


engine = establish_connection()
Session = sessionmaker(bind=engine)

session = Session()
