import { defineStore } from 'pinia'
import { ref } from 'vue'
import { todayApi } from '@/api'
import type { TodayArticle, TodayArticleListResponse, TodayStats } from '@/types'

export const useTodayStore = defineStore('today', () => {
  // 状态
  const articles = ref<TodayArticle[]>([])
  const stats = ref<TodayStats | null>(null)
  const loading = ref(false)
  const processing = ref(false)
  const pagination = ref({
    page: 1,
    size: 20,
    total: 0,
  })
  const filters = ref({
    source: '',
    language: '',
  })

  // 动作
  const fetchTodayArticles = async (params?: {
    page?: number
    size?: number
    source?: string
    language?: string
    append?: boolean
  }) => {
    try {
      loading.value = true
      
      const requestParams = {
        page: params?.page || pagination.value.page,
        size: params?.size || pagination.value.size,
        source: params?.source || filters.value.source,
        language: params?.language || filters.value.language,
      }

      const response: TodayArticleListResponse = await todayApi.getTodayArticles(requestParams)
      
      if (params?.append) {
        articles.value.push(...response.articles)
      } else {
        articles.value = response.articles
      }
      
      pagination.value = {
        page: response.page,
        size: response.size,
        total: response.total,
      }
    } catch (error) {
      console.error('Failed to fetch today articles:', error)
    } finally {
      loading.value = false
    }
  }

  const fetchTodayStats = async () => {
    try {
      stats.value = await todayApi.getTodayStats()
    } catch (error) {
      console.error('Failed to fetch today stats:', error)
    }
  }

  const processTodayArticles = async () => {
    try {
      processing.value = true
      await todayApi.processTodayArticles()
      // 处理完成后刷新数据
      await Promise.all([
        fetchTodayArticles(),
        fetchTodayStats(),
      ])
    } catch (error) {
      console.error('Failed to process today articles:', error)
    } finally {
      processing.value = false
    }
  }

  const loadMore = async () => {
    if (pagination.value.page * pagination.value.size < pagination.value.total && !loading.value) {
      pagination.value.page += 1
      await fetchTodayArticles({
        page: pagination.value.page,
        append: true,
      })
    }
  }

  const setFilters = (newFilters: Partial<typeof filters.value>) => {
    Object.assign(filters.value, newFilters)
    pagination.value.page = 1
    fetchTodayArticles()
  }

  const resetFilters = () => {
    filters.value = {
      source: '',
      language: '',
    }
    pagination.value.page = 1
    fetchTodayArticles()
  }

  return {
    // 状态
    articles,
    stats,
    loading,
    processing,
    pagination,
    filters,
    // 动作
    fetchTodayArticles,
    fetchTodayStats,
    processTodayArticles,
    loadMore,
    setFilters,
    resetFilters,
  }
})
