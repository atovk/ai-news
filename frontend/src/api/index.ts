import { apiClient } from '@/utils/api'
import type {
  Article,
  ArticleListResponse,
  TodayArticle,
  TodayArticleListResponse,
  TodayStats,
  SearchParams,
  NewsSource,
  Category,
  Stats,
} from '@/types'

// 文章 API
export const articleApi = {
  // 获取文章列表
  getArticles: (params: {
    page?: number
    size?: number
    category?: string
    source_id?: number
  }) => apiClient.get<ArticleListResponse>('/articles', params),

  // 获取文章详情
  getArticle: (id: number) => apiClient.get<Article>(`/articles/${id}`),

  // 搜索文章
  searchArticles: (params: SearchParams) => 
    apiClient.get<ArticleListResponse>('/search', params),
}

// 今日文章 API
export const todayApi = {
  // 获取今日文章列表
  getTodayArticles: (params: {
    page?: number
    size?: number
    source?: string
    language?: string
  }) => apiClient.get<TodayArticleListResponse>('/today/articles', params),

  // 获取今日统计信息
  getTodayStats: () => apiClient.get<TodayStats>('/today/stats'),

  // 手动触发今日文章处理
  processTodayArticles: () => apiClient.post('/today/process'),
}

// 新闻源 API
export const sourceApi = {
  // 获取新闻源列表
  getSources: () => apiClient.get<NewsSource[]>('/sources'),

  // 获取新闻源详情
  getSource: (id: number) => apiClient.get<NewsSource>(`/sources/${id}`),
}

// 分类 API
export const categoryApi = {
  // 获取分类列表
  getCategories: () => apiClient.get<Category[]>('/categories'),

  // 获取分类下的文章
  getCategoryArticles: (id: number, params?: {
    page?: number
    size?: number
  }) => apiClient.get<ArticleListResponse>(`/categories/${id}/articles`, params),
}

// 系统 API
export const systemApi = {
  // 健康检查
  healthCheck: () => apiClient.get('/health'),

  // 获取系统统计
  getStats: () => apiClient.get<Stats>('/stats'),
}

// 管理 API
export const adminApi = {
  // 新闻源管理
  sources: {
    list: () => apiClient.get<NewsSource[]>('/admin/sources'),
    create: (data: Partial<NewsSource>) => apiClient.post<NewsSource>('/admin/sources', data),
    update: (id: number, data: Partial<NewsSource>) => 
      apiClient.put<NewsSource>(`/admin/sources/${id}`, data),
    delete: (id: number) => apiClient.delete(`/admin/sources/${id}`),
    fetch: (id: number) => apiClient.post(`/admin/sources/${id}/fetch`),
  },
}
