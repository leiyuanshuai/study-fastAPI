from typing import List

from fastapi import FastAPI
from enum import Enum

from pydantic import BaseModel

app = FastAPI()

@app.get("/item/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}

# 测试路径demo为: http://127.0.0.1:8000/files//home/johndoe/myfile.txt
@app.get("/files/{file_path:path}")
# :path 表示可以匹配任意路径，包括斜杠和文件名
async def read_file(file_path: str):
# file_path = "/home/johndoe/myfile.txt" file_path的值是除了http://127.0.0.1:8000/files/之外的路径
    return {"file_path": file_path, "name": "leichao"}

@app.get("/test/{file_path}")
async def test_path(file_path: str):
    return {"file_path": file_path, "name": "test_path"}

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

# 测试查询参数和路径参数混合使用 默认 优先级路径参数 > 查询参数
@app.get("/modifyUserInfo/{user_id}")
async def modify_user_info(user_id: str, name: str = "John Doe", age: int = 25,is_admin:bool = False, limit: int | None = None):
    print(user_id)
    print(name)
    print(age)
    return {"user_id": user_id, "name": name, "age": age, "is_admin":is_admin, "limit": limit}


# 请求体参数
class UserInfo(BaseModel):
    name: str = 'John Doe'
    age: int
    tax: float | None = None
    price: float
    interests: List[str]

@app.post("/addUserInfo")
async def modify_user_info(item:UserInfo):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        # 字典更新某个健的方法
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

# 请求体+路径参数
@app.post("/updateUserInfo/{user_id}")
async def modify_user_info(item:UserInfo, user_id: str):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        # 字典更新某个健的方法
        item_dict.update({"price_with_tax": price_with_tax})
    item_dict.update({"user_id": user_id})
    return item_dict

# 测试 路径参数+查询参数+请求体参数
@app.put("/putUserInfo/{user_id}")
async def update_item(user_id: int, item: UserInfo, qs: str | None = None):
    result = {"user_id": user_id, **item.dict()}
    if qs:
        result.update({"qq": qs})
    return result

@app.get("/")
async def root():
    return {"message": "Hello World"}
