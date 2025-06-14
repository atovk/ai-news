# 多阶段构建 Dockerfile
FROM node:18-alpine as builder

# 设置工作目录
WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY . .

# 设置环境变量
ENV NODE_ENV=production

# 构建应用
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 安装 curl 和 tzdata
RUN apk add --no-cache tzdata curl

# 设置时区
ENV TZ=Asia/Shanghai

# 复制构建结果
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# 复制等待脚本
COPY wait-for-backend.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/wait-for-backend.sh

# 创建日志目录
RUN mkdir -p /var/log/nginx

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# 使用等待脚本启动
ENTRYPOINT ["/usr/local/bin/wait-for-backend.sh"]
CMD ["nginx", "-g", "daemon off;"]
