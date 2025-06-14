# AI News 项目 Makefile

.PHONY: help install dev-deps test lint format clean build run docker-build docker-run
.PHONY: dev-env prod-env stop-all status logs health-check

# 默认目标
help: ## 显示帮助信息
	@echo "AI News 项目管理命令:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'
	@echo ""
	@echo "示例:"
	@echo "  make dev-env     # 启动开发环境"
	@echo "  make prod-env    # 启动生产环境"
	@echo "  make stop-all    # 停止所有服务"

# Python 环境相关
install: ## 安装 Python 依赖
	poetry install

dev-deps: ## 安装开发依赖
	poetry install --with dev,test

# 开发环境管理
dev-env: ## 启动开发环境 (后端容器 + 前端本地)
	@echo "启动开发环境..."
	@./start-fullstack.sh dev

prod-env: ## 启动生产环境 (所有服务容器化)
	@echo "启动生产环境..."
	@./start-fullstack.sh prod

stop-all: ## 停止所有服务
	@echo "停止所有服务..."
	@./start-fullstack.sh stop

status: ## 查看服务状态
	@./start-fullstack.sh status

logs: ## 查看所有服务日志
	@./start-fullstack.sh logs

logs-backend: ## 查看后端日志
	@./start-fullstack.sh logs backend

health-check: ## 检查服务健康状态
	@echo "检查后端健康状态..."
	@curl -f http://localhost:8000/api/v1/health || echo "后端服务不可用"
	@echo "检查前端健康状态..."
	@curl -f http://localhost:3000/ || echo "前端服务不可用"

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
