from fastapi import HTTPException
import os
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
import time



def establish_connection():
    return create_engine(
        f'{os.getenv("DATABASE_URL") or "postgresql://dbtype_user:zp5uFbyt5N7H28vO3d9PcAO7ng0R7n0T@dpg-cmp7l3fqd2ns738pa3h0-a.oregon-postgres.render.com/dbtype"}', 
    )

engine = establish_connection()
Session = sessionmaker(bind=engine)

session = Session()