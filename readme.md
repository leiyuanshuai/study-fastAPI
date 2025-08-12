### 函数参数按如下规则进行识别：
```aiignore
# 测试 路径参数+查询参数+请求体参数
@app.put("/putUserInfo/{user_id}")
async def update_item(user_id: int, item: UserInfo, qs: str | None = None):
    result = {"user_id": user_id, **item.dict()}
    if qs:
        result.update({"qq": qs})
    return result
```
`路径中声明了相同参数的参数，是路径参数
类型是（int、float、str、bool 等）单类型的参数，是查询参数
类型是 Pydantic 模型的参数，是请求体`


conda install -c conda-forge psycopg
