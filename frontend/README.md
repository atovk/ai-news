# AI 新闻前端

基于 Vue.js 3 + TypeScript + Element Plus 构建的现代化新闻聚合系统前端界面。

## 特性

- 🎨 现代化 UI 设计，支持深色/浅色主题
- 📱 响应式布局，完美适配移动端
- 🔍 智能搜索功能，支持全文检索
- 📊 数据可视化展示
- ⚡ 基于 Vite 的快速开发体验
- 🛡️ TypeScript 类型安全
- 📦 组件化架构，易于维护和扩展

## 技术栈

- **框架**: Vue.js 3 + TypeScript
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **构建工具**: Vite
- **HTTP客户端**: Axios
- **样式**: CSS3 + CSS Variables
- **图标**: Element Plus Icons

## 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── api/               # API 接口定义
│   ├── components/        # 通用组件
│   │   ├── AppLayout.vue  # 应用布局
│   │   ├── ArticleCard.vue # 文章卡片
│   │   ├── ArticleList.vue # 文章列表
│   │   └── SearchBox.vue  # 搜索框
│   ├── router/            # 路由配置
│   ├── stores/            # 状态管理
│   │   ├── article.ts     # 文章状态
│   │   └── common.ts      # 通用状态
│   ├── styles/            # 样式文件
│   ├── types/             # 类型定义
│   ├── utils/             # 工具函数
│   ├── views/             # 页面组件
│   │   ├── HomePage.vue   # 首页
│   │   ├── TodayPage.vue  # 今日精选
│   │   ├── SearchPage.vue # 搜索页面
│   │   └── ...
│   ├── App.vue            # 根组件
│   └── main.ts            # 入口文件
├── index.html             # HTML 模板
├── package.json           # 项目配置
├── tsconfig.json          # TypeScript 配置
└── vite.config.ts         # Vite 配置
```

## 快速开始

### 环境要求

- Node.js >= 16.0.0
- npm >= 8.0.0 或 yarn >= 1.22.0

### 安装依赖

```bash
cd frontend
npm install
# 或
yarn install
```

### 开发模式

```bash
npm run dev
# 或
yarn dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
# 或
yarn build
```

### 预览生产版本

```bash
npm run preview
# 或
yarn preview
```

## 主要功能

### 1. 首页

- 展示最新文章列表
- 支持按分类和新闻源筛选
- 文章卡片展示，包含标题、摘要、标签等信息
- 无限滚动加载更多文章

### 2. 今日精选

- 展示当天经过 LLM 处理的精选文章
- 统计数据可视化展示
- 支持按语言和新闻源筛选
- 手动触发文章处理功能

### 3. 搜索功能

- 全文搜索支持
- 高级搜索选项（分类、时间范围、排序方式）
- 搜索建议和热门搜索
- 搜索结果分页展示

### 4. 分类浏览

- 按分类浏览文章
- 分类卡片展示
- 分类文章列表

### 5. 响应式设计

- 桌面端、平板端、移动端完美适配
- 侧边栏折叠功能
- 触摸友好的交互设计

## 配置说明

### API 代理配置

前端开发服务器配置了 API 代理，将 `/api` 请求转发到后端服务：

```typescript
// vite.config.ts
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

### 环境变量

可以创建 `.env.local` 文件配置环境变量：

```bash
# API 基础URL（如果需要覆盖默认代理配置）
VITE_API_BASE_URL=http://localhost:8000/api/v1

# 应用标题
VITE_APP_TITLE=AI 新闻系统
```

## 主题系统

支持浅色和深色主题，主题切换通过 CSS 变量实现：

```css
:root {
  --primary-color: #409eff;
  --bg-color: #ffffff;
  --text-color-primary: #303133;
  /* ... 更多变量 */
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg-color: #1a1a1a;
    --text-color-primary: #e5eaf3;
    /* ... 深色主题变量 */
  }
}
```

## 开发指南

### 添加新页面

1. 在 `src/views/` 创建页面组件
2. 在 `src/router/index.ts` 添加路由配置
3. 在导航菜单中添加链接

### 添加新组件

1. 在 `src/components/` 创建组件文件
2. 使用 TypeScript 定义 Props 和 Emits
3. 添加适当的样式和响应式支持

### API 接口

所有 API 接口定义在 `src/api/index.ts` 中，按功能模块分组：

```typescript
// 文章相关 API
export const articleApi = {
  getArticles: (params) => apiClient.get('/articles', params),
  getArticle: (id) => apiClient.get(`/articles/${id}`),
  // ...
}
```

### 状态管理

使用 Pinia 进行状态管理，每个功能模块对应一个 store：

```typescript
// stores/article.ts
export const useArticleStore = defineStore('article', () => {
  const articles = ref([])
  const loading = ref(false)
  
  const fetchArticles = async () => {
    // ...
  }
  
  return { articles, loading, fetchArticles }
})
```

## 部署

### Docker 部署

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 静态托管

构建后的 `dist` 目录可以部署到任何静态文件托管服务，如：

- Nginx
- Apache
- Vercel
- Netlify
- GitHub Pages

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

## 许可证

MIT License
