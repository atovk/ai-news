import { defineStore } from 'pinia'
import { ref } from 'vue'
import { sourceApi, categoryApi } from '@/api'
import type { NewsSource, Category } from '@/types'

export const useCommonStore = defineStore('common', () => {
  // 状态
  const sources = ref<NewsSource[]>([])
  const categories = ref<Category[]>([])
  const loading = ref(false)

  // 动作
  const fetchSources = async () => {
    try {
      loading.value = true
      sources.value = await sourceApi.getSources()
    } catch (error) {
      console.error('Failed to fetch sources:', error)
    } finally {
      loading.value = false
    }
  }

  const fetchCategories = async () => {
    try {
      loading.value = true
      categories.value = await categoryApi.getCategories()
    } catch (error) {
      console.error('Failed to fetch categories:', error)
    } finally {
      loading.value = false
    }
  }

  const initializeData = async () => {
    await Promise.all([
      fetchSources(),
      fetchCategories(),
    ])
  }

  return {
    // 状态
    sources,
    categories,
    loading,
    // 动作
    fetchSources,
    fetchCategories,
    initializeData,
  }
})
