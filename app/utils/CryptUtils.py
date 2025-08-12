from datetime import timedelta, datetime, timezone #
# timedelta 表示时间间隔   timezone 表示时区
import jwt # 导入 PyJWT 库，用于生成和解析 JWT（JSON Web Token），实现用户登录认证。

# Import Passlib 库中的 CryptContext 类，用于'密码哈希'加密 和 验证。
from passlib.context import CryptContext

from app.config.env import env

"""
创建一个密码上下文对象：
- `schemes=["bcrypt"]` 指定使用 bcrypt 哈希算法进行密码加密。
- `deprecated="auto"` 自动标记旧算法为“已弃用”，未来可升级；
- 这个对象提供了 .hash() 和 .verify() 方法。
"""
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CryptUtils:
  @staticmethod
  def get_password_hash(password): # 对密码进行哈希加密处理
    """
    对密码进行哈希加密处理

    Args:
        password (str): 需要加密的原始密码字符串

    Returns:
        str: 经过哈希加密后的密码字符串
    """
    return pwd_context.hash(password)

  @staticmethod
  def verify_password(plain_password, hashed_password): # 验证密码是否正确
    """
    验证密码是否正确

    通过比较明文密码和哈希密码来验证密码是否匹配

    参数:
        plain_password (str): 明文密码
        hashed_password (str): 哈希后的密码

    返回:
        bool: 密码验证结果，True表示密码正确，False表示密码错误
    """
    return pwd_context.verify(plain_password, hashed_password)

  @staticmethod # 创建访问令牌jwt 但是只是针对username进行加密
  def create_access_token(username: str, expires_delta: timedelta | None = None):
    data: dict = {"sub": username}
    to_encode = data.copy() # 复制一份，避免修改原始数据
    if expires_delta:
      expire = datetime.now(timezone.utc) + expires_delta
    else:
      expire = datetime.now(timezone.utc) + timedelta(minutes=env.jwt_access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, env.jwt_secret_key, algorithm=env.jwt_algorithm)
    return encoded_jwt

  @staticmethod
  def get_username_from_token(token: str) -> str | None:
    try:
      payload = jwt.decode(
        token,
        env.jwt_secret_key,
        algorithms=[env.jwt_algorithm]
      )
      return payload.get("sub")
    except jwt.ExpiredSignatureError:
      return None  # token 过期
    except jwt.InvalidTokenError:
      return None  # token 无效（篡改、格式错等）

