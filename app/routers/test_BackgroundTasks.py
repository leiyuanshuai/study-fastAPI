from fastapi import APIRouter, BackgroundTasks, FastAPI


def background_task(app: FastAPI, prefix: str = "/test_background_tasks"):
  router = APIRouter(prefix=prefix, tags=["测试BackgroundTasks"])
  def write_notification(email: str, message=""):
    try:
      # 模拟发送邮件的逻辑
      # 模拟内部发送邮件功能 或者写入日志功能
      with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)
      print(f"Sending email to {email} with message: {message}")
    except Exception as e:
      print(f"Error sending email to {email}: {e}")

  @router.post("/send-notification/{email}")
  async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "通知已经在后台运行，稍后会发送到邮箱"}

  app.include_router(router)






