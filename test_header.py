from datetime import datetime, time, timedelta

from typing import List, Union, Annotated, Literal
from uuid import UUID
import asyncio
from fastapi.params import Cookie
from fastapi import FastAPI, Query, Path, Body, Header
from enum import Enum
from pydantic import BaseModel, Field,HttpUrl
app = FastAPI()
# Query和Path都只是一个函数类型
# print('Path',type(Path))
# print('Query',type(Query))
# 路径参数


@app.get("/items/")
async def read_items(user_agent: Annotated[str | None, Header()] = None):
    return {"User-Agent": user_agent}
