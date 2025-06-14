"""
LLM 服务接口和枚举定义
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime


class LLMProvider(str, Enum):
    """支持的 LLM 提供商"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUOSHAN = "huoshan"
    QIANWEN = "qianwen"
    CUSTOM = "custom"


class LLMServiceInterface(ABC):
    """LLM 服务抽象接口 - 定义统一的服务契约"""
    
    @abstractmethod
    async def summarize_content(self, content: str, target_length: int = 400, **kwargs) -> str:
        """生成内容摘要
        
        Args:
            content: 原始内容
            target_length: 目标摘要长度
            **kwargs: 扩展参数（如模型特定配置）
        
        Returns:
            生成的摘要文本
        """
        pass
    
    @abstractmethod
    async def translate_to_chinese(self, text: str, source_language: str = "auto", **kwargs) -> str:
        """翻译为中文
        
        Args:
            text: 待翻译文本
            source_language: 源语言代码
            **kwargs: 扩展参数
        
        Returns:
            中文翻译结果
        """
        pass
    
    @abstractmethod
    async def detect_language(self, text: str, **kwargs) -> str:
        """检测文本语言
        
        Args:
            text: 待检测文本
            **kwargs: 扩展参数
        
        Returns:
            语言代码 (如: en, zh, ja)
        """
        pass
    
    @abstractmethod
    async def extract_keywords(self, content: str, max_keywords: int = 5, **kwargs) -> List[str]:
        """提取关键词
        
        Args:
            content: 原始内容
            max_keywords: 最大关键词数量
            **kwargs: 扩展参数
        
        Returns:
            关键词列表
        """
        pass
    
    @abstractmethod
    async def categorize_article(self, title: str, content: str, categories: List[str], **kwargs) -> str:
        """文章分类
        
        Args:
            title: 文章标题
            content: 文章内容
            categories: 候选分类列表
            **kwargs: 扩展参数
        
        Returns:
            最匹配的分类
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """健康检查
        
        Returns:
            健康状态信息
        """
        pass


class LLMProcessingError(Exception):
    """LLM 处理异常"""
    pass
