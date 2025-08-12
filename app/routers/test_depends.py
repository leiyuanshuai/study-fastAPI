from fastapi import APIRouter, FastAPI, Depends, Cookie, Header, HTTPException

from typing import  Annotated
def add_depends_router(app: FastAPI, prefix: str = "/test_depends"):



  router = APIRouter(prefix=prefix, tags=["测试依赖项模块"])
  # 函数作为依赖项
  async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    """
    依赖项一般都是函数 依赖项应该是 "可调用对象"。
    python中的类也是"可调用对象"
    :param q:
    :param skip:
    :param limit:
    :return:
    """
    return {"q": q, "skip": skip, "limit": limit}

  fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

  @router.get("/items/fn")
  async def read_items(commons: dict = Depends(common_parameters)):
    return commons

  class CommonQueryParams:
      def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit
  # 类作为依赖项
  @router.get("/items/cls")
  # async def read_items_cls(commons: CommonQueryParams = Depends(CommonQueryParams)):
  # 下面这行代码是对上面的简写形式
  async def read_items_cls(commons: CommonQueryParams = Depends()):

    response = {}
    if commons.q:
      response.update({"q": commons.q})
    items = fake_items_db[commons.skip: commons.skip + commons.limit]
    response.update({"items": items})
    return response
  # 下面是演示多层嵌套依赖项的写法
  def query_extractor(q: str | None = None):
      print("query_extractor called", q)
      return q
  # Depends依赖于其函数返回值
  def query_or_cookie_extractor(
    q: Annotated[str, Depends(query_extractor)],
    last_query: Annotated[str | None, Cookie()] = None,
    # 下面是低版本的写法3.10以下版本的写法
    # q: str = Depends(query_extractor),
    # last_query: Union[str, None] = Cookie(default=None)
  ):
    if not q:
      return last_query
    return q

  @router.get("/items/deep")
  async def read_query(
    query_or_default: Annotated[str, Depends(query_or_cookie_extractor)],
  ):
    return {"q_or_cookie": query_or_default}

  async def verify_token(x_token: str = Header()):
      if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")

  async def verify_key(x_key: str = Header()):
    if x_key != "fake-super-secret-key":
      raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key # 这里没用,不会传递给用到此依赖项的 => 路径操作函数

  # dependencies 依赖项列表不依赖于Depends的返回值, 他们的返回值也没用不会传递过来
  @router.get("/items/dependencies", dependencies=[Depends(verify_token), Depends(verify_key)])
  async def read_items_dependencies():
    return [{"item": "Foo"}, {"item": "Bar"}]
  # 也可以给一组路由添加依赖项
  app.include_router(router)






