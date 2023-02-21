import time
from typing import Optional, List
from fastapi import Depends, FastAPI, Response, status, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from requests import post

from sqlalchemy.orm import Session


from . import models, schemas
from .database import engine, get_db

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


@app.get("/posts/", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()

    return posts


@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    post = (
        db.query(models.Post).filter(models.Post.id == id).first()
    )  # no need to scan the rest of the table

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id={id} was not found",
        )

    return post


@app.post("/posts/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # update new_post from the database


    return new_post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    if not post_query.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id={id} does not exist",
        )

    post_query.delete(synchronize_session=False)

    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", response_model=schemas.Post) #can also use status_code=status.HTTP_204_NO_CONTENT
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    if not post_query.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id={id} does not exist",
        )

    post_query.update(updated_post.dict(), synchronize_session=False)

    db.commit()

    return post_query.first()
