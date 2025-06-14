#!/bin/bash

# AI 新闻项目启动脚本 - 前后端一体化

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${BLUE}=== AI 新闻项目启动脚本 ===${NC}"
echo -e "${BLUE}项目目录: $PROJECT_ROOT${NC}"

# 检查必要的工具
check_requirements() {
    echo -e "${YELLOW}检查环境要求...${NC}"
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}错误: 未找到 Docker，请先安装 Docker${NC}"
        exit 1
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}错误: 未找到 Docker Compose，请先安装 Docker Compose${NC}"
        exit 1
    fi
    
    # 检查 Node.js (用于前端开发)
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node -v | sed 's/v//')
        echo -e "${GREEN}✓ Node.js 版本: $NODE_VERSION${NC}"
    else
        echo -e "${YELLOW}! 未找到 Node.js，前端开发模式将不可用${NC}"
    fi
    
    # 检查 Python (用于后端开发)
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo -e "${GREEN}✓ Python 版本: $PYTHON_VERSION${NC}"
    fi
    
    echo -e "${GREEN}✓ 环境检查完成${NC}"
}

# 启动开发环境
start_dev() {
    echo -e "${YELLOW}启动开发环境...${NC}"
    
    # 启动后端服务 (仅后端和依赖服务)
    echo -e "${BLUE}启动后端服务...${NC}"
    if [ -f "docker-compose.dev.yml" ]; then
        docker-compose -f docker-compose.dev.yml up -d
    else
        echo -e "${RED}未找到 docker-compose.dev.yml 文件${NC}"
        exit 1
    fi
    
    # 等待后端启动
    echo -e "${YELLOW}等待后端服务启动...${NC}"
    
    # 检查后端健康状态
    check_backend_health() {
        local max_attempts=30
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if curl -f http://localhost:8000/api/v1/health &> /dev/null; then
                echo -e "${GREEN}✓ 后端服务已就绪${NC}"
                return 0
            fi
            
            echo -e "${YELLOW}等待后端服务... ($attempt/$max_attempts)${NC}"
            sleep 2
            ((attempt++))
        done
        
        echo -e "${RED}后端服务启动失败或超时${NC}"
        return 1
    }
    
    if check_backend_health; then
        # 启动前端开发服务器 (本地方式，避免与Docker冲突)
        if [ -d "$FRONTEND_DIR" ] && command -v node &> /dev/null; then
            echo -e "${BLUE}启动前端开发服务器...${NC}"
            cd "$FRONTEND_DIR"
            
            # 检查并安装依赖
            if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
                echo -e "${YELLOW}安装/更新前端依赖...${NC}"
                if command -v pnpm &> /dev/null; then
                    pnpm install
                elif command -v yarn &> /dev/null; then
                    yarn install
                else
                    npm install
                fi
            fi
            
            # 设置环境变量指向后端API
            export VITE_API_BASE_URL=http://localhost:8000
            
            # 启动开发服务器
            echo -e "${GREEN}启动前端开发服务器 (http://localhost:5173)...${NC}"
            if command -v pnpm &> /dev/null; then
                pnpm dev
            elif command -v yarn &> /dev/null; then
                yarn dev
            else
                npm run dev
            fi
        else
            echo -e "${YELLOW}前端开发环境不可用，请手动进入 frontend 目录运行 npm run dev${NC}"
            echo -e "${BLUE}或访问后端服务: http://localhost:8000${NC}"
        fi
    else
        echo -e "${RED}无法启动前端，后端服务未就绪${NC}"
        exit 1
    fi
}

# 启动生产环境
start_prod() {
    echo -e "${YELLOW}启动生产环境...${NC}"
    
    # 使用完整的 docker-compose.yml 启动所有服务
    if [ -f "docker-compose.yml" ]; then
        echo -e "${BLUE}构建并启动所有服务...${NC}"
        docker-compose up -d --build
        
        # 等待服务启动
        echo -e "${YELLOW}等待服务启动...${NC}"
        sleep 15
        
        # 检查服务状态
        echo -e "${BLUE}检查服务状态...${NC}"
        docker-compose ps
        
        echo -e "${GREEN}✓ 生产环境启动完成${NC}"
        echo -e "${BLUE}访问地址:${NC}"
        echo -e "  前端: http://localhost:3000"
        echo -e "  后端: http://localhost:8000"
        echo -e "  API文档: http://localhost:8000/docs"
    else
        echo -e "${RED}未找到 docker-compose.yml 文件${NC}"
        exit 1
    fi
}

# 停止服务
stop_services() {
    echo -e "${YELLOW}停止所有服务...${NC}"
    
    # 停止开发环境
    if [ -f "docker-compose.dev.yml" ]; then
        echo -e "${BLUE}停止开发环境...${NC}"
        docker-compose -f docker-compose.dev.yml down
    fi
    
    # 停止生产环境
    if [ -f "docker-compose.yml" ]; then
        echo -e "${BLUE}停止生产环境...${NC}"
        docker-compose down
    fi
    
    # 尝试停止可能在运行的前端开发服务器
    if command -v pkill &> /dev/null; then
        pkill -f "vite" 2>/dev/null || true
        pkill -f "webpack-dev-server" 2>/dev/null || true
        pkill -f "npm.*dev" 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✓ 所有服务已停止${NC}"
}

# 查看服务状态
show_status() {
    echo -e "${BLUE}=== 服务状态 ===${NC}"
    
    if [ -f "docker-compose.dev.yml" ]; then
        echo -e "${YELLOW}开发环境 (docker-compose.dev.yml):${NC}"
        docker-compose -f docker-compose.dev.yml ps
    fi
    
    if [ -f "docker-compose.yml" ]; then
        echo -e "${YELLOW}生产环境 (docker-compose.yml):${NC}"
        docker-compose ps
    fi
}

# 查看日志
show_logs() {
    local service="${2:-}"
    local env="${3:-dev}"
    
    echo -e "${BLUE}=== 服务日志 ===${NC}"
    
    if [ "$env" = "prod" ] && [ -f "docker-compose.yml" ]; then
        if [ -n "$service" ]; then
            docker-compose logs -f "$service"
        else
            docker-compose logs -f
        fi
    elif [ -f "docker-compose.dev.yml" ]; then
        if [ -n "$service" ]; then
            docker-compose -f docker-compose.dev.yml logs -f "$service"
        else
            docker-compose -f docker-compose.dev.yml logs -f
        fi
    else
        echo -e "${RED}未找到对应的 docker-compose 文件${NC}"
        exit 1
    fi
}

# 清理数据
clean_data() {
    echo -e "${YELLOW}清理项目数据...${NC}"
    
    # 停止服务
    stop_services
    
    # 清理 Docker 镜像和容器
    echo -e "${YELLOW}清理 Docker 资源...${NC}"
    docker system prune -f
    
    # 清理前端构建产物
    if [ -d "$FRONTEND_DIR/dist" ]; then
        echo -e "${YELLOW}清理前端构建产物...${NC}"
        rm -rf "$FRONTEND_DIR/dist"
    fi
    
    if [ -d "$FRONTEND_DIR/node_modules" ]; then
        echo -e "${YELLOW}清理前端依赖...${NC}"
        rm -rf "$FRONTEND_DIR/node_modules"
    fi
    
    echo -e "${GREEN}✓ 清理完成${NC}"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  dev          启动开发环境"
    echo "  prod         启动生产环境"
    echo "  stop         停止所有服务"
    echo "  status       查看服务状态"
    echo "  logs [服务]  查看服务日志"
    echo "  clean        清理项目数据"
    echo "  help         显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 dev           # 启动开发环境"
    echo "  $0 prod          # 启动生产环境"
    echo "  $0 logs backend  # 查看后端日志"
    echo "  $0 clean         # 清理所有数据"
    echo ""
    echo "开发环境访问地址:"
    echo "  前端: http://localhost:3000"
    echo "  后端: http://localhost:8000"
    echo "  API文档: http://localhost:8000/docs"
}

# 主函数
main() {
    case "${1:-help}" in
        "dev"|"d")
            check_requirements
            start_dev
            ;;
        "prod"|"p")
            check_requirements
            start_prod
            ;;
        "stop"|"s")
            stop_services
            ;;
        "status"|"st")
            show_status
            ;;
        "logs"|"l")
            show_logs "$@"
            ;;
        "clean"|"c")
            read -p "确定要清理所有数据吗？这将删除构建产物和依赖包 (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                clean_data
            else
                echo -e "${YELLOW}操作已取消${NC}"
            fi
            ;;
        "help"|"h"|"--help"|"-h")
            show_help
            ;;
        *)
            echo -e "${RED}未知命令: $1${NC}"
            show_help
            exit 1
            ;;
    esac
}

# 捕获中断信号
trap 'echo -e "\n${YELLOW}操作已取消${NC}"; exit 1' INT

# 执行主函数
main "$@"
