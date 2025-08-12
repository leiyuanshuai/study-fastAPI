from typing import List

from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv


class Settings(BaseSettings):
  db_host: str = Field(..., env="DB_HOST")
  db_port: str = Field(..., env="DB_PORT")
  db_username: str = Field(..., env="DB_USERNAME")
  db_password: str = Field(..., env="DB_PASSWORD")
  db_database: str = Field(..., env="DB_DATABASE")

  pg_db_host: str = Field(..., env="PG_DB_HOST")
  pg_db_port: str = Field(..., env="PG_DB_PORT")
  pg_db_username: str = Field(..., env="PG_DB_USERNAME")
  pg_db_password: str = Field(..., env="PG_DB_PASSWORD")
  pg_db_database: str = Field(..., env="PG_DB_DATABASE")

  llm_key_local: str = Field(..., env="LLM_KEY_LOCAL")
  llm_key_huoshan: str = Field(..., env="LLM_KEY_HUOSHAN")
  llm_key_bailian: str = Field(..., env="LLM_KEY_BAILIAN")
  llm_key_deepseek: str = Field(..., env="LLM_KEY_DEEPSEEK")

  server_port: str = Field(..., env="SERVER_PORT")
  server_domain: str = Field(..., env="SERVER_DOMAIN")

  jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
  jwt_algorithm: str = Field(..., env="JWT_ALGORITHM")
  jwt_access_token_expire_minutes: int = Field(..., env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
  jwt_global_enable: bool = Field(..., env="JWT_GLOBAL_ENABLE")
  jwt_white_list: List[str] = Field(..., env="JWT_WHITE_LIST")

  class Config:
    env_file = ".env"
    env_file_encoding = "utf-8"


load_dotenv(".env")  # 先加载 .env 文件
env = Settings()
