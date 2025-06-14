#!/bin/bash

# AI News "今日"功能部署脚本

echo "开始部署 AI News 今日功能..."

# 1. 检查依赖
echo "检查依赖..."
poetry --version || { echo "请先安装 Poetry"; exit 1; }

# 2. 安装依赖
echo "安装项目依赖..."
poetry install

# 3. 运行数据库迁移
echo "运行数据库迁移..."
poetry run python scripts/migrate_llm_fields.py

# 4. 创建测试数据（可选）
echo "是否创建测试数据？(y/n)"
read -p "请选择: " choice
if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
    echo "创建测试数据..."
    poetry run python scripts/test_today_feature.py
fi

# 5. 启动服务
echo "启动服务..."
echo "访问 http://localhost:8000/docs 查看API文档"
echo "访问 http://localhost:8000/api/v1/today 使用今日功能"
echo ""
echo "按 Ctrl+C 停止服务"

poetry run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
