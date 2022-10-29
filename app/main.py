import time
from fastapi import FastAPI, Response, status, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from requests import post

while True:

    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='0000', cursor_factory=RealDictCursor)

        cursor = conn.cursor()
        print("Database connection was successful")
        break
    except Exception as error:
        print("Connection to database failed :(")
        print(f"Error: {error}")

        time.sleep(2)

db_posts = [{"title": "title1", "content": "content1", "id": 1},
            {"title": "title2", "content": "content2", "id": 2},
            {"title": "title3", "content": "content3", "id": 3}]


class Post(BaseModel):
    title: str
    content: str    
    published: bool = True


def post_from_db(id: int):
    """"Based on id fetch the right elemetn from the db"""

    for p in db_posts:
        if p["id"] == id:
            return p


def find_index_post(db_posts: list[dict], id: int):
    for i, p in enumerate(db_posts):
        if p["id"] == id:
            return i


app = FastAPI()


@app.get("/posts/")
def get_posts():
    cursor.execute("SELECT * FROM public.posts")

    posts = cursor.fetchall()

    print(posts[0])

    return {"data": posts}


@app.get("/posts/{id}")
def get_post(id: int):
    post = post_from_db(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id={id} was not found")

    return {"data": post}


@app.post("/posts/", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    db_posts.append(post.dict())

    return {"data": db_posts}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_index_post(db_posts, id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id={id} does not exist")

    del db_posts[index]

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def update_post(id: int, post: Post):
    index = find_index_post(db_posts, id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id={id} does not exist")

    post_dict = post.dict()
    post_dict["id"] = id

    db_posts[index] = post_dict

    return {"data": post_dict}
