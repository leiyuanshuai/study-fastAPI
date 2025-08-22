from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langserve import add_routes
from app.config.env import env
from app.controller.add_langgraph_route import add_langgraph_route
from app.controller.add_redis_route import add_redis_route
from app.controller.add_user_route import add_user_route
from app.create_app import create_app
from app.middlewares.app_middlewares import add_app_middlewares
from app.model.LgChat import LgChatService
from app.routers.test_depends import add_depends_router
from app.routers.users import add_users_router
from app.routers.test_BackgroundTasks import background_task
from app.routers.test_origin_sql_query import add_origin_sql_query_route
from app.utils.ModelInputSchema import ModelInputSchema
from app.utils.add_async_route import add_async_route

# from app.routers.test_sqlmodel_crud import add_test_sqlmodel_crud_route
from app.utils.create_module_service import create_model_service
from app.controller.add_lg_approve_route import add_lg_approve_route
from app.controller.add_langgraph_approve_route import add_langgraph_approve_route
from app.controller.add_langgraph_chat_route import add_langgraph_chat_route
from app.model.LgApprove import LgApproveService
from app.model.LgMessage import LgMessageService
from app.model.LlmOrder import LlmOrder, LlmOrderService
from app.model.LlmProduct import LlmProduct, LlmProductService
from app.model.LgChat import LgChatService

from app.model.user_role import Role
from app.utils.llm_utils import create_llm

# create_app初始化doc文档本地化，设置静态文件根目录，设置数据库连接等。
app = create_app()
add_app_middlewares(app)

# 注意这个background_task必须是同步的，不能是异步的，否则会报错。
background_task(app, prefix="/test_background_tasks")
add_users_router(app, prefix="/users")
# 用户登录 注册，校验用户等模块
add_user_route(app, prefix="/user")
add_depends_router(app, prefix="/depends")
# 测试原生SQL查询
add_origin_sql_query_route(app, prefix="/test_origin_sql_query")

# 添加Redis路由
add_redis_route(app, prefix="/redis")

LgChatService.add_route(app=app, path="/lg_chat")

add_langgraph_route(app)
add_lg_approve_route(app)
add_langgraph_chat_route(app)

# 下面这个是作业提交接口
add_langgraph_approve_route(app)
# 测试批量生成接口
# create_model_service(
#   app=app,
#   path="/batch_generate_interface",
#   Cls=Role
# )

add_routes(
  app=app,
  runnable=RunnableLambda(lambda x: x['messages']) | create_llm() | StrOutputParser(),
  input_type=ModelInputSchema,
  path="/doubao"
)

add_async_route(
  app=app,
  input_type=ModelInputSchema,
  runnable=RunnableLambda(lambda x: x['messages']) | create_llm("bailian-qwen-turbo"),
  path="/qwen"
)

LlmOrderService.add_route(app=app, path="/llm_order")
LlmProductService.add_route(app=app, path="/llm_product")
LgApproveService.add_route(app=app, path="/lg_approve")
LgMessageService.add_route(app=app, path="/lg_message")

# 测试SQLModel的CRUD操作
# add_test_sqlmodel_crud_route(app, prefix="/test_sqlmodel_crud")

# 只有在直接运行此文件时才启动服务器（开发环境）
if __name__ == "__main__":
  import os
  import uvicorn

  # 检查是否在 Gunicorn 环境下运行
  if "GUNICORN_CMD_ARGS" in os.environ:
    # 在 Gunicorn 环境下，不需要在这里启动服务器
    # Gunicorn 会自己处理
    pass
  else:
    # 开发环境，使用 uvicorn 启动
    port = int(env.server_port)
    print(f"在开发环境中启动服务器，端口: {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
