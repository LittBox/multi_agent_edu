"""应用配置管理，通过环境变量加载。"""

from pydantic_settings import BaseSettings

#字段要和.env文件中的字段保持一致
#pydantic-settings，默认情况下环境变量名是 case-insensitive，即大小写不敏感
#settings里要小写，.env里要大写
# settings.py：Python 字段名，用小写 snake_case
# .env：环境变量名，用大写 SNAKE_CASE
# 访问配置：用 settings.py 里的小写字段名
class Settings(BaseSettings):
    # LLM
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    minimax_api_key: str = ""
    minimax_model: str = "MiniMax-M2.7"
    deepseek_api_key: str = ""
    deepseek_model: str = ""

    # Database
    database_url: str = ""
    secret_key: str = ""
    redis_url: str = "redis://localhost:6379/0"

    # Server
    api_port: int = 8000
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

if __name__ == "__main__":
    print(settings.dict())