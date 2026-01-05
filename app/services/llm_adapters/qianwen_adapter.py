"""
阿里千问 LLM 适配器实现
"""
import httpx
import json
from typing import Dict, Any, List
from app.services.llm_interface import LLMServiceInterface, LLMProcessingError
from app.services.llm_config import QianwenConfig
import logging

logger = logging.getLogger(__name__)


class QianwenAdapter(LLMServiceInterface):
    """阿里千问适配器实现"""

    def __init__(self, config: QianwenConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            timeout=config.timeout,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
        )

    async def summarize_content(self, content: str, target_length: int = 400, **kwargs) -> str:
        """使用千问生成摘要"""
        prompt = self._build_summary_prompt(content, target_length)
        return await self._call_qianwen(prompt)

    async def translate_to_chinese(self, text: str, source_language: str = "auto", **kwargs) -> str:
        """使用千问翻译为中文"""
        if source_language.lower() in ['zh', 'zh-cn', 'chinese']:
            return text

        prompt = self._build_translation_prompt(text, source_language)
        return await self._call_qianwen(prompt)

    async def detect_language(self, text: str, **kwargs) -> str:
        """使用千问检测语言"""
        try:
            # 优先使用 langdetect 库
            import langdetect
            return langdetect.detect(text)
        except Exception:
            # 如果检测失败，使用 LLM 检测
            prompt = f"请检测以下文本的语言，只返回语言代码（如：en, zh, ja等）：\n\n{text[:200]}"
            response = await self._call_qianwen(prompt)
            return response.strip().lower()

    async def extract_keywords(self, content: str, max_keywords: int = 5, **kwargs) -> List[str]:
        """提取关键词"""
        prompt = f"请从以下文本中提取{max_keywords}个最重要的关键词，以逗号分隔：\n\n{content}"
        response = await self._call_qianwen(prompt)
        return [kw.strip() for kw in response.split(',')][:max_keywords]

    async def categorize_article(self, title: str, content: str, categories: List[str], **kwargs) -> str:
        """文章分类"""
        categories_str = "、".join(categories)
        prompt = f"请将以下文章分类到最合适的类别中，候选类别：{categories_str}\n\n标题：{title}\n\n内容：{content[:500]}\n\n分类："
        response = await self._call_qianwen(prompt)
        return response.strip()

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 千问使用简单的请求测试健康状态
            response = await self.client.post(
                f"{self.config.base_url}/services/aigc/text-generation/generation",
                json={
                    "model": self.config.model,
                    "input": {
                        "messages": [{"role": "user", "content": "test"}]
                    },
                    "parameters": {
                        "max_tokens": 10
                    }
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

    async def _call_qianwen(self, prompt: str) -> str:
        """调用千问 API"""
        try:
            response = await self.client.post(
                f"{self.config.base_url}/services/aigc/text-generation/generation",
                json={
                    "model": self.config.model,
                    "input": {
                        "messages": [
                            {"role": "user", "content": prompt}
                        ]
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["output"]["text"]
        except Exception as e:
            logger.error(f"千问 API 调用失败: {e}")
            raise LLMProcessingError(f"千问 API 调用失败: {e}")

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
