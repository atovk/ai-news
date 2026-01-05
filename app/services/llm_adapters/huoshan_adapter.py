"""
火山引擎 LLM 适配器实现
"""
import httpx
import json
from typing import Dict, Any, List
from app.services.llm_interface import LLMServiceInterface, LLMProcessingError
from app.services.llm_config import HuoshanConfig
import logging

logger = logging.getLogger(__name__)


class HuoshanAdapter(LLMServiceInterface):
    """火山引擎适配器实现"""

    def __init__(self, config: HuoshanConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            timeout=config.timeout,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
        )

    async def summarize_content(self, content: str, target_length: int = 400, **kwargs) -> str:
        """使用火山引擎生成摘要"""
        prompt = self._build_summary_prompt(content, target_length)
        return await self._call_huoshan(prompt)

    async def translate_to_chinese(self, text: str, source_language: str = "auto", **kwargs) -> str:
        """使用火山引擎翻译为中文"""
        if source_language.lower() in ['zh', 'zh-cn', 'chinese']:
            return text

        prompt = self._build_translation_prompt(text, source_language)
        return await self._call_huoshan(prompt)

    async def detect_language(self, text: str, **kwargs) -> str:
        """使用火山引擎检测语言"""
        try:
            # 优先使用 langdetect 库
            import langdetect
            return langdetect.detect(text)
        except Exception:
            # 如果检测失败，使用 LLM 检测
            prompt = f"请检测以下文本的语言，只返回语言代码（如：en, zh, ja等）：\n\n{text[:200]}"
            response = await self._call_huoshan(prompt)
            return response.strip().lower()

    async def extract_keywords(self, content: str, max_keywords: int = 5, **kwargs) -> List[str]:
        """提取关键词"""
        prompt = f"请从以下文本中提取{max_keywords}个最重要的关键词，以逗号分隔：\n\n{content}"
        response = await self._call_huoshan(prompt)
        return [kw.strip() for kw in response.split(',')][:max_keywords]

    async def categorize_article(self, title: str, content: str, categories: List[str], **kwargs) -> str:
        """文章分类"""
        categories_str = "、".join(categories)
        prompt = f"请将以下文章分类到最合适的类别中，候选类别：{categories_str}\n\n标题：{title}\n\n内容：{content[:500]}\n\n分类："
        response = await self._call_huoshan(prompt)
        return response.strip()

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 火山引擎使用简单的请求测试健康状态
            response = await self.client.post(
                f"{self.config.base_url}/chat/completions",
                json={
                    "model": self.config.model,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 10
                }
            )
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "provider": self.config.provider.value,
                "model": self.config.model,
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": self.config.provider.value,
                "error": str(e)
            }

    async def _call_huoshan(self, prompt: str) -> str:
        """调用火山引擎 API"""
        try:
            response = await self.client.post(
                f"{self.config.base_url}/chat/completions",
                json={
                    "model": self.config.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"火山引擎 API 调用失败: {e}")
            raise LLMProcessingError(f"火山引擎 API 调用失败: {e}")

    def _build_summary_prompt(self, content: str, target_length: int) -> str:
        """构建摘要提示词"""
        return f"""
请将以下文章内容压缩为约 {target_length} 字的中文摘要，要求：
1. 保留文章核心信息和要点
2. 语言简洁清晰，便于快速阅读
3. 如果原文非中文，请翻译为中文
4. 保持客观中性的表述

文章内容：
{content}

摘要：
"""

    def _build_translation_prompt(self, text: str, source_language: str) -> str:
        """构建翻译提示词"""
        return f"""
请将以下{source_language}文本翻译为简体中文，要求：
1. 翻译准确，保持原意
2. 语言自然流畅
3. 适合中文阅读习惯

原文：
{text}

中文翻译：
"""
