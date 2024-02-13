from fastapi import HTTPException
import os
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
import time


def establish_connection():
    return create_engine(
        f'{os.getenv("DATABASE_URL") or "postgresql://RRHHBaseLang:Z3SPEOQj8wvs@ep-icy-math-a58907mm.us-east-2.aws.neon.tech/neondb"}',
        connect_args={'sslmode': 'allow'}

    )


engine = establish_connection()
Session = sessionmaker(bind=engine)

session = Session()
