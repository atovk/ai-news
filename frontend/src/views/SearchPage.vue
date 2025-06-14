<template>
  <div class="search-page">
    <!-- 搜索框 -->
    <div class="search-section">
      <SearchBox
        :loading="loading"
        :show-advanced="true"
        :categories="categories"
        @search="handleSearch"
      />
    </div>

    <!-- 搜索结果 -->
    <div class="results-section" v-if="hasSearched">
      <div class="results-header">
        <h2 class="results-title">
          搜索结果
          <span class="results-count" v-if="searchResults.length > 0">
            ({{ searchResults.length }} 条结果)
          </span>
        </h2>
      </div>

      <ArticleList
        :articles="searchResults"
        :loading="loading"
        :show-filters="false"
        :show-pagination="true"
        :total="pagination.total"
        :page="pagination.page"
        :page-size="pagination.size"
        @article-click="handleArticleClick"
        @page-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>

    <!-- 默认推荐 -->
    <div class="recommendations-section" v-else>
      <div class="recommendations-header">
        <h2 class="section-title">推荐阅读</h2>
      </div>
      
      <ArticleList
        :articles="recommendedArticles"
        :loading="loading"
        :show-filters="false"
        :has-more="hasMore"
        @article-click="handleArticleClick"
        @load-more="loadMoreRecommended"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import SearchBox from '@/components/SearchBox.vue'
import ArticleList from '@/components/ArticleList.vue'
import { articleApi } from '@/api'
import { useCommonStore } from '@/stores/common'
import type { Article, SearchParams } from '@/types'

// Router
const router = useRouter()

// Store
const commonStore = useCommonStore()

// 响应式状态
const loading = ref(false)
const hasSearched = ref(false)
const searchResults = ref<Article[]>([])
const recommendedArticles = ref<Article[]>([])
const hasMore = ref(false)
const pagination = ref({
  page: 1,
  size: 20,
  total: 0,
})
const currentSearchParams = ref<SearchParams | null>(null)

// 计算属性
const categories = computed(() => commonStore.categories)

// 生命周期
onMounted(async () => {
  await loadRecommendedArticles()
})

// 方法
const handleSearch = async (params: SearchParams) => {
  try {
    loading.value = true
    hasSearched.value = true
    currentSearchParams.value = params
    
    const response = await articleApi.searchArticles({
      ...params,
      page: 1,
      size: pagination.value.size,
    })
    
    searchResults.value = response.articles
    pagination.value = {
      page: response.page,
      size: response.size,
      total: response.total,
    }
  } catch (error) {
    console.error('Failed to search articles:', error)
    ElMessage.error('搜索失败')
  } finally {
    loading.value = false
  }
}

const loadRecommendedArticles = async () => {
  try {
    loading.value = true
    const response = await articleApi.getArticles({
      page: 1,
      size: 20,
    })
    
    recommendedArticles.value = response.articles
    hasMore.value = response.page * response.size < response.total
  } catch (error) {
    console.error('Failed to load recommended articles:', error)
  } finally {
    loading.value = false
  }
}

const loadMoreRecommended = async () => {
  try {
    const nextPage = Math.floor(recommendedArticles.value.length / 20) + 1
    const response = await articleApi.getArticles({
      page: nextPage,
      size: 20,
    })
    
    recommendedArticles.value.push(...response.articles)
    hasMore.value = response.page * response.size < response.total
  } catch (error) {
    console.error('Failed to load more articles:', error)
    ElMessage.error('加载更多失败')
  }
}

const handleArticleClick = (article: Article) => {
  router.push({
    name: 'article-detail',
    params: { id: article.id.toString() }
  })
}

const handlePageChange = async (page: number) => {
  if (!currentSearchParams.value) return
  
  try {
    loading.value = true
    const response = await articleApi.searchArticles({
      ...currentSearchParams.value,
      page,
      size: pagination.value.size,
    })
    
    searchResults.value = response.articles
    pagination.value = {
      page: response.page,
      size: response.size,
      total: response.total,
    }
  } catch (error) {
    console.error('Failed to load page:', error)
    ElMessage.error('加载页面失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = async (size: number) => {
  if (!currentSearchParams.value) return
  
  pagination.value.size = size
  await handlePageChange(1)
}
</script>

<style scoped>
.search-page {
  max-width: 1200px;
  margin: 0 auto;
}

.search-section {
  background: var(--bg-color);
  border: 1px solid var(--border-color-lighter);
  border-radius: var(--radius-base);
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: var(--shadow-light);
}

.results-section,
.recommendations-section {
  margin-bottom: 24px;
}

.results-header,
.recommendations-header {
  margin-bottom: 16px;
}

.results-title,
.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0;
}

.results-count {
  font-size: 16px;
  color: var(--text-color-secondary);
  font-weight: normal;
}
</style>
