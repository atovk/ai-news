# AI 新闻聚合系统

## 🎯 项目概述

> **信息爆炸时代的智能新闻助手**  
> 告别信息茧房，让AI为您筛选真正有价值的内容

#### � 现代界面

- **响应式设计**: 完美适配桌面、平板、手机
- **深色模式**: 护眼深色主题，自动跟随系统
- **流畅交互**: 无限滚动、实时加载状态
- **一键操作**: 复制链接、打开原文、分享文章

## 🎯 使用场景

### 👨‍💼 专业人士

- **行业分析师**: 快速获取多源信息，AI生成的中文摘要节省80%阅读时间
- **投资研究**: 及时获取国际财经资讯，不错过重要市场动态
- **技术从业者**: 聚合GitHub、HackerNews等技术资讯，保持技术敏感度

### 📰 内容创作者  

- **新媒体运营**: 发现热点话题和素材，AI标签助力内容分类
- **翻译工作者**: 快速了解外文资讯概要，提高工作效率
- **学术研究**: 跟踪相关领域最新进展，建立个人知识库

### 🏢 团队协作

- **企业内参**: 部署私有实例，定制化新闻源，打造企业专属资讯平台
- **舆情监控**: 关键词追踪，及时发现品牌相关信息
- **竞品分析**: 持续关注竞争对手动态和行业趋势

## 🚀 开始使用

**⚡ 5分钟快速体验**

```bash
# 克隆项目
git clone https://github.com/your-repo/ai-news.git
cd ai-news

# 一键启动 (Docker环境)
./start-fullstack.sh dev

# 访问应用
# 前端: http://localhost:3000
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

> �💡 **首次运行提示**: 系统会自动创建数据库、拉取示例新闻源，并启动AI处理服务。建议先体验"今日精选"功能感受AI处理效果。 解决的痛点

- **信息过载**: 每天海量新闻，无法高效筛选有价值内容
- **语言障碍**: 优质外文资讯无法及时获取和理解  
- **内容质量**: 标题党、重复内容、低质信息泛滥
- **时间成本**: 在多个新闻源间跳转，效率低下

### ⚡ 核心价值

**🧠 AI驱动的内容理解**  
集成Ollama本地大模型，自动生成中文摘要、提取关键标签，让您3秒读懂一篇文章的核心要点

**🌍 多源聚合 + 智能去重**  
聚合RSS、API等多种新闻源，AI智能去重和质量评估，确保每条推送都有价值

**🎯 个性化精选推荐**  
基于内容质量和时效性的智能排序，"今日精选"功能让您不错过重要资讯

**📱 现代化交互体验**  
Vue3+TypeScript构建的响应式界面，支持深色模式，桌面/移动端完美适配

## 🏗️ 技术架构

### � 前端技术栈

- **框架**: Vue.js 3 + TypeScript + Element Plus
- **状态管理**: Pinia + Vue Router  
- **构建工具**: Vite (秒级热重载)
- **容器化**: Docker + Nginx

### ⚙️ 后端技术栈  

- **API框架**: FastAPI (高性能异步框架)
- **数据库**: SQLite + FTS全文搜索
- **AI模型**: Ollama本地部署 (支持Qwen/LLaMA)
- **任务调度**: APScheduler定时抓取
- **项目管理**: Poetry依赖管理

### 🚀 一键部署

```bash
# 开发环境 - 后端Docker + 前端热重载
./start-fullstack.sh dev

# 生产环境 - 前后端容器化 + Nginx代理  
./start-fullstack.sh prod
```

## ✨ 功能亮点

## ✨ 功能亮点

### 🧠 AI智能处理

- **多语言理解**: 自动识别文章语言，生成中文标题和摘要
- **内容质量评估**: AI筛选高质量内容，过滤垃圾信息
- **智能标签提取**: 自动提取关键词和主题标签
- **重复内容去重**: 基于内容相似度的智能去重

### � 数据可视化

- **今日精选仪表板**: 文章处理状态、语言分布统计
- **新闻源监控**: 各新闻源抓取状态和成功率
- **趋势分析**: 热门话题和关键词趋势
- **实时统计**: 文章数量、处理进度实时更新

### 🔍 强大搜索

- **全文检索**: 基于SQLite FTS的高性能搜索
- **高级筛选**: 时间范围、分类、新闻源多维度筛选
- **搜索建议**: 智能补全和热门搜索推荐
- **结果排序**: 按相关性或时间灵活排序

### � 现代界面

- **响应式设计**: 完美适配桌面、平板、手机
- **深色模式**: 护眼深色主题，自动跟随系统
- **流畅交互**: 无限滚动、实时加载状态
- **一键操作**: 复制链接、打开原文、分享文章

## 📁 项目结构

```text
ai-news/
├── 📁 app/                    # 🐍 Python后端 (FastAPI)
│   ├── api/v1/               # RESTful API路由
│   ├── core/                 # 核心业务逻辑
│   ├── models/               # 数据模型
│   ├── services/             # 业务服务
│   └── utils/                # 工具函数
├── 📁 frontend/              # 🌐 Vue.js前端
│   ├── src/
│   │   ├── components/       # 通用组件
│   │   ├── views/           # 页面组件
│   │   ├── api/             # API接口
│   │   ├── stores/          # 状态管理
│   │   └── utils/           # 工具函数
│   ├── Dockerfile           # 前端容器化
│   └── nginx.conf           # Nginx配置
├── 📁 data/                  # 📊 数据存储
│   ├── database/            # SQLite数据库
│   ├── cache/               # 缓存文件
│   └── logs/                # 日志文件
├── 📁 scripts/               # 🔧 部署脚本
├── 🐳 docker-compose.yml     # 开发环境
├── 🐳 docker-compose.frontend.yml # 生产环境
└── 🚀 start-fullstack.sh     # 一键启动脚本
```

│   │   ├── SearchPage.vue    # 搜索页面
│   │   ├── CategoriesPage.vue # 分类页面
│   │   └── NotFoundPage.vue  # 404页面
│   ├── App.vue               # 根组件
│   └── main.ts               # 应用入口
├── index.html                # HTML模板
├── package.json              # 项目配置
├── tsconfig.json             # TypeScript配置
├── vite.config.ts            # Vite构建配置
├── Dockerfile               # Docker构建配置
├── nginx.conf               # Nginx配置
└── README.md                # 前端说明文档

```

## 🚀 快速开始

### 开发环境

1. **安装依赖**

   ```bash
   cd frontend
   npm install
   ```

2. **启动开发服务器**

   ```bash
   npm run dev
   ```

   访问: <http://localhost:3000>

3. **使用便捷脚本**

   ```bash
   ./frontend/start.sh dev
   ```

### 生产部署

1. **构建生产版本**

   ```bash
   cd frontend
   npm run build
   ```

2. **Docker部署**

   ```bash
   # 构建镜像
   docker build -t ai-news-frontend ./frontend
   
   # 运行容器
   docker run -p 3000:80 ai-news-frontend
   ```

3. **完整部署（前后端一体）**

   ```bash
   # 启动开发环境
   ./start-fullstack.sh dev
   
   # 启动生产环境
   ./start-fullstack.sh prod
   ```

## 🔧 配置说明

### API代理配置

开发环境中，前端会自动将`/api`请求代理到后端服务：

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

### 主题系统

支持自动主题切换和手动切换：

- 自动跟随系统主题
- 手动切换深色/浅色主题
- 主题设置本地存储

### 响应式设计

- 桌面端：完整功能和布局
- 平板端：适配中等屏幕
- 移动端：优化触摸交互，简化界面

## 📊 功能特色

### 1. 智能文章展示

- **双语标题**: 优先显示中文标题，fallback到原文标题
- **智能摘要**: 显示LLM生成的摘要或原文摘要
- **处理状态**: 清晰显示文章的处理状态
- **多语言支持**: 显示原文语言标识

### 2. 高级筛选功能

- **分类筛选**: 按新闻分类筛选
- **新闻源筛选**: 按新闻源筛选
- **状态筛选**: 按处理状态筛选
- **时间筛选**: 按发布时间范围筛选

### 3. 数据可视化

- **统计图表**: 今日文章统计、语言分布
- **进度展示**: 处理进度可视化
- **实时更新**: 数据实时刷新

### 4. 用户体验优化

- **加载状态**: 优雅的加载动画
- **错误处理**: 友好的错误提示
- **快捷操作**: 一键复制链接、打开原文
- **无障碍设计**: 支持键盘导航

## 🎨 界面预览

### 首页

- 现代化的文章卡片设计
- 侧边栏导航和筛选
- 响应式布局适配

### 今日精选

- 渐变色页面头部
- 统计数据卡片展示
- 图表可视化展示
- 精美的文章卡片

### 搜索页面

- 高级搜索功能
- 搜索建议和热门搜索
- 搜索结果高亮显示

## 🔌 API集成

完整对接后端API接口：

```typescript
// 文章相关API
articleApi.getArticles()      // 获取文章列表
articleApi.getArticle(id)     // 获取文章详情
articleApi.searchArticles()   // 搜索文章

// 今日功能API
todayApi.getTodayArticles()   // 获取今日文章
todayApi.getTodayStats()      // 获取今日统计
todayApi.processTodayArticles() // 手动处理

// 其他API
sourceApi.getSources()        // 获取新闻源
categoryApi.getCategories()   // 获取分类
systemApi.getStats()          // 获取系统统计
```

## 🌐 部署选项

### 1. 开发部署

- 前端开发服务器 + 后端Docker容器
- 支持热重载和实时调试
- API代理自动配置

### 2. 生产部署

- 前后端都使用Docker容器
- Nginx反向代理
- 静态资源优化

### 3. 分离部署

- 前端部署到CDN或静态托管
- 后端独立部署
- 跨域配置支持

## 📝 使用说明

### 启动完整系统

```bash
# 开发环境（推荐）
./start-fullstack.sh dev

# 生产环境
./start-fullstack.sh prod

# 查看服务状态
./start-fullstack.sh status

# 查看日志
./start-fullstack.sh logs

# 停止服务
./start-fullstack.sh stop
```

### 仅启动前端

```bash
# 进入前端目录
cd frontend

# 开发模式
./start.sh dev

# 构建生产版本
./start.sh build

# 预览生产版本
./start.sh preview
```

## 🛡️ 安全特性

- XSS防护
- CSRF防护
- 内容安全策略
- 安全HTTP头设置
- 输入验证和清理

## ⚡ 性能优化

- 代码分割和懒加载
- 图片懒加载和优化
- HTTP缓存策略
- Gzip压缩
- 资源预加载

## 🔄 后续扩展

已预留的扩展接口：

- 用户系统集成
- 评论功能
- 收藏功能
- 推荐算法
- 多语言国际化
- PWA支持

## 📞 技术支持

前端技术栈：

- Vue.js 3 + TypeScript
- Element Plus UI框架
- Pinia状态管理
- Vue Router路由
- Vite构建工具
- Axios HTTP客户端

这个前端系统完全独立于后端，通过标准的REST API进行通信，可以独立开发、测试和部署。界面现代化、功能完整、易于维护和扩展。
