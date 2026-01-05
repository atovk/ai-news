"""
应用配置管理
"""
import os
import re
from typing import Optional
from pydantic import ConfigDict, field_validator
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
    SECRET_KEY: str = ""
    ADMIN_PASSWORD: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 新闻抓取配置
    DEFAULT_FETCH_INTERVAL: int = 3600  # 1小时
    MAX_ARTICLES_PER_SOURCE: int = 50
    
    # API限流配置
    RATE_LIMIT_PER_MINUTE: int = 60
    
    model_config = ConfigDict(env_file=".env")


# 全局配置实例
settings = Settings()
