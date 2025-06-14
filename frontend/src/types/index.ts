// 新闻文章类型
export interface Article {
  id: number
  title: string
  summary?: string
  content?: string
  url: string
  author?: string
  published_at: string
  fetched_at: string
  is_processed: boolean
  category?: string
  tags: string[]
  chinese_title?: string
  llm_summary?: string
  original_language?: string
  llm_processed_at?: string
  llm_processing_status: 'pending' | 'processing' | 'completed' | 'failed'
  source: NewsSource
}

// 今日文章视图类型
export interface TodayArticle {
  id: number
  original_title: string
  chinese_title: string
  url: string
  author?: string
  source_name: string
  published_at: string
  llm_summary: string
  original_language: string
  tags: string[]
}

// 新闻源类型
export interface NewsSource {
  id: number
  name: string
  url: string
  source_type: string
  is_active: boolean
  fetch_interval: number
  last_fetch_time?: string
  created_at: string
  updated_at: string
}

// 分类类型
export interface Category {
  id: number
  name: string
  description?: string
  parent_id?: number
  is_active: boolean
}

// 分页响应类型
export interface PaginatedResponse<T> {
  total: number
  page: number
  size: number
  data: T[]
}

// 文章列表响应
export interface ArticleListResponse extends PaginatedResponse<Article> {
  articles: Article[]
}

// 今日文章列表响应
export interface TodayArticleListResponse extends PaginatedResponse<TodayArticle> {
  articles: TodayArticle[]
}

// 搜索请求参数
export interface SearchParams {
  q: string
  category?: string
  page?: number
  size?: number
  sort?: 'published_at' | 'relevance'
}

// 统计信息
export interface Stats {
  total_articles: number
  processed_articles: number
  today_articles: number
  active_sources: number
}

// 今日统计信息
export interface TodayStats {
  total_articles: number
  processed_articles: number
  pending_articles: number
  failed_articles: number
  processing_articles: number
  sources_stats: Array<{
    source_name: string
    total: number
    processed: number
  }>
  language_stats: Array<{
    language: string
    count: number
  }>
}

// API 响应基础类型
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// 错误响应类型
export interface ErrorResponse {
  error: string
  message: string
  details?: Record<string, any>
}
