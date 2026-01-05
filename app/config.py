"""
应用配置管理
"""
from typing import Optional
from pydantic import ConfigDict, field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用配置
    APP_NAME: str = "AI News"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./data/database/ai_news.db"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_ENABLED: bool = False
    
    # LLM配置
    OLLAMA_BASE_URL: str = "http://192.168.11.12:11434"
    OLLAMA_MODEL: str = "qwen3:latest"
    OLLAMA_TIMEOUT: int = 60
    
    # OpenAI配置
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    # 火山引擎配置
    HUOSHAN_API_KEY: str = ""
    HUOSHAN_SECRET_KEY: str = ""
    HUOSHAN_MODEL: str = "ep-xxx"
    
    # 阿里千问配置
    QIANWEN_API_KEY: str = ""
    QIANWEN_MODEL: str = "qwen-turbo"
    
    # LLM处理配置
    DEFAULT_LLM_PROVIDER: str = "ollama"
    SUMMARY_TARGET_LENGTH: int = 400
    BATCH_PROCESS_SIZE: int = 50
    MAX_RETRIES: int = 3
    ENABLE_LLM_FALLBACK: bool = True
    
    # LLM异步处理超时配置  
    LLM_ASYNC_TIMEOUT: int = 120  # 异步文章处理超时时间（秒）
    LLM_BATCH_TIMEOUT: int = 300  # 批量处理超时时间（秒）
    LLM_SINGLE_TIMEOUT: int = 60  # 单文章处理超时时间（秒）
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ADMIN_PASSWORD: str = "admin123"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 新闻抓取配置
    DEFAULT_FETCH_INTERVAL: int = 3600  # 1小时
    MAX_ARTICLES_PER_SOURCE: int = 50
    
    # API限流配置
    RATE_LIMIT_PER_MINUTE: int = 60

    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """验证SECRET_KEY不能使用默认值"""
        if v == "your-secret-key-change-in-production":
            import warnings
            warnings.warn(
                "使用默认SECRET_KEY不安全，请在生产环境中更改！",
                UserWarning
            )
        return v

    @field_validator('OLLAMA_TIMEOUT', 'LLM_ASYNC_TIMEOUT', 'LLM_BATCH_TIMEOUT', 'LLM_SINGLE_TIMEOUT')
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        """验证超时时间必须为正数"""
        if v <= 0:
            raise ValueError("超时时间必须大于0")
        return v

    @field_validator('RATE_LIMIT_PER_MINUTE', 'MAX_ARTICLES_PER_SOURCE', 'BATCH_PROCESS_SIZE')
    @classmethod
    def validate_positive_int(cls, v: int) -> int:
        """验证必须为正整数"""
        if v <= 0:
            raise ValueError("该值必须大于0")
        return v

    @model_validator(mode='after')
    def validate_llm_config(self) -> 'Settings':
        """验证LLM配置的完整性"""
        provider = self.DEFAULT_LLM_PROVIDER.lower()

        if provider == "openai" and not self.OPENAI_API_KEY:
            raise ValueError("使用OpenAI时必须配置OPENAI_API_KEY")

        if provider == "huoshan" and (not self.HUOSHAN_API_KEY or not self.HUOSHAN_SECRET_KEY):
            raise ValueError("使用火山引擎时必须配置HUOSHAN_API_KEY和HUOSHAN_SECRET_KEY")

        if provider == "qianwen" and not self.QIANWEN_API_KEY:
            raise ValueError("使用千问时必须配置QIANWEN_API_KEY")

        # 验证超时时间的合理性
        if self.LLM_SINGLE_TIMEOUT > self.LLM_ASYNC_TIMEOUT:
            raise ValueError("LLM_SINGLE_TIMEOUT不应大于LLM_ASYNC_TIMEOUT")

        if self.LLM_ASYNC_TIMEOUT > self.LLM_BATCH_TIMEOUT:
            raise ValueError("LLM_ASYNC_TIMEOUT不应大于LLM_BATCH_TIMEOUT")

        return self

    model_config = ConfigDict(env_file=".env")


# 全局配置实例
settings = Settings()
