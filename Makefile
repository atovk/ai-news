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
