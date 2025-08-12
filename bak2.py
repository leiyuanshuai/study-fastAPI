from datetime import datetime, time, timedelta

from typing import List, Union, Annotated, Literal
from uuid import UUID

from fastapi import FastAPI, Query,Path, Body
from enum import Enum
from pydantic import BaseModel, Field,HttpUrl

app = FastAPI()
# Query和Path都只是一个函数类型
# print('Path',type(Path))
# print('Query',type(Query))
# 路径参数
"""
@app.get("/item/{item_id}")
async def read_items(
 item_id: Annotated[int, Path(description="查询item_id")],  name: Annotated[str | None, Query(max_length=50, alias="itemName")]):
  results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
  if name:
    results.update({"name": name})
  # 路径参数总是必填，所以即便我们设置不是必填的，也是无效的
  results.update({"item_id": item_id})
  return results

"""
"""
# 复杂的多个查询参数
class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []


@app.get("/test-query-params/")
async def test_query_params(filter_query: Annotated[FilterParams, Query()]):
  return filter_query
"""

"""
class Item(BaseModel):
  name: str
  description: str | None = None
  price: float
  tax: float | None = None

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
  results = {"item_id": item_id, "item": item}
  return results
"""

"""
class Item(BaseModel):
  name: str = Field(..., min_length=3, max_length=50, description="The name of the item")
  description: str | None = Field(
    default=None, title="The description of the item", max_length=300
  )
  price: float = Field(gt=0, description="The price must be greater than zero")
  tax: float | None = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
  results = {"item_id": item_id, "item": item}
  return results
"""


"""
class Item(BaseModel):
  name: str
  description: str | None = None
  price: float
  tax: float | None = None
  tags: set[str] = set()


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
  results = {"item_id": item_id, "item": item}
  return results
"""


class Image(BaseModel):
  url: HttpUrl
  name: str


class Item(BaseModel):
  name: str
  description: str | None = None
  price: float
  tax: float | None = None
  tags: set[str] = set()
  image: Image | None = None


"""
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
  results = {"item_id": item_id, "item": item}
  return results

@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images

"""
@app.put("/items/{item_id}")
async def read_items(
    item_id: UUID,
    start_datetime: Annotated[datetime, Body()],
    end_datetime: Annotated[datetime, Body()],
    process_after: Annotated[timedelta, Body()],
    repeat_at: Annotated[time | None, Body()] = None,
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "process_after": process_after,
        "repeat_at": repeat_at,
        "start_process": start_process,
        "duration": duration,
    }

@app.get("/")
async def root():
    return {"message": "Hello World"}
