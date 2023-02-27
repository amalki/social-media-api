import time
from typing import List
from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor

from . import models
from .database import engine
from .routers import posts, users


models.Base.metadata.create_all(bind=engine)


while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapi",
            user="postgres",
            password="0000",
            cursor_factory=RealDictCursor,
        )

        cursor = conn.cursor()
        print("Database connection was successful")
        break
    except Exception as error:
        print("Connection to database failed :(")
        print(f"Error: {error}")

        time.sleep(2)


app = FastAPI()

app.include_router(posts.router)
app.include_router(users.router)
