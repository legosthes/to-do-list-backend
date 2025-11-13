from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/")
def read_all_items(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/items/new/")
def new_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


@app.put("/items/{item_id}/edit")
def edit_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.delete("/items/{item_id}/delete")
def delete_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}
