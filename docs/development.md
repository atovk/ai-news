# AI News - 开发指南

## 快速开始

### 1. 环境准备

确保您的系统已安装：
- Python 3.9+
- Poetry (Python包管理工具)

### 2. 项目初始化

```bash
# 克隆项目
git clone <repository-url>
cd ai-news

# 复制环境变量文件
cp .env.example .env

# 安装依赖
make dev

# 初始化数据库
make init-db

# 导入种子数据
make seed-data
```

### 3. 启动开发服务器

```bash
# 启动后端服务
make run

# 访问API文档
open http://localhost:8000/docs
```

## 开发工作流

### 代码质量检查

```bash
# 代码格式化
make format

# 代码检查
make lint

# 运行测试
make test
```

### 数据库操作

```bash
# 重新初始化数据库
make init-db

# 手动抓取新闻
poetry run python scripts/fetch_news.py
```

## API 使用示例

### 获取新闻列表

```bash
curl http://localhost:8000/api/v1/articles/
```

### 搜索新闻

```bash
curl "http://localhost:8000/api/v1/search/?q=artificial%20intelligence"
```

### 管理新闻源

```bash
# 获取新闻源列表
curl http://localhost:8000/api/v1/sources/

# 添加新闻源
curl -X POST http://localhost:8000/api/v1/sources/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example News",
    "url": "https://example.com/rss",
    "source_type": "rss"
  }'
```

## 部署

### Docker 部署

```bash
# 构建镜像
make docker-build

# 启动服务
make docker-run
```

### 生产部署

```bash
# 安装生产依赖
poetry install --no-dev

# 启动生产服务器
poetry run gunicorn ai_news.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 `DATABASE_URL` 配置
   - 确保数据目录存在且有写权限

2. **RSS抓取失败**
   - 检查网络连接
   - 验证RSS源URL是否有效

3. **依赖安装失败**
   - 升级Poetry: `pip install --upgrade poetry`
   - 清理缓存: `poetry cache clear pypi --all`

### 日志查看

```bash
# 查看应用日志
tail -f data/logs/app.log

# 查看Docker日志
docker-compose logs -f app
```
