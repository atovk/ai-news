"""
LLM 服务管理器 - 实现统一服务入口和回退机制
"""
from typing import Dict, Type, Any, List
from app.services.llm_interface import LLMServiceInterface, LLMProvider, LLMProcessingError
from app.services.llm_config import LLMConfig, LLMProviderConfig
from app.services.llm_adapters import OllamaAdapter
import logging

logger = logging.getLogger(__name__)


class LLMAdapterFactory:
    """LLM 适配器工厂"""
    
    _adapters: Dict[LLMProvider, Type[LLMServiceInterface]] = {
        LLMProvider.OLLAMA: OllamaAdapter,
        # TODO: 添加其他适配器
        # LLMProvider.OPENAI: OpenAIAdapter,
        # LLMProvider.HUOSHAN: HuoshanAdapter,
        # LLMProvider.QIANWEN: QianwenAdapter,
    }
    
    @classmethod
    def create_adapter(cls, config: LLMProviderConfig) -> LLMServiceInterface:
        """创建适配器实例"""
        adapter_class = cls._adapters.get(config.provider)
        if not adapter_class:
            raise ValueError(f"不支持的 LLM 提供商: {config.provider}")
        
        return adapter_class(config)
    
    @classmethod
    def register_adapter(cls, provider: LLMProvider, adapter_class: Type[LLMServiceInterface]):
        """注册自定义适配器"""
        cls._adapters[provider] = adapter_class


class LLMServiceManager:
    """LLM 服务管理器 - 实现统一服务入口和回退机制"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.adapters: Dict[LLMProvider, LLMServiceInterface] = {}
        self._initialize_adapters()
    
    def _initialize_adapters(self):
        """初始化所有适配器"""
        for provider, provider_config in self.config.providers.items():
            if provider_config.enabled:
                try:
                    adapter = LLMAdapterFactory.create_adapter(provider_config)
                    self.adapters[provider] = adapter
                    logger.info(f"成功初始化 {provider.value} 适配器")
                except Exception as e:
                    logger.error(f"初始化 {provider.value} 适配器失败: {e}")
    
    async def summarize_content(self, content: str, target_length: int = 400, **kwargs) -> str:
        """生成摘要 - 支持回退机制"""
        return await self._execute_with_fallback("summarize_content", content, target_length, **kwargs)
    
    async def translate_to_chinese(self, text: str, source_language: str = "auto", **kwargs) -> str:
        """翻译为中文 - 支持回退机制"""
        return await self._execute_with_fallback("translate_to_chinese", text, source_language, **kwargs)
    
    async def detect_language(self, text: str, **kwargs) -> str:
        """检测语言 - 支持回退机制"""
        return await self._execute_with_fallback("detect_language", text, **kwargs)
    
    async def extract_keywords(self, content: str, max_keywords: int = 5, **kwargs) -> List[str]:
        """提取关键词 - 支持回退机制"""
        return await self._execute_with_fallback("extract_keywords", content, max_keywords, **kwargs)
    
    async def categorize_article(self, title: str, content: str, categories: List[str], **kwargs) -> str:
        """文章分类 - 支持回退机制"""
        return await self._execute_with_fallback("categorize_article", title, content, categories, **kwargs)
    
    async def _execute_with_fallback(self, method_name: str, *args, **kwargs) -> Any:
        """执行方法并支持回退机制"""
        # 优先使用默认提供商
        providers_to_try = [self.config.default_provider]
        
        # 如果启用回退，添加回退提供商列表
        if self.config.enable_fallback:
            for provider in self.config.fallback_order:
                if provider != self.config.default_provider and provider in self.adapters:
                    providers_to_try.append(provider)
        
        last_error = None
        for provider in providers_to_try:
            adapter = self.adapters.get(provider)
            if not adapter:
                continue
            
            try:
                method = getattr(adapter, method_name)
                result = await method(*args, **kwargs)
                logger.info(f"LLM 调用成功 - 提供商: {provider.value}, 方法: {method_name}")
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"LLM 调用失败 - 提供商: {provider.value}, 方法: {method_name}, 错误: {e}")
                continue
        
        # 所有提供商都失败
        raise LLMProcessingError(f"所有 LLM 提供商都失败，最后错误: {last_error}")
    
    async def health_check_all(self) -> Dict[str, Any]:
        """检查所有适配器的健康状态"""
        results = {}
        for provider, adapter in self.adapters.items():
            try:
                health = await adapter.health_check()
                results[provider.value] = health
            except Exception as e:
                results[provider.value] = {
                    "status": "error",
                    "error": str(e)
                }
        return results
    
    def switch_default_provider(self, provider: LLMProvider):
        """切换默认提供商"""
        if provider not in self.adapters:
            raise ValueError(f"提供商 {provider} 未初始化")
        self.config.default_provider = provider
        logger.info(f"默认 LLM 提供商已切换为: {provider.value}")
    
    def get_active_providers(self) -> List[LLMProvider]:
        """获取活跃的提供商列表"""
        return list(self.adapters.keys())
