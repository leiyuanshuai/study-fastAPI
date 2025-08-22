from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html, get_redoc_html
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.config.env import env


from app.utils.db_utils import check_database_connection
from app.utils.postgres_checkpointer import check_postgres_connection


def create_app():
  @asynccontextmanager
  async def lifespan(app: FastAPI):
    print("lifespan：应用启动阶段")
    async_engine = await check_database_connection()
    await check_postgres_connection()
    yield
    print("lifespan：应用销毁阶段")
    await async_engine.dispose()

  app = FastAPI(
    docs_url=None,  # 禁用默认 Swagger
    redoc_url=None,  # 禁用默认 ReDoc
    # 下面是添加全局依赖项
    # dependencies=[Depends(verify_token), Depends(verify_key)],
    lifespan=lifespan,
  )
  # 定义项目静态文件根目录 或者挂载子应用
  app.mount("/static", StaticFiles(directory="static"), name="static")

  # 自定义 Swagger 页面（使用本地资源）
  @app.get("/docs", include_in_schema=False)
  async def custom_swagger_ui():
    return get_swagger_ui_html(
      openapi_url=app.openapi_url,
      title=app.title + " - Swagger UI",
      oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
      swagger_js_url="/static/swagger-ui-bundle.min.js",
      swagger_css_url="/static/swagger-ui.min.css",
    )

  @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
  async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

  @app.get("/redoc", include_in_schema=False)
  async def redoc_html():
    return get_redoc_html(
      openapi_url=app.openapi_url,
      title=app.title + " - ReDoc",
      redoc_js_url="/static/redoc.standalone.js",
    )

  app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
  )

  # @app.get("/get_env")
  # async def test():
  #   return env.model_dump_json()

  @app.get("/test2")
  async def test():
    return {"msg": "hello"}

  return app
