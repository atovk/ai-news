# AI News "今日"功能使用指南

## 功能概述

"今日"功能是 AI News 系统的核心功能，通过 LLM 大语言模型将当日的所有新闻文章处理为 400字左右的中文摘要，方便用户快速阅读。

## 主要特性

- 🤖 **智能摘要**: 使用 LLM 将任意长度文章压缩为 400字精华摘要
- 🌍 **多语言支持**: 自动检测原文语言并翻译为中文
- 📊 **实时统计**: 显示今日文章处理状态统计
- 🔄 **多模型支持**: 支持 Ollama、OpenAI、火山引擎、阿里千问等
- 🛡️ **高可用设计**: 多提供商自动回退机制

## 快速开始

### 1. 环境准备

```bash
# 1. 确保已安装 Poetry
poetry --version

# 2. 安装依赖
poetry install

# 3. 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件，配置 LLM 相关参数
```

### 2. 启动 Ollama 服务（默认LLM）

```bash
# 安装并启动 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载 Qwen2.5 模型
ollama pull qwen2.5

# 启动 Ollama 服务
ollama serve
```

### 3. 启动应用

```bash
# 运行数据库迁移
poetry run python scripts/migrate_llm_fields.py

# 启动服务
poetry run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问服务

- API 文档: http://localhost:8000/docs
- 今日功能: http://localhost:8000/api/v1/today

## API 接口说明

### 核心接口

#### 1. 获取今日文章列表

```http
GET /api/v1/today/articles?page=1&size=20&source=xxx&language=zh
```

**参数说明:**
- `page`: 页码，默认1
- `size`: 每页数量，默认20，最大100
- `source`: 筛选特定新闻源（可选）
- `language`: 筛选特定语言（可选）

**响应示例:**
```json
{
  "total": 150,
  "page": 1,
  "size": 20,
  "articles": [
    {
      "id": 123,
      "original_title": "AI Technology Breakthrough",
      "chinese_title": "人工智能技术突破",
      "url": "https://example.com/article/123",
      "author": "John Doe",
      "source_name": "TechNews",
      "published_at": "2024-01-15T10:30:00Z",
      "llm_summary": "本文介绍了人工智能领域的最新突破...",
      "original_language": "en",
      "tags": ["科技", "人工智能", "突破"]
    }
  ]
}
```

#### 2. 获取今日统计

```http
GET /api/v1/today/stats
```

**响应示例:**
```json
{
  "today_total": 200,
  "processed": 150,
  "processing": 30,
  "pending": 15,
  "failed": 5,
  "language_distribution": {
    "en": 80,
    "zh": 50,
    "ja": 20
  }
}
```

#### 3. 手动触发处理

```http
POST /api/v1/today/process?limit=50
```

**参数说明:**
- `limit`: 处理文章数量限制，默认50

#### 4. 获取LLM健康状态

```http
GET /api/v1/today/llm/health
```

**响应示例:**
```json
{
  "providers": {
    "ollama": {
      "status": "healthy",
      "provider": "ollama",
      "model": "qwen2.5",
      "response_time": 0.5
    }
  },
  "active_providers": ["ollama"],
  "default_provider": "ollama"
}
```

#### 5. 切换LLM提供商

```http
POST /api/v1/today/llm/switch-provider?provider=openai
```

### 辅助接口

- `GET /api/v1/today/sources` - 获取可用新闻源列表
- `GET /api/v1/today/languages` - 获取可用语言列表

## 配置说明

### 环境变量配置

在 `.env` 文件中配置以下参数：

```bash
# 默认 LLM 提供商
DEFAULT_LLM_PROVIDER=ollama

# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5
OLLAMA_TIMEOUT=60

# OpenAI 配置（可选）
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_BASE_URL=https://api.openai.com/v1

# 火山引擎配置（可选）
HUOSHAN_API_KEY=your-huoshan-key
HUOSHAN_SECRET_KEY=your-huoshan-secret
HUOSHAN_MODEL=ep-xxx

# 阿里千问配置（可选）
QIANWEN_API_KEY=your-qianwen-key
QIANWEN_MODEL=qwen-turbo

# 处理配置
SUMMARY_TARGET_LENGTH=400
BATCH_PROCESS_SIZE=50
MAX_RETRIES=3
ENABLE_LLM_FALLBACK=true
```

## 架构说明

### 高内聚低耦合设计

1. **接口抽象层**: `LLMServiceInterface` 定义统一接口
2. **适配器层**: 各 LLM 提供商的具体实现
3. **管理层**: `LLMServiceManager` 提供统一服务入口
4. **业务层**: `ContentProcessorService` 和 `TodayService` 处理业务逻辑

### 多模型支持

系统支持多种 LLM 提供商：
- **Ollama**: 本地部署，支持开源模型
- **OpenAI**: GPT 系列模型
- **火山引擎**: 字节跳动的豆包模型
- **阿里千问**: 阿里巴巴的通义千问

### 自动回退机制

当主要 LLM 提供商不可用时，系统自动切换到备用提供商，确保服务稳定性。

## 测试

### 运行测试

```bash
# 运行功能测试
poetry run python scripts/test_today_feature.py

# 运行完整测试套件
poetry run pytest
```

### 测试覆盖

测试覆盖以下方面：
- LLM 管理器功能
- 内容处理器功能
- 今日服务功能
- API 接口功能
- 异常处理

## 部署

### 生产环境部署

```bash
# 1. 克隆项目
git clone <repository-url>
cd ai-news

# 2. 运行部署脚本
chmod +x scripts/deploy_today.sh
./scripts/deploy_today.sh

# 3. 使用 Docker（可选）
docker-compose up -d
```

### 监控

- 访问 `/api/v1/today/llm/health` 监控 LLM 服务状态
- 访问 `/api/v1/today/stats` 监控处理统计
- 查看应用日志了解运行状态

## 常见问题

### Q: Ollama 连接失败怎么办？

A: 检查以下项目：
1. Ollama 服务是否启动: `ollama serve`
2. 模型是否下载: `ollama pull qwen2.5`
3. 服务地址是否正确: 默认 `http://localhost:11434`

### Q: 如何添加新的 LLM 提供商？

A: 按以下步骤：
1. 实现 `LLMServiceInterface` 接口
2. 创建对应的配置类
3. 在 `LLMAdapterFactory` 中注册
4. 更新配置文件

### Q: 处理速度太慢怎么办？

A: 可以：
1. 增加并发处理数量
2. 使用更快的 LLM 模型
3. 配置多个 LLM 提供商
4. 调整摘要长度

### Q: 如何自定义摘要长度？

A: 在环境变量中设置 `SUMMARY_TARGET_LENGTH=300`，或在 API 调用中传递参数。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进"今日"功能！

## 许可证

本项目采用 MIT 许可证。
