#!/bin/bash

# 前端容器等待后端就绪脚本

set -e

# 等待后端服务就绪
wait_for_backend() {
    local backend_url="${BACKEND_URL:-http://backend:8000}"
    local max_attempts="${MAX_WAIT_ATTEMPTS:-60}"
    local attempt=1
    
    echo "等待后端服务就绪 ($backend_url)..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f "$backend_url/api/v1/health" &> /dev/null; then
            echo "✓ 后端服务已就绪"
            return 0
        fi
        
        echo "等待后端服务... ($attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    echo "错误: 后端服务启动超时"
    return 1
}

# 等待函数
wait_for_backend

# 启动 nginx
echo "启动 Nginx..."
exec "$@"
