# from fastapi import FastAPI, HTTPException
#
# from app.model.user_role import User, Role, UserRolesLink
# from app.utils.db_utils import AsyncSessionDep, is_super_admin_by_role_id
#
# from fastapi import APIRouter, FastAPI
#
# from app.utils.next_id import next_id
# from sqlmodel import select
# from pydantic import BaseModel, Field
#
#
# class CreateRole(BaseModel):
#   name: str = Field(..., description="角色名称")
#   username: str = Field(..., description="用户名称")
#
#
# def add_test_sqlmodel_crud_route(app: FastAPI, prefix: str = "/test_sqlmodel_crud_route"):
#   router = APIRouter(prefix=prefix, tags=["测试sqlmodel的crud操作"])
#
#   # @router.get("/searchUserByUsername")
#   # async def search_user_by_username(username: str, session: AsyncSessionDep):
#   #   query = select(User).where(User.username == username)
#   #   user = (await session.exec(query)).first()
#   #   return {"user": user}
#   #
#   # @router.get("/searchUserById")
#   # async def search_user_by_id(id: str, session: AsyncSessionDep):
#   #   query = select(User).where(User.id == id)
#   #   user = (await session.exec(query)).first()
#   #   return {"user": user}
#   #
#   # @router.get("/searchUserByEmail")
#   # async def search_user_by_email(email: str, session: AsyncSessionDep):
#   #   query = select(User).where(User.email == email)
#   #   user = (await session.exec(query)).first()
#   #   # print(f'roles:{user.username}', user.roles[0].name)
#   #   return {"user": user}
#   #
#   # @router.get("/searchUserByPhone")
#   # async def search_user_by_phone(phone: str, session: AsyncSessionDep):
#   #   query = select(User).where(User.phone == phone)
#   #   user = (await session.exec(query)).first()
#   #   return {"user": user}
#
#   @router.post("/insertUser")
#   async def insert_user(user: User, session: AsyncSessionDep, role_ids: list[str] | None = None):
#     query = select(User).where((User.username == user.username) | (User.email == user.email) |(User.phone == user.phone))
#     exist_user = (await session.exec(query)).first()
#
#     if exist_user:
#       # 如果存在冲突的用户，构建一个错误响应
#       error_details = []
#       if exist_user.username == user.username:
#         error_details.append("username")
#       if exist_user.email == user.email:
#         error_details.append("email")
#       if exist_user.phone == user.phone:
#         error_details.append("phone")
#       error_msg = f"User with the following fields already exists: {', '.join(error_details)}"
#       raise HTTPException(status_code=400, detail={
#         "message": error_msg,
#         "code": 500
#       })
#       #
#       # 设置用户的ID为下一个可用的ID（如果尚未设置）
#     if user.id is None:
#       user.id = await next_id()
#
#     if role_ids is  None: # 这里先简单写下
#       role_ids = ['bedbdfc8-d170-4b22-94f9-dc83498e030f']  # 默认角色ID
#
#       # 添加新用户到会话，并提交更改
#     session.add(user)
#
#       # 3. 创建中间表关联
#     for role_id in role_ids:
#       link = UserRolesLink(user_id=user.id, role_id=role_id)
#       session.add(link)
#
#     await session.commit()
#     await session.refresh(user)
#
#     # 返回成功创建的用户信息
#     return {"user": user}
#
#   @router.post("/updateUser")
#   async def update_user_info(user: dict, session: AsyncSessionDep):
#     # 先查询要更新的对象
#     update_user = (await session.exec(select(User).where(User.id == user.get('id')))).first()
#     if not update_user:
#       raise HTTPException(status_code=500, detail="用户不存在")
#
#     # 按字段更新需要的字段
#     for key, value in user.items():
#       setattr(update_user, key, value)
#
#     session.add(update_user)
#     await session.commit()
#     await session.refresh(update_user)
#
#     return {"result": update_user}
#
#   @router.post("/deleteUser")
#   async def delete_user(user: dict, session: AsyncSessionDep):
#     # 先查询要删除的对象
#     query = select(User).where(User.id == user.get('id'))
#     del_user = (await session.exec(query)).first()
#     if not del_user:
#       raise HTTPException(status_code=500, detail="用户不存在")
#
#     # 删除用户
#     session.delete(del_user)
#     await session.commit()
#
#     return {"result": "删除成功"}
#
#   async def is_admin(username: str, session: AsyncSessionDep):
#     query = select(User).where(User.username == username)
#     user = (await session.exec(query)).first()
#     if not user:
#       raise HTTPException(status_code=400, detail={
#         "message": f"用户名{username}不存在",
#         "code": 200
#       })
#     # 获取所有关联角色的ID
#     link_query = select(UserRolesLink).where(UserRolesLink.user_id == user.id)
#     result = (await session.exec(link_query)).all()
#     for role in result:
#       if is_super_admin_by_role_id(role.role_id):
#         return True
#     return False
#
#   @router.post("/insertRole")
#   async def insert_role(role: CreateRole, session: AsyncSessionDep):
#     if role.username is None:
#       raise HTTPException(status_code=400, detail={
#         "message": "用户名不能为空",
#         "code": 200
#       })
#     is_super_admin = await is_admin(role.username, session)
#     if not is_super_admin:
#       raise HTTPException(status_code=400, detail={
#         "message": "只有超级管理员才能创建角色",
#         "code": 200
#       })
#     # 判断用户是否是超级管理员，只有超级管理员才可以创建角色
#     query = select(Role).where(Role.name == role.name)
#     exist_role = (await session.exec(query)).first()
#
#     if exist_role:
#       error_msg = f"角色{role.name}已经存在啦"
#       raise HTTPException(status_code=200, detail={
#         "message": error_msg,
#         "code": 200
#       })
#
#       # 设置用户的ID为下一个可用的ID（如果尚未设置）
#     add_role_id = await next_id()
#     add_role = Role(id=add_role_id, name=role.name)
#
#       # 添加新用户到会话，并提交更改
#     session.add(add_role)
#     await session.commit()
#     await session.refresh(add_role)
#
#     # 返回成功创建的用户信息
#     return {"role": add_role}
#
#
#   app.include_router(router)
#
