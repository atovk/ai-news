FROM python:3.11-slim

# 设置工作目录
WORKDIR /

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装Poetry
RUN pip install poetry

# 配置Poetry
RUN poetry config virtualenvs.create false

# 复制依赖配置文件
COPY pyproject.toml poetry.lock ./

# 安装Python依赖 (不安装当前项目，只安装依赖)
RUN poetry install --no-root

# 复制应用代码
COPY . .

# 安装当前项目
RUN poetry install --only-root

# 创建数据目录
RUN mkdir -p data/database data/logs data/cache

# 设置环境变量
ENV PYTHONPATH=/
ENV DATABASE_URL=sqlite:///./data/database/ai_news.db

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
