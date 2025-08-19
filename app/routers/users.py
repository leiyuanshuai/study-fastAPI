from fastapi import APIRouter, FastAPI


def add_users_router(app: FastAPI, prefix: str = "/users"):
  router = APIRouter(prefix=prefix, tags=["测试users模块"])

  @router.get("/list", )
  async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]

  @router.get("/about", )
  async def read_user_me():
    return {"username": "fakecurrentuser"}

  @router.get("/{username}", )
  async def read_user(username: str):
    return {"username": username}

  app.include_router(router)






