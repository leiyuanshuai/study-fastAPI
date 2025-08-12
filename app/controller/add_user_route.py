from datetime import timedelta
from enum import Enum

from fastapi import FastAPI, Depends, HTTPException, APIRouter, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jwt import InvalidTokenError
from pydantic import BaseModel as PydanticBaseModel
from sqlmodel import select, Field
from starlette import status

from app.model.user_role import User as UserModel
from app.config.env import env
from app.model.BasicModel import BasicModel
from app.utils.CryptUtils import CryptUtils
from app.utils.db_utils import AsyncSessionDep
from app.utils.next_id import next_id

# 1: 注册用户需要哪些字段  username email password email用来激活用户 也用来注销账户(也就是删除用户)
# 2: 登录用户需要哪些字段  username  password 忘记密码只能通过邮箱去重置密码(我们向用户邮箱发送一个重置密码的)
# 3: 注册成功  应该返回那些字段给前端 PublicUser + active_url(激活链接)
# 4: 登录成功 应该返回哪些字段给前端 PublicUser + token
# 5: 获取用户信息应该返回哪些字段给前端 PublicUser

class UserValidate(str, Enum):
  active = 'active'
  inactive = 'inactive'

# 公共的，也是最后返回给前端的一个用户信息数据类型 => 接口返回用户信息类，主要是排除了哈希密码字段值；
class PublicUser(BasicModel):
  username: str = Field(..., description="用户名")
  email: str = Field(..., description="邮箱")
  status: UserValidate = Field(default=UserValidate.inactive, description="用户账号是否已经激活")


# # 注册的时候，客户端传入的用户信息，需要包含这个明文密码字段
class RegistryUser(PublicUser):
  password: str = Field(..., description="用户明文密码")

# 登录之后返回的token信息；
class Token(PydanticBaseModel):
  token: str
  token_type: str


def add_user_route(app: FastAPI, prefix: str = "/user"):
  router = APIRouter(prefix=prefix, tags=["用户登录 注册，校验用户等模块"])
  @app.post("/registry")
  async def _registry(registry_user: RegistryUser, session: AsyncSessionDep):
    # /*---------------------------------------检查用户名是否已经注册-------------------------------------------*/
    query = select(UserModel).where((UserModel.username == registry_user.username) | (UserModel.email == registry_user.email))
    item_cls = (await session.exec(query)).first()

    if item_cls:
      # 如果存在冲突的用户，构建一个错误响应
      if item_cls.username == registry_user.username:
        return {"result": None, "error": f"用户名：{registry_user.username} 已经注册", "code": 1}
      if item_cls.email == registry_user.email:
        return {"result": None, "error": f"邮箱：{registry_user.username} 已经注册", "code": 1}

    # /*---------------------------------------开始注册流程-------------------------------------------*/

    password_hash = CryptUtils.get_password_hash(registry_user.password)
    user = UserModel(
      username=registry_user.username,
      email=registry_user.email,
      password_hash=password_hash,
      status=UserValidate.inactive,
    )
    user.id = await next_id()
    session.add(user)
    await session.commit()
    await session.refresh(user)

    public_user = PublicUser(**user.model_dump())

    active_user_token = CryptUtils.create_access_token(public_user.username, expires_delta=timedelta(days=30 * 12))
    active_url = f"{env.server_domain}:{env.server_port}/verify?token={active_user_token}"
    # 注册返回token和激活链接  正常应该发送邮件去激活的，这里只是返回激活链接，前端自己处理激活逻辑
    return {
     "code": 0,
      "result": public_user,
      "active_url": active_url
    }
  # 注意这个校验的接口为/verify
  @app.get("/verify") # 激活用户，改变用户的状态为active
  async def _verify(token: str, session: AsyncSessionDep):
    username = CryptUtils.get_username_from_token(token)

    if not username:
      return {"result": None, "error": "token无效或者已经过期"}

    query = select(UserModel).where(UserModel.username == username)
    result = await session.exec(query)
    item_cls: UserModel | None = result.first()

    if not item_cls:
      return {"result": None, "error": f"用户名: {username} 不存在"}

    item_cls.status = UserValidate.active
    session.add(item_cls)
    await session.commit()
    await session.refresh(item_cls)

    public_user = PublicUser(**item_cls.model_dump())

    return {
      "result": public_user,
      "message": f"用户 {username} 激活成功"
    }


  """
  # 登录接口必须是application/x-www-form-urlencoded类型的提交，否则会报错 OAuth2PasswordRequestForm
  提交的字段为 username 和 password 这两个字段名是写死的
  grant_type=password 固定写死
  """
  @app.post("/login")
  @app.post("/token")
  async def _token(session: AsyncSessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    print("login", form_data)
    user = await authenticate_user(session, form_data.username, form_data.password)

    if not user:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="用户名或者密码不正确",
        headers={"WWW-Authenticate": "Bearer"},
      )

    token = Token(
      token=CryptUtils.create_access_token(user.username),
      token_type="Bearer",
    )

    return {
      "result": user,
      "token": token,
    }

  @router.get("/me") # 获取当前登录用户信息
  async def _me(req: Request):
    return req.state.user

  # @router.post("/order")
  # async def _query_order(product_name: str, current_user: PublicUser = Depends(get_current_user)):
  #   return [product_name]

  app.include_router(router)


async def authenticate_user(session: AsyncSessionDep, username: str, password: str):
  query = select(UserModel).where(UserModel.username == username)
  result = await session.exec(query)
  item_cls: UserModel | None = result.first()
  if not item_cls:
    return None

  if item_cls.status != UserValidate.active:
    # 用户未激活无法进行下面的步骤
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="用户注册未激活，请先到邮箱里点击链接去激活用户",
      headers={"WWW-Authenticate": "Bearer"},
    )
  # 密码不对
  if not CryptUtils.verify_password(password, item_cls.password_hash):
    return None

  public_user = PublicUser(**item_cls.model_dump())

  return public_user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

unauthorized_exception = HTTPException(
  status_code=status.HTTP_401_UNAUTHORIZED,
  detail="The token is invalid or had expired",
  headers={"WWW-Authenticate": "Bearer"},
)

#  Depends(oauth2_scheme) 这种写法默认会从请求头中获取Authorization字段的值，格式为 Bearer <token>
async def get_current_user(session: AsyncSessionDep, token: str = Depends(oauth2_scheme)):
  try:
    username = CryptUtils.get_username_from_token(token)
    if not username:
      raise unauthorized_exception
  except InvalidTokenError:
    raise unauthorized_exception

  user_model = await get_user_by_username(username, session)
  if not user_model:
    raise unauthorized_exception

  return PublicUser(**user_model.model_dump())


async def get_user_by_username(username: str, session: AsyncSessionDep):
  query = (
    select(UserModel)
    .where(UserModel.username == username)
    .where(UserModel.status == UserValidate.active)
  )
  result = await session.exec(query)
  item_cls: UserModel | None = result.first()
  return item_cls
