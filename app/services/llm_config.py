"""
LLM 配置管理
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from app.services.llm_interface import LLMProvider


class LLMProviderConfig(BaseModel):
    """LLM 提供商配置基类"""
    provider: LLMProvider
    enabled: bool = True
    timeout: int = 60
    max_retries: int = 3
    retry_delay: int = 1


class OllamaConfig(LLMProviderConfig):
    """Ollama 配置"""
    provider: LLMProvider = LLMProvider.OLLAMA
    base_url: str = "http://192.168.11.12:11434"
    model: str = "qwen3"
    temperature: float = 0.7


class OpenAIConfig(LLMProviderConfig):
    """OpenAI 配置"""
    provider: LLMProvider = LLMProvider.OPENAI
    api_key: str
    model: str = "gpt-3.5-turbo"
    base_url: str = "https://api.openai.com/v1"
    temperature: float = 0.7
    max_tokens: int = 1000


class HuoshanConfig(LLMProviderConfig):
    """火山引擎配置"""
    provider: LLMProvider = LLMProvider.HUOSHAN
    api_key: str
    secret_key: str
    model: str = "ep-20240101-xxx"
    base_url: str = "https://ark.cn-beijing.volces.com/api/v3"


class QianwenConfig(LLMProviderConfig):
    """阿里千问配置"""
    provider: LLMProvider = LLMProvider.QIANWEN
    api_key: str
    model: str = "qwen-turbo"
    base_url: str = "https://dashscope.aliyuncs.com/api/v1"


class LLMConfig(BaseModel):
    """LLM 模块总配置"""
    # 默认提供商
    default_provider: LLMProvider = LLMProvider.OLLAMA
    
    # 提供商配置映射
    providers: Dict[LLMProvider, LLMProviderConfig] = {}
    
    # 处理配置
    summary_target_length: int = 400
    batch_process_size: int = 50
    max_concurrent_tasks: int = 10
    
    # 回退策略配置
    enable_fallback: bool = True
    fallback_order: List[LLMProvider] = [
        LLMProvider.OLLAMA,
        LLMProvider.OPENAI,
        LLMProvider.QIANWEN
    ]
