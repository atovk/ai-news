# 技术架构设计

## 设计原则

- **简洁高效**: 保证系统简洁高效，无额外依赖及冗余功能
- **开闭原则**: 对扩展开放，对修改关闭
- **高内聚低耦合**: 模块间职责清晰，依赖关系简单
- **可扩展性**: 支持新闻源、分类方式的灵活扩展

## 系统架构图

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web 前端      │    │    API 网关     │    │   管理后台      │
│  (Vue.js/React) │◄──►│   (FastAPI)     │◄──►│   (Admin UI)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       业务服务层                                │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│   新闻聚合服务   │   内容处理服务   │   搜索服务      │ 分类服务  │
│  NewsAggregator │ ContentProcessor │ SearchService   │Classifier │
└─────────────────┴─────────────────┴─────────────────┴───────────┘
              │              │              │              │
              ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       数据持久层                                │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│   SQLite 数据库  │   Redis 缓存    │   文件存储      │ 索引存储  │
│   (主数据)      │   (临时数据)    │   (RSS/配置)    │(ElasticSearch)│
└─────────────────┴─────────────────┴─────────────────┴───────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       外部服务                                  │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│   RSS 新闻源    │   新闻 API      │   Ollama LLM    │ 第三方API │
│   (多个源)      │   (备用)        │   (本地部署)    │  (可选)   │
└─────────────────┴─────────────────┴─────────────────┴───────────┘
```

## 技术选型

### 后端技术栈

- **Web框架**: FastAPI (高性能，自动API文档)
- **项目管理**: Poetry (依赖管理、打包、虚拟环境)
- **数据库**: SQLite (轻量级，零配置)
- **缓存**: Redis (可选，用于高频查询缓存)
- **搜索引擎**: SQLite FTS (全文搜索)
- **任务调度**: APScheduler (定时任务)
- **HTTP客户端**: httpx (异步HTTP请求)

### 前端技术栈

- **框架**: Vue.js 3 + TypeScript
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **构建工具**: Vite

### 大模型能力

- **默认**: 本地 Ollama 接口，调用 Qwen2.5 模型
- **备选**: OpenAI API, 通义千问 API (可配置切换)
- **用途**: 内容摘要生成、分类标签提取、内容清洗

### 部署方案

- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx (可选)
- **进程管理**: Supervisor (可选)

## 数据库设计

### 核心表结构

```sql
-- 新闻源配置表
CREATE TABLE news_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    url TEXT NOT NULL,
    source_type VARCHAR(20) DEFAULT 'rss', -- rss, api
    is_active BOOLEAN DEFAULT TRUE,
    fetch_interval INTEGER DEFAULT 3600, -- 秒
    last_fetch_time DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 新闻文章表
CREATE TABLE news_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    url TEXT UNIQUE NOT NULL,
    source_id INTEGER,
    author VARCHAR(100),
    published_at DATETIME,
    fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_processed BOOLEAN DEFAULT FALSE,
    category VARCHAR(50),
    tags TEXT, -- JSON格式存储标签数组
    embedding_vector BLOB, -- 可选：文章向量表示
    chinese_title TEXT,           -- 中文标题
    llm_summary TEXT,             -- LLM 生成的摘要 (400字)
    original_language VARCHAR(10), -- 原文语言
    llm_processed_at DATETIME,     -- LLM 处理时间
    llm_processing_status VARCHAR(20) DEFAULT 'pending', -- pending/processing/completed/failed
    FOREIGN KEY (source_id) REFERENCES news_sources (id)
);

-- 分类表
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    parent_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (parent_id) REFERENCES categories (id)
);

-- 用户搜索日志 (可选)
CREATE TABLE search_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    result_count INTEGER,
    search_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45)
);

-- 全文搜索索引
CREATE VIRTUAL TABLE articles_fts USING fts5(
    title, summary, content, tags,
    content='news_articles'
);

-- 今日文章索引
CREATE INDEX idx_articles_today ON news_articles(published_at, llm_processing_status) 
WHERE DATE(published_at) = DATE('now');
```

## 领域模型

### 核心实体

```python
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from enum import Enum

class LLMProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class NewsSource(BaseModel):
    id: Optional[int] = None
    name: str
    url: HttpUrl
    source_type: str = "rss"  # rss, api
    is_active: bool = True
    fetch_interval: int = 3600  # 秒
    last_fetch_time: Optional[datetime] = None

class NewsArticle(BaseModel):
    id: Optional[int] = None
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    url: HttpUrl
    source_id: int
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    fetched_at: datetime
    is_processed: bool = False
    category: Optional[str] = None
    tags: List[str] = []
    # LLM 处理相关字段
    chinese_title: Optional[str] = None
    llm_summary: Optional[str] = None
    original_language: Optional[str] = None
    llm_processed_at: Optional[datetime] = None
    llm_processing_status: LLMProcessingStatus = LLMProcessingStatus.PENDING

class Category(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: bool = True

class SearchQuery(BaseModel):
    query: str
    limit: int = 20
    offset: int = 0
    category: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class TodayArticleView(BaseModel):
    """今日文章视图模型"""
    id: int
    original_title: str
    chinese_title: str
    url: str
    author: Optional[str]
    source_name: str
    published_at: datetime
    llm_summary: str
    original_language: str
    tags: List[str] = []
```

### 服务层接口

```python
from abc import ABC, abstractmethod

class NewsAggregatorService(ABC):
    @abstractmethod
    async def fetch_from_source(self, source: NewsSource) -> List[NewsArticle]:
        pass
    
    @abstractmethod
    async def schedule_fetch_tasks(self) -> None:
        pass

class SearchService(ABC):
    @abstractmethod
    async def search_articles(self, query: SearchQuery) -> List[NewsArticle]:
        pass
    
    @abstractmethod
    async def index_article(self, article: NewsArticle) -> None:
        pass
```

## 开放接口设计

### REST API 接口

```python
# 新闻相关接口
GET    /api/v1/articles              # 获取新闻列表
GET    /api/v1/articles/{id}         # 获取单篇新闻详情
GET    /api/v1/articles/search       # 搜索新闻
GET    /api/v1/categories            # 获取分类列表
GET    /api/v1/categories/{id}/articles  # 获取分类下的新闻

# RSS 订阅接口
GET    /api/v1/rss                   # RSS 订阅输出
GET    /api/v1/rss/{category}        # 分类 RSS 订阅

# 管理接口 (后台)
GET    /api/v1/admin/sources         # 获取新闻源列表
POST   /api/v1/admin/sources         # 添加新闻源
PUT    /api/v1/admin/sources/{id}    # 更新新闻源
DELETE /api/v1/admin/sources/{id}    # 删除新闻源
POST   /api/v1/admin/sources/{id}/fetch  # 手动触发抓取

# 系统状态接口
GET    /api/v1/health               # 健康检查
GET    /api/v1/stats                # 系统统计信息

# 今日文章接口
GET    /api/v1/today/articles        # 获取今日文章列表
GET    /api/v1/today/stats           # 获取今日统计信息
POST   /api/v1/today/process         # 手动触发今日文章处理
```

### 请求/响应格式

```python
# 新闻列表响应
class ArticleListResponse(BaseModel):
    total: int
    page: int
    size: int
    articles: List[NewsArticle]

# 搜索请求
class SearchRequest(BaseModel):
    q: str  # 搜索关键词
    category: Optional[str] = None
    page: int = 1
    size: int = 20
    sort: str = "published_at"  # published_at, relevance

# 统一错误响应
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None
```

## 关键技术实现

### 1. 新闻聚合策略

- RSS解析使用 `feedparser` 库
- 支持多线程/异步并发抓取
- 去重机制基于URL和内容hash
- 错误重试和熔断机制

### 2. 内容处理流程

- LLM调用封装，支持多种模型切换
- Prompt工程优化摘要生成质量
- 内容清洗去除HTML标签和广告
- 关键词提取和自动分类

### 3. 搜索优化

- SQLite FTS5全文搜索
- 搜索结果相关性排序
- 搜索关键词高亮显示
- 搜索历史和热门搜索

### 4. 缓存策略

- Redis缓存热门文章和搜索结果
- 浏览器缓存静态资源
- CDN加速图片和媒体资源

## 扩展性设计

### 1. 新闻源扩展

- 插件化新闻源适配器
- 支持RSS、API、爬虫等多种方式
- 动态配置新闻源参数

### 2. 分类算法扩展

- 支持基于规则、机器学习、LLM多种分类方式
- 分类器热插拔机制
- 人工标注反馈循环

### 3. 部署扩展

- 支持单机、集群部署
- 数据库读写分离
- 微服务化改造方案

## 项目结构设计

### Poetry 项目管理

使用 Poetry 进行 Python 项目的依赖管理、打包和虚拟环境管理，提供更好的开发体验和部署一致性。

### 项目目录结构

```text
ai-news/
├── pyproject.toml              # Poetry 配置文件
├── poetry.lock                 # 锁定的依赖版本
├── README.md                   # 项目说明文档
├── SA_README.md               # 技术架构设计文档
├── .env.example               # 环境变量模板
├── .gitignore                 # Git 忽略文件
├── Dockerfile                 # Docker 构建文件
├── docker-compose.yml         # Docker Compose 配置
├── Makefile                   # 构建和运行脚本
│
├── ai_news/                   # 主应用包
│   ├── __init__.py
│   ├── main.py                # FastAPI 应用入口
│   ├── config.py              # 配置管理
│   ├── dependencies.py        # 依赖注入
│   │
│   ├── api/                   # API 路由层
│   │   ├── __init__.py
│   │   ├── v1/                # API v1 版本
│   │   │   ├── __init__.py
│   │   │   ├── articles.py    # 新闻文章 API
│   │   │   ├── search.py      # 搜索 API
│   │   │   ├── categories.py  # 分类 API
│   │   │   ├── sources.py     # 新闻源管理 API
│   │   │   └── rss.py         # RSS 订阅 API
│   │   └── admin/             # 管理后台 API
│   │       ├── __init__.py
│   │       ├── sources.py     # 新闻源管理
│   │       └── stats.py       # 统计信息
│   │
│   ├── core/                  # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── aggregator.py      # 新闻聚合服务
│   │   ├── processor.py       # 内容处理服务
│   │   ├── search.py          # 搜索服务
│   │   ├── classifier.py      # 分类服务
│   │   └── scheduler.py       # 定时任务调度
│   │
│   ├── models/                # 数据模型
│   │   ├── __init__.py
│   │   ├── database.py        # 数据库连接和会话
│   │   ├── article.py         # 新闻文章模型
│   │   ├── source.py          # 新闻源模型
│   │   ├── category.py        # 分类模型
│   │   └── search_log.py      # 搜索日志模型
│   │
│   ├── schemas/               # Pydantic 数据模式
│   │   ├── __init__.py
│   │   ├── article.py         # 新闻文章模式
│   │   ├── source.py          # 新闻源模式
│   │   ├── category.py        # 分类模式
│   │   ├── search.py          # 搜索模式
│   │   └── common.py          # 通用模式
│   │
│   ├── services/              # 业务服务层
│   │   ├── __init__.py
│   │   ├── article_service.py # 新闻文章服务
│   │   ├── source_service.py  # 新闻源服务
│   │   ├── search_service.py  # 搜索服务
│   │   ├── llm_service.py     # LLM 服务
│   │   └── cache_service.py   # 缓存服务
│   │
│   ├── utils/                 # 工具函数
│   │   ├── __init__.py
│   │   ├── rss_parser.py      # RSS 解析工具
│   │   ├── text_utils.py      # 文本处理工具
│   │   ├── date_utils.py      # 日期处理工具
│   │   ├── cache_utils.py     # 缓存工具
│   │   └── logger.py          # 日志工具
│   │
│   └── db/                    # 数据库相关
│       ├── __init__.py
│       ├── migrations/        # 数据库迁移脚本
│       │   ├── 001_init.sql   # 初始化数据库
│       │   └── 002_fts.sql    # 全文搜索索引
│       └── seeds/             # 种子数据
│           └── news_sources.json # 默认新闻源
│
├── frontend/                  # 前端应用 (Vue.js)
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── components/        # Vue 组件
│   │   ├── views/             # 页面视图
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── services/          # API 服务
│   │   ├── types/             # TypeScript 类型定义
│   │   └── assets/            # 静态资源
│   └── dist/                  # 构建输出
│
├── tests/                     # 测试代码
│   ├── __init__.py
│   ├── conftest.py            # pytest 配置
│   ├── test_api/              # API 测试
│   │   ├── test_articles.py
│   │   ├── test_search.py
│   │   └── test_sources.py
│   ├── test_core/             # 核心逻辑测试
│   │   ├── test_aggregator.py
│   │   ├── test_processor.py
│   │   └── test_classifier.py
│   └── test_utils/            # 工具函数测试
│       ├── test_rss_parser.py
│       └── test_text_utils.py
│
├── scripts/                   # 脚本文件
│   ├── init_db.py            # 初始化数据库
│   ├── seed_data.py          # 导入种子数据
│   ├── fetch_news.py         # 手动抓取新闻
│   └── backup_db.py          # 数据库备份
│
├── docs/                     # 文档
│   ├── api.md                # API 文档
│   ├── deployment.md         # 部署文档
│   └── development.md        # 开发指南
│
├── config/                   # 配置文件
│   ├── logging.yaml          # 日志配置
│   ├── nginx.conf            # Nginx 配置
│   └── supervisor.conf       # Supervisor 配置
│
└── data/                     # 数据目录
    ├── database/             # 数据库文件
    ├── logs/                 # 日志文件
    └── cache/                # 缓存文件
```

### Makefile 示例

```makefile
.PHONY: install dev test lint format clean build run docker-build docker-run

# 安装依赖
install:
    poetry install

# 安装开发依赖
dev:
    poetry install --with dev,test

# 运行测试
test:
    poetry run pytest

# 代码检查
lint:
    poetry run flake8 ai_news tests
    poetry run mypy ai_news

# 代码格式化
format:
    poetry run black ai_news tests scripts
    poetry run isort ai_news tests scripts

# 清理缓存
clean:
    find . -type d -name __pycache__ -delete
    find . -type f -name "*.pyc" -delete
    rm -rf .coverage htmlcov/ .pytest_cache/

# 构建包
build:
    poetry build

# 运行应用
run:
    poetry run uvicorn ai_news.main:app --reload --host 0.0.0.0 --port 8000

# 初始化数据库
init-db:
    poetry run python scripts/init_db.py

# 导入种子数据
seed-data:
    poetry run python scripts/seed_data.py

# Docker 构建
docker-build:
    docker build -t ai-news .

# Docker 运行
docker-run:
    docker-compose up -d

# 开发环境启动
dev-start: install init-db seed-data
    poetry run uvicorn ai_news.main:app --reload
```

### 开发流程

1. **项目初始化**

   ```bash
   # 克隆项目
   git clone <repository-url>
   cd ai-news
   
   # 安装依赖
   make dev
   
   # 初始化数据库
   make init-db
   
   # 导入种子数据
   make seed-data
   ```

2. **开发启动**

   ```bash
   # 启动后端服务
   make run
   
   # 启动前端服务 (另一个终端)
   cd frontend
   npm run dev
   ```

3. **代码质量**

   ```bash
   # 代码格式化
   make format
   
   # 代码检查
   make lint
   
   # 运行测试
   make test
   ```

4. **部署**

   ```bash
   # Docker 部署
   make docker-build
   make docker-run
   
   # 或者生产部署
   poetry build
   poetry run gunicorn ai_news.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### 关键设计决策

1. **模块化分层**: 严格按照 API -> Service -> Model 分层，职责清晰
2. **依赖注入**: 使用 FastAPI 的依赖注入系统，便于测试和扩展
3. **配置管理**: 使用 Pydantic Settings 进行配置管理，支持环境变量
4. **异步支持**: 全面使用异步编程，提高并发性能
5. **类型安全**: 使用 TypeScript (前端) 和 Python 类型注解，减少运行时错误
6. **测试友好**: 完整的测试结构，支持单元测试和集成测试

## 架构设计补充项

### 1. 安全性设计

```python
# 安全配置
class SecurityConfig:
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    RATE_LIMIT_PER_MINUTE: int = 60
    
# 认证中间件
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # JWT token验证逻辑
    pass
```

### 2. 错误处理和监控

```python
# 全局异常处理
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "path": request.url.path
        }
    )

# 日志配置
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/app.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
```

### 3. 性能优化配置

```python
# 数据库连接池配置
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite:///./data/database/ai_news.db",
    poolclass=StaticPool,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# 缓存配置
from functools import lru_cache
import redis

@lru_cache()
def get_redis_client():
    return redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True,
        socket_keepalive=True,
        socket_keepalive_options={}
    )
```

### 4. 任务调度详细配置

```python
# 定时任务配置
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

executors = {
    'default': AsyncIOExecutor(),
}

job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults
)
```

### 5. 环境配置管理

```python
# .env 文件配置
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
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
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:latest"
    
    # API密钥
    OPENAI_API_KEY: str = ""
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ADMIN_PASSWORD: str = "admin123"
    
    # 新闻抓取配置
    DEFAULT_FETCH_INTERVAL: int = 3600  # 1小时
    MAX_ARTICLES_PER_SOURCE: int = 50
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 6. 数据库迁移管理

```python
# alembic配置
# alembic/env.py
from alembic import context
from sqlalchemy import engine_from_config, pool
from ai_news.models.database import Base

config = context.config
target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
```

### 7. 前端状态管理完善

```typescript
// stores/articles.ts
import { defineStore } from 'pinia'
import type { Article, SearchQuery } from '@/types/article'

export const useArticlesStore = defineStore('articles', {
  state: () => ({
    articles: [] as Article[],
    loading: false,
    error: null as string | null,
    currentPage: 1,
    totalPages: 0,
    searchQuery: '' as string,
    selectedCategory: null as string | null
  }),

  actions: {
    async fetchArticles(page: number = 1) {
      this.loading = true
      try {
        const response = await api.getArticles({ page, size: 20 })
        this.articles = response.articles
        this.totalPages = Math.ceil(response.total / 20)
        this.currentPage = page
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    async searchArticles(query: SearchQuery) {
      this.loading = true
      try {
        const response = await api.searchArticles(query)
        this.articles = response.articles
        this.searchQuery = query.q
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    }
  }
})
```

### 8. Docker部署配置

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装Poetry
RUN pip install poetry

# 复制依赖配置
COPY pyproject.toml poetry.lock ./

# 安装依赖
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p data/database data/logs

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "ai_news.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/database/ai_news.db
      - REDIS_URL=redis://redis:6379
      - REDIS_ENABLED=true
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - app
    restart: unless-stopped

volumes:
  redis_data:
```

### 9. 测试覆盖率提升

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ai_news.main import app
from ai_news.models.database import Base, get_db

# 测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)
```

### 10. 生产环境监控

```python
# 健康检查增强
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": settings.VERSION,
        "database": await check_database_health(),
        "redis": await check_redis_health(),
        "ollama": await check_ollama_health()
    }

# 指标监控
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## LLM 架构设计

### LLM 在本项目中的核心作用

LLM (Large Language Model) 在本项目中的主要功能是**将 RSS 文章内容压缩为 400字左右的浓缩信息**，方便用户快速阅读，同时提供多语言内容的中文翻译服务。

### 高内聚低耦合的 LLM 架构设计

#### 1. 抽象接口层 (Interface Layer)

采用**适配器模式**和**策略模式**，定义统一的 LLM 服务接口，实现高内聚低耦合：

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum

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
```

#### 2. 配置管理层 (Configuration Layer)

支持多种 LLM 提供商的统一配置管理：

```python
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

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
    base_url: str = "http://localhost:11434"
    model: str = "qwen2.5"
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
    
    @classmethod
    def from_env(cls) -> 'LLMConfig':
        """从环境变量创建配置"""
        # 实现从环境变量读取配置的逻辑
        pass
```

#### 3. 适配器实现层 (Adapter Layer)

为每个 LLM 提供商实现具体的适配器：

```python
import httpx
import asyncio
import json
from typing import Dict, Any, List

class OllamaAdapter(LLMServiceInterface):
    """Ollama 适配器实现"""
    
    def __init__(self, config: OllamaConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=config.timeout)
    
    async def summarize_content(self, content: str, target_length: int = 400, **kwargs) -> str:
        """使用 Ollama 生成摘要"""
        prompt = self._build_summary_prompt(content, target_length)
        return await self._call_ollama(prompt)
    
    async def translate_to_chinese(self, text: str, source_language: str = "auto", **kwargs) -> str:
        """使用 Ollama 翻译为中文"""
        if source_language.lower() in ['zh', 'zh-cn', 'chinese']:
            return text
        
        prompt = self._build_translation_prompt(text, source_language)
        return await self._call_ollama(prompt)
    
    async def detect_language(self, text: str, **kwargs) -> str:
        """使用 Ollama 检测语言"""
        prompt = f"请检测以下文本的语言，只返回语言代码（如：en, zh, ja等）：\n\n{text[:200]}"
        response = await self._call_ollama(prompt)
        return response.strip().lower()
    
    async def extract_keywords(self, content: str, max_keywords: int = 5, **kwargs) -> List[str]:
        """提取关键词"""
        prompt = f"请从以下文本中提取{max_keywords}个最重要的关键词，以逗号分隔：\n\n{content}"
        response = await self._call_ollama(prompt)
        return [kw.strip() for kw in response.split(',')][:max_keywords]
    
    async def categorize_article(self, title: str, content: str, categories: List[str], **kwargs) -> str:
        """文章分类"""
        categories_str = "、".join(categories)
        prompt = f"请将以下文章分类到最合适的类别中，候选类别：{categories_str}\n\n标题：{title}\n\n内容：{content[:500]}\n\n分类："
        response = await self._call_ollama(prompt)
        return response.strip()
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            response = await self.client.get(f"{self.config.base_url}/api/tags")
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
    
    async def _call_ollama(self, prompt: str) -> str:
        """调用 Ollama API"""
        try:
            response = await self.client.post(
                f"{self.config.base_url}/api/generate",
                json={
                    "model": self.config.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.config.temperature
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            raise LLMProcessingError(f"Ollama API 调用失败: {e}")
    
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

class OpenAIAdapter(LLMServiceInterface):
    """OpenAI 适配器实现"""
    
    def __init__(self, config: OpenAIConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            timeout=config.timeout,
            headers={"Authorization": f"Bearer {config.api_key}"}
        )
    
    async def summarize_content(self, content: str, target_length: int = 400, **kwargs) -> str:
        """使用 OpenAI 生成摘要"""
        messages = [
            {"role": "system", "content": "你是一个专业的文章摘要助手。"},
            {"role": "user", "content": self._build_summary_prompt(content, target_length)}
        ]
        return await self._call_openai(messages)
    
    async def translate_to_chinese(self, text: str, source_language: str = "auto", **kwargs) -> str:
        """使用 OpenAI 翻译为中文"""
        if source_language.lower() in ['zh', 'zh-cn', 'chinese']:
            return text
        
        messages = [
            {"role": "system", "content": "你是一个专业的翻译助手。"},
            {"role": "user", "content": self._build_translation_prompt(text, source_language)}
        ]
        return await self._call_openai(messages)
    
    # ... 其他方法实现类似
    
    async def _call_openai(self, messages: List[Dict[str, str]]) -> str:
        """调用 OpenAI API"""
        try:
            response = await self.client.post(
                f"{self.config.base_url}/chat/completions",
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise LLMProcessingError(f"OpenAI API 调用失败: {e}")

# 类似地实现其他适配器...
class HuoshanAdapter(LLMServiceInterface):
    """火山引擎适配器实现"""
    # 实现火山引擎的具体接口调用逻辑
    pass

class QianwenAdapter(LLMServiceInterface):
    """阿里千问适配器实现"""
    # 实现千问的具体接口调用逻辑
    pass
```

#### 4. 工厂模式和服务管理层 (Factory & Service Layer)

```python
from typing import Dict, Type

class LLMAdapterFactory:
    """LLM 适配器工厂"""
    
    _adapters: Dict[LLMProvider, Type[LLMServiceInterface]] = {
        LLMProvider.OLLAMA: OllamaAdapter,
        LLMProvider.OPENAI: OpenAIAdapter,
        LLMProvider.HUOSHAN: HuoshanAdapter,
        LLMProvider.QIANWEN: QianwenAdapter,
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
                except Exception as e:
                    logger.error(f"初始化 {provider} 适配器失败: {e}")
    
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

class LLMProcessingError(Exception):
    """LLM 处理异常"""
    pass
```

#### 5. 使用示例和扩展指南

```python
# 配置示例
async def setup_llm_service():
    """设置 LLM 服务的完整示例"""
    
    # 1. 创建配置
    config = LLMConfig(
        default_provider=LLMProvider.OLLAMA,
        providers={
            LLMProvider.OLLAMA: OllamaConfig(
                base_url="http://localhost:11434",
                model="qwen2.5"
            ),
            LLMProvider.OPENAI: OpenAIConfig(
                api_key="sk-xxx",
                model="gpt-3.5-turbo"
            ),
            LLMProvider.QIANWEN: QianwenConfig(
                api_key="your-qianwen-key",
                model="qwen-turbo"
            )
        },
        enable_fallback=True,
        fallback_order=[
            LLMProvider.OLLAMA,
            LLMProvider.OPENAI, 
            LLMProvider.QIANWEN
        ]
    )
    
    # 2. 创建服务管理器
    llm_manager = LLMServiceManager(config)
    
    # 3. 使用服务
    content = "这是一篇很长的文章内容..."
    summary = await llm_manager.summarize_content(content, target_length=400)
    
    # 4. 切换提供商
    llm_manager.switch_default_provider(LLMProvider.OPENAI)
    
    # 5. 健康检查
    health_status = await llm_manager.health_check_all()
    print(health_status)

# 自定义适配器扩展示例
class CustomLLMAdapter(LLMServiceInterface):
    """自定义 LLM 适配器示例"""
    
    def __init__(self, config: LLMProviderConfig):
        self.config = config
    
    async def summarize_content(self, content: str, target_length: int = 400, **kwargs) -> str:
        # 实现自定义的摘要逻辑
        pass
    
    # ... 实现其他必需方法

# 注册自定义适配器
LLMAdapterFactory.register_adapter(LLMProvider.CUSTOM, CustomLLMAdapter)
```

### 架构优势

1. **高内聚低耦合**:
   - 每个适配器只关注特定 LLM 提供商的实现
   - 统一接口隔离了具体实现细节
   - 服务管理器提供统一入口

2. **易扩展**:
   - 新增 LLM 提供商只需实现接口并注册
   - 支持自定义适配器扩展
   - 配置驱动的灵活性

3. **高可用**:
   - 自动回退机制保证服务可用性
   - 健康检查监控各提供商状态
   - 可动态切换默认提供商

4. **便于测试**:
   - 接口抽象便于 Mock 测试
   - 适配器模式支持单独测试
   - 配置外部化便于测试环境隔离

### "今日" 功能设计

**功能概述**: "今日"功能将所有订阅 RSS 的当日文章按照发布顺序展示，包含原始信息和 LLM 处理后的内容。

#### 功能特性

1. **智能内容压缩**: 将任意长度的文章内容压缩为约 400字的精华摘要
2. **多语言翻译**: 将所有语言的内容统一翻译为中文
3. **时间排序**: 按照文章发布时间顺序展示
4. **完整信息保留**: 保留原文标题、链接、作者、发布日期等元信息

### 业务服务层 (Business Service Layer)

### 异步处理和调度 (Async Processing & Scheduling)

### "今日" 功能 API 设计

### 前端界面设计

#### "今日"

### 配置管理

```python
# LLM 相关配置
class LLMSettings(BaseSettings):
    # 默认提供商配置
    DEFAULT_PROVIDER: str = "ollama"
    
    # Ollama 配置
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5"
    OLLAMA_TIMEOUT: int = 60
    
    # OpenAI 配置
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
    
    # 处理配置
    SUMMARY_TARGET_LENGTH: int = 400
    BATCH_PROCESS_SIZE: int = 50
    MAX_RETRIES: int = 3
    ENABLE_FALLBACK: bool = True
    
    # 队列配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    class Config:
        env_prefix = "LLM_"

# 使用示例
llm_settings = LLMSettings()

# 根据配置创建 LLM 管理器

## 总结

本技术架构设计文档涵盖了 AI News 项目的完整技术栈和实现方案，重点突出了 **LLM 模块的高内聚低耦合架构设计**：

### 核心特性

1. **RSS 内容聚合**: 支持多种 RSS 源的自动抓取和内容解析
2. **LLM 智能处理**: 将文章内容压缩为 400字中文摘要，支持多语言翻译
3. **"今日"功能**: 展示当日所有文章的智能摘要，便于快速阅读
4. **多模型支持**: 支持 Ollama、OpenAI、火山引擎、阿里千问等多种 LLM 服务
5. **高可用设计**: 自动回退机制、健康检查、异步处理

### LLM 架构优势

- **高内聚**: 每个适配器专注于特定 LLM 提供商实现
- **低耦合**: 统一接口抽象，便于扩展和测试
- **易切换**: 配置驱动的提供商切换机制
- **高可用**: 多提供商回退机制保证服务稳定性

该架构设计确保了系统的可扩展性、可维护性和高可用性，为 AI 新闻聚合项目提供了坚实的技术基础。
