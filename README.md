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


### 在生产环境中最佳实践部署
Gunicorn 负责进程管理、负载均衡、优雅重启。
Uvicorn 负责处理 ASGI 异步请求。
是 FastAPI 生产部署的黄金组合。

chmod +x start_server.sh
gunicorn 服务器上必须安装这个
生产环境中启动服务：
conda activate py_3_11 &&  ENV_FILE=.env.production gunicorn -c gunicorn.conf.py app.main:app
conda activate py_3_11
cd /www/wwwroot/fastapi-server
chmod +x start_server.sh

# 停止
pkill -KILL -f gunicorn

# 优雅停止所有 gunicorn 进程
pkill -TERM -f gunicorn

# 强制停止所有 gunicorn 进程
pkill -KILL -f gunicorn
