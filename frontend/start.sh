#!/bin/bash

# AI 新闻前端启动脚本

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

echo -e "${BLUE}=== AI 新闻前端启动脚本 ===${NC}"

# 检查 Node.js 环境
check_node() {
    if ! command -v node &> /dev/null; then
        echo -e "${RED}错误: 未找到 Node.js，请先安装 Node.js (>= 16.0.0)${NC}"
        exit 1
    fi
    
    NODE_VERSION=$(node -v | sed 's/v//')
    REQUIRED_VERSION="16.0.0"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$NODE_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        echo -e "${RED}错误: Node.js 版本过低，需要 >= $REQUIRED_VERSION，当前版本: $NODE_VERSION${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Node.js 版本检查通过: $NODE_VERSION${NC}"
}

# 检查项目目录
check_project() {
    if [ ! -d "$FRONTEND_DIR" ]; then
        echo -e "${RED}错误: 前端目录不存在: $FRONTEND_DIR${NC}"
        exit 1
    fi
    
    if [ ! -f "$FRONTEND_DIR/package.json" ]; then
        echo -e "${RED}错误: 未找到 package.json 文件${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ 项目目录检查通过${NC}"
}

# 安装依赖
install_deps() {
    echo -e "${YELLOW}正在安装依赖...${NC}"
    cd "$FRONTEND_DIR"
    
    if command -v yarn &> /dev/null; then
        echo -e "${BLUE}使用 Yarn 安装依赖${NC}"
        yarn install
    else
        echo -e "${BLUE}使用 NPM 安装依赖${NC}"
        npm install
    fi
    
    echo -e "${GREEN}✓ 依赖安装完成${NC}"
}

# 启动开发服务器
start_dev() {
    echo -e "${YELLOW}正在启动开发服务器...${NC}"
    cd "$FRONTEND_DIR"
    
    if command -v yarn &> /dev/null; then
        yarn dev
    else
        npm run dev
    fi
}

# 构建生产版本
build_prod() {
    echo -e "${YELLOW}正在构建生产版本...${NC}"
    cd "$FRONTEND_DIR"
    
    if command -v yarn &> /dev/null; then
        yarn build
    else
        npm run build
    fi
    
    echo -e "${GREEN}✓ 构建完成，输出目录: $FRONTEND_DIR/dist${NC}"
}

# 预览生产版本
preview_prod() {
    echo -e "${YELLOW}正在启动预览服务器...${NC}"
    cd "$FRONTEND_DIR"
    
    if command -v yarn &> /dev/null; then
        yarn preview
    else
        npm run preview
    fi
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  dev, d     启动开发服务器"
    echo "  build, b   构建生产版本"
    echo "  preview, p 预览生产版本"
    echo "  install, i 安装依赖"
    echo "  help, h    显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 dev      # 启动开发服务器"
    echo "  $0 build    # 构建生产版本"
    echo "  $0 preview  # 预览生产版本"
}

# 主函数
main() {
    check_node
    check_project
    
    case "${1:-dev}" in
        "dev"|"d")
            install_deps
            start_dev
            ;;
        "build"|"b")
            install_deps
            build_prod
            ;;
        "preview"|"p")
            if [ ! -d "$FRONTEND_DIR/dist" ]; then
                echo -e "${YELLOW}未找到构建文件，先进行构建...${NC}"
                install_deps
                build_prod
            fi
            preview_prod
            ;;
        "install"|"i")
            install_deps
            ;;
        "help"|"h"|"--help"|"-h")
            show_help
            ;;
        *)
            echo -e "${RED}未知选项: $1${NC}"
            show_help
            exit 1
            ;;
    esac
}

# 捕获中断信号
trap 'echo -e "\n${YELLOW}操作已取消${NC}"; exit 1' INT

# 执行主函数
main "$@"
