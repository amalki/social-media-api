from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel


db_posts = [{"title": "title1", "content": "content1", "id": 1},
            {"title": "title2", "content": "content2", "id": 2},
            {"title": "title3", "content": "content3", "id": 3}]


class Post(BaseModel):
    title: str
    content: str
    id: int
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
    return {"data": db_posts}


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

    return {"message": "post was successfully deleted"}
