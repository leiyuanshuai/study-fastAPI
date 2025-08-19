# Gunicorn 配置文件
import multiprocessing
import os
from dotenv import load_dotenv
# 加载环境变量
env_file = os.getenv("ENV_FILE", ".env.production")
load_dotenv(env_file)

# 服务器套接字设置 - 使用环境变量中的端口
server_port = os.getenv("SERVER_PORT", "7002")
bind = f"0.0.0.0:{server_port}"


pidfile = "./logs/gunicorn.pid"

# 工作进程数 - 通常设置为 CPU 核心数
# workers = multiprocessing.cpu_count() * 2 + 1
workers = 1 # 为了避免把自己的内存占用过多
# 工作进程类 - 使用 Uvicorn 工作进程以支持 ASGI
worker_class = "uvicorn.workers.UvicornWorker"

# 工作进程连接数限制
worker_connections = 1000

# 设置守护进程后台运行（可选）
daemon = True

# 进程名
proc_name = "fastapi_app"

# 日志级别
loglevel = "info"

# 日志文件路径 - 使用相对路径或确保目录存在
accesslog = "./logs/gunicorn_access.log"
errorlog = "./logs/gunicorn_error.log"

# 确保日志目录存在
if not os.path.exists("logs"):
    os.makedirs("logs")

# 访问日志格式
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 设置工作进程超时时间（秒）
timeout = 120

# 优雅地重启工作进程的超时时间
graceful_timeout = 30

# 重启工作进程前处理的请求数
max_requests = 1000

# 重启工作进程前处理请求数的抖动范围
max_requests_jitter = 100

# 预加载应用
preload_app = True

