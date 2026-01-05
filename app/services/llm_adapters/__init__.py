"""
LLM 适配器包初始化
"""
from .ollama_adapter import OllamaAdapter
from .openai_adapter import OpenAIAdapter
from .huoshan_adapter import HuoshanAdapter
from .qianwen_adapter import QianwenAdapter

__all__ = ["OllamaAdapter", "OpenAIAdapter", "HuoshanAdapter", "QianwenAdapter"]
