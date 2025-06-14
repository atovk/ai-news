"""
LLM 管理器配置工厂
"""
from app.services.llm_manager import LLMServiceManager
from app.services.llm_config import LLMConfig, OllamaConfig, OpenAIConfig, HuoshanConfig, QianwenConfig
from app.services.llm_interface import LLMProvider
from app.config import settings


def create_llm_manager() -> LLMServiceManager:
    """根据配置创建 LLM 管理器"""
    
    # 创建提供商配置
    providers = {}
    
    # Ollama 配置（默认启用）
    providers[LLMProvider.OLLAMA] = OllamaConfig(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        timeout=settings.OLLAMA_TIMEOUT,
        enabled=True
    )
    
    # OpenAI 配置（如果有API Key则启用）
    if settings.OPENAI_API_KEY:
        providers[LLMProvider.OPENAI] = OpenAIConfig(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            base_url=settings.OPENAI_BASE_URL,
            enabled=True
        )
    
    # 火山引擎配置（如果有API Key则启用）
    if settings.HUOSHAN_API_KEY and settings.HUOSHAN_SECRET_KEY:
        providers[LLMProvider.HUOSHAN] = HuoshanConfig(
            api_key=settings.HUOSHAN_API_KEY,
            secret_key=settings.HUOSHAN_SECRET_KEY,
            model=settings.HUOSHAN_MODEL,
            enabled=True
        )
    
    # 阿里千问配置（如果有API Key则启用）
    if settings.QIANWEN_API_KEY:
        providers[LLMProvider.QIANWEN] = QianwenConfig(
            api_key=settings.QIANWEN_API_KEY,
            model=settings.QIANWEN_MODEL,
            enabled=True
        )
    
    # 确定默认提供商
    try:
        default_provider = LLMProvider(settings.DEFAULT_LLM_PROVIDER)
    except ValueError:
        default_provider = LLMProvider.OLLAMA
    
    # 创建LLM配置
    llm_config = LLMConfig(
        default_provider=default_provider,
        providers=providers,
        summary_target_length=settings.SUMMARY_TARGET_LENGTH,
        batch_process_size=settings.BATCH_PROCESS_SIZE,
        enable_fallback=settings.ENABLE_LLM_FALLBACK,
        fallback_order=[
            LLMProvider.OLLAMA,
            LLMProvider.OPENAI,
            LLMProvider.QIANWEN,
            LLMProvider.HUOSHAN
        ]
    )
    
    return LLMServiceManager(llm_config)


# 全局LLM管理器实例（单例模式）
_llm_manager = None


def get_llm_manager() -> LLMServiceManager:
    """获取LLM管理器实例（单例）"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = create_llm_manager()
    return _llm_manager
