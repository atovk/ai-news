"""
测试 LLM 适配器功能
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import httpx

from app.services.llm_interface import LLMProvider, LLMProcessingError
from app.services.llm_config import (
    OllamaConfig, OpenAIConfig, HuoshanConfig, QianwenConfig
)
from app.services.llm_adapters import (
    OllamaAdapter, OpenAIAdapter, HuoshanAdapter, QianwenAdapter
)


class TestOllamaAdapter:
    """测试 Ollama 适配器"""

    @pytest.fixture
    def ollama_config(self):
        return OllamaConfig(
            base_url="http://localhost:11434",
            model="qwen3",
            temperature=0.7
        )

    @pytest.fixture
    def ollama_adapter(self, ollama_config):
        return OllamaAdapter(ollama_config)

    @pytest.mark.asyncio
    async def test_summarize_content(self, ollama_adapter):
        """测试摘要生成"""
        with patch.object(ollama_adapter, '_call_ollama', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "这是一个测试摘要"
            result = await ollama_adapter.summarize_content("测试内容", 100)
            assert result == "这是一个测试摘要"
            mock_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_translate_to_chinese(self, ollama_adapter):
        """测试翻译功能"""
        with patch.object(ollama_adapter, '_call_ollama', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "你好世界"
            result = await ollama_adapter.translate_to_chinese("Hello World", "en")
            assert result == "你好世界"
            mock_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_translate_chinese_to_chinese(self, ollama_adapter):
        """测试中文到中文翻译（应直接返回）"""
        result = await ollama_adapter.translate_to_chinese("你好", "zh")
        assert result == "你好"

    @pytest.mark.asyncio
    async def test_extract_keywords(self, ollama_adapter):
        """测试关键词提取"""
        with patch.object(ollama_adapter, '_call_ollama', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "AI, 机器学习, 深度学习"
            result = await ollama_adapter.extract_keywords("测试内容", 3)
            assert len(result) == 3
            assert "AI" in result

    @pytest.mark.asyncio
    async def test_categorize_article(self, ollama_adapter):
        """测试文章分类"""
        with patch.object(ollama_adapter, '_call_ollama', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "科技"
            result = await ollama_adapter.categorize_article(
                "AI新闻", "关于人工智能的文章", ["科技", "财经", "体育"]
            )
            assert result == "科技"

    @pytest.mark.asyncio
    async def test_health_check_success(self, ollama_adapter):
        """测试健康检查成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.5

        with patch.object(ollama_adapter.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            result = await ollama_adapter.health_check()
            assert result["status"] == "healthy"
            assert result["provider"] == "ollama"

    @pytest.mark.asyncio
    async def test_health_check_failure(self, ollama_adapter):
        """测试健康检查失败"""
        with patch.object(ollama_adapter.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Connection error")
            result = await ollama_adapter.health_check()
            assert result["status"] == "unhealthy"
            assert "error" in result


class TestOpenAIAdapter:
    """测试 OpenAI 适配器"""

    @pytest.fixture
    def openai_config(self):
        return OpenAIConfig(
            api_key="test-key",
            model="gpt-3.5-turbo",
            base_url="https://api.openai.com/v1"
        )

    @pytest.fixture
    def openai_adapter(self, openai_config):
        return OpenAIAdapter(openai_config)

    @pytest.mark.asyncio
    async def test_summarize_content(self, openai_adapter):
        """测试摘要生成"""
        with patch.object(openai_adapter, '_call_openai', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "这是一个测试摘要"
            result = await openai_adapter.summarize_content("测试内容", 100)
            assert result == "这是一个测试摘要"
            mock_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_call_openai_success(self, openai_adapter):
        """测试 OpenAI API 调用成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "测试响应"}}]
        }

        with patch.object(openai_adapter.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await openai_adapter._call_openai("测试提示")
            assert result == "测试响应"

    @pytest.mark.asyncio
    async def test_call_openai_failure(self, openai_adapter):
        """测试 OpenAI API 调用失败"""
        with patch.object(openai_adapter.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("API error")
            with pytest.raises(LLMProcessingError):
                await openai_adapter._call_openai("测试提示")


class TestHuoshanAdapter:
    """测试火山引擎适配器"""

    @pytest.fixture
    def huoshan_config(self):
        return HuoshanConfig(
            api_key="test-key",
            secret_key="test-secret",
            model="ep-test",
            base_url="https://ark.cn-beijing.volces.com/api/v3"
        )

    @pytest.fixture
    def huoshan_adapter(self, huoshan_config):
        return HuoshanAdapter(huoshan_config)

    @pytest.mark.asyncio
    async def test_summarize_content(self, huoshan_adapter):
        """测试摘要生成"""
        with patch.object(huoshan_adapter, '_call_huoshan', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "这是一个测试摘要"
            result = await huoshan_adapter.summarize_content("测试内容", 100)
            assert result == "这是一个测试摘要"
            mock_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_call_huoshan_success(self, huoshan_adapter):
        """测试火山引擎 API 调用成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "测试响应"}}]
        }

        with patch.object(huoshan_adapter.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await huoshan_adapter._call_huoshan("测试提示")
            assert result == "测试响应"

    @pytest.mark.asyncio
    async def test_call_huoshan_failure(self, huoshan_adapter):
        """测试火山引擎 API 调用失败"""
        with patch.object(huoshan_adapter.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("API error")
            with pytest.raises(LLMProcessingError):
                await huoshan_adapter._call_huoshan("测试提示")


class TestQianwenAdapter:
    """测试千问适配器"""

    @pytest.fixture
    def qianwen_config(self):
        return QianwenConfig(
            api_key="test-key",
            model="qwen-turbo",
            base_url="https://dashscope.aliyuncs.com/api/v1"
        )

    @pytest.fixture
    def qianwen_adapter(self, qianwen_config):
        return QianwenAdapter(qianwen_config)

    @pytest.mark.asyncio
    async def test_summarize_content(self, qianwen_adapter):
        """测试摘要生成"""
        with patch.object(qianwen_adapter, '_call_qianwen', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "这是一个测试摘要"
            result = await qianwen_adapter.summarize_content("测试内容", 100)
            assert result == "这是一个测试摘要"
            mock_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_call_qianwen_success(self, qianwen_adapter):
        """测试千问 API 调用成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "output": {"text": "测试响应"}
        }

        with patch.object(qianwen_adapter.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await qianwen_adapter._call_qianwen("测试提示")
            assert result == "测试响应"

    @pytest.mark.asyncio
    async def test_call_qianwen_failure(self, qianwen_adapter):
        """测试千问 API 调用失败"""
        with patch.object(qianwen_adapter.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("API error")
            with pytest.raises(LLMProcessingError):
                await qianwen_adapter._call_qianwen("测试提示")


class TestAdapterIntegration:
    """测试适配器集成"""

    @pytest.mark.asyncio
    async def test_all_adapters_implement_interface(self):
        """测试所有适配器都实现了接口"""
        from app.services.llm_interface import LLMServiceInterface

        adapters = [OllamaAdapter, OpenAIAdapter, HuoshanAdapter, QianwenAdapter]

        for adapter_class in adapters:
            assert issubclass(adapter_class, LLMServiceInterface)

            # 检查所有必需方法是否存在
            required_methods = [
                'summarize_content',
                'translate_to_chinese',
                'detect_language',
                'extract_keywords',
                'categorize_article',
                'health_check'
            ]

            for method in required_methods:
                assert hasattr(adapter_class, method)
