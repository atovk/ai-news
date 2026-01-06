import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { articleApi } from '@/api'
import type { Article, ArticleListResponse } from '@/types'

export const useArticleStore = defineStore('article', () => {
  // 状态
  const articles = ref<Article[]>([])
  const currentArticle = ref<Article | null>(null)
  const loading = ref(false)
  const pagination = ref({
    page: 1,
    size: 20,
    total: 0,
  })
  const filters = ref({
    category: '',
    source_id: undefined as number | undefined,
    tag_id: undefined as number | undefined,
  })

  // 计算属性
  const hasMore = computed(() => {
    return pagination.value.page * pagination.value.size < pagination.value.total
  })

  const totalPages = computed(() => {
    return Math.ceil(pagination.value.total / pagination.value.size)
  })

  // 动作
  const fetchArticles = async (params?: {
    page?: number
    size?: number
    category?: string
    source_id?: number
    tag_id?: number
    append?: boolean
  }) => {
    try {
      loading.value = true
      
      const requestParams = {
        page: params?.page || pagination.value.page,
        size: params?.size || pagination.value.size,
        category: params?.category || filters.value.category,
        source_id: params?.source_id || filters.value.source_id,
        tag_id: params?.tag_id || filters.value.tag_id,
      }

      // @ts-ignore - API signature update pending in types but valid in backend
      const response: ArticleListResponse = await articleApi.getArticles(requestParams)
      
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
      console.error('Failed to fetch articles:', error)
    } finally {
      loading.value = false
    }
  }

  const fetchArticle = async (id: number) => {
    try {
      loading.value = true
      currentArticle.value = await articleApi.getArticle(id)
    } catch (error) {
      console.error('Failed to fetch article:', error)
    } finally {
      loading.value = false
    }
  }

  const loadMore = async () => {
    if (hasMore.value && !loading.value) {
      pagination.value.page += 1
      await fetchArticles({
        page: pagination.value.page,
        append: true,
      })
    }
  }

  const setFilters = (newFilters: Partial<typeof filters.value>) => {
    Object.assign(filters.value, newFilters)
    pagination.value.page = 1
    fetchArticles()
  }

  const resetFilters = () => {
    filters.value = {
      category: '',
      source_id: undefined,
      tag_id: undefined,
    }
    pagination.value.page = 1
    fetchArticles()
  }

  return {
    // 状态
    articles,
    currentArticle,
    loading,
    pagination,
    filters,
    // 计算属性
    hasMore,
    totalPages,
    // 动作
    fetchArticles,
    fetchArticle,
    loadMore,
    setFilters,
    resetFilters,
  }
})
