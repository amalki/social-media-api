import time
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from requests import post

while True:

    try:
        conn = psycopg2.connect(host='localhost', database='fastapi',
                                user='postgres', password='0000', cursor_factory=RealDictCursor)

        cursor = conn.cursor()
        print("Database connection was successful")
        break
    except Exception as error:
        print("Connection to database failed :(")
        print(f"Error: {error}")

        time.sleep(2)


class Post(BaseModel):
    title: str
    content: str
    published: Optional[bool]


app = FastAPI()


@app.get("/posts/")
def get_posts():
    cursor.execute("SELECT * FROM public.posts")

    posts = cursor.fetchall()

    print(posts[0])

    return {"data": posts}


@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute(
        """SELECT * FROM public.posts WHERE ID=%s""",
        (str(id),))

    post = cursor.fetchone()

    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id={id} was not found")

    return {"data": post}


@app.post("/posts/", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute(
        """INSERT INTO public.posts (title, content) VALUES (%s, %s) RETURNING *""",
        (post.title, post.content))

    post = cursor.fetchone()

    conn.commit()

    return {"data": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):

    cursor.execute(
        """DELETE FROM public.posts WHERE ID=%s RETURNING *""",
        (str(id),))

    deleted_post = cursor.fetchone()

    conn.commit()

    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id={id} does not exist")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def update_post(id: int, post: Post):
    cursor.execute(
        """UPDATE public.posts SET title=%s, content=%s WHERE ID=%s RETURNING *""",
        (post.title, post.content, str(id)))

    updated_post = cursor.fetchone()

    conn.commit()

    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id={id} does not exist")

    return {"data": updated_post}
