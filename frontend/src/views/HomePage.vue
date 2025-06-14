<template>
  <div class="home-page">
    <!-- 页面标题和统计 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">最新新闻</h1>
        <div class="page-stats" v-if="stats">
          <el-statistic
            title="总文章数"
            :value="stats.total_articles"
            suffix="篇"
          />
          <el-statistic
            title="已处理"
            :value="stats.processed_articles"
            suffix="篇"
          />
          <el-statistic
            title="今日新增"
            :value="stats.today_articles"
            suffix="篇"
          />
          <el-statistic
            title="活跃源"
            :value="stats.active_sources"
            suffix="个"
          />
        </div>
      </div>
    </div>

    <!-- 文章列表 -->
    <ArticleList
      :articles="articles"
      :loading="loading"
      :has-more="hasMore"
      :sources="sources"
      :categories="categories"
      @article-click="handleArticleClick"
      @filter-change="handleFilterChange"
      @load-more="handleLoadMore"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ArticleList from '@/components/ArticleList.vue'
import { useArticleStore } from '@/stores/article'
import { useCommonStore } from '@/stores/common'
import { systemApi } from '@/api'
import type { Article, Stats } from '@/types'

// 路由
const route = useRoute()
const router = useRouter()

// Store
const articleStore = useArticleStore()
const commonStore = useCommonStore()

// 响应式状态
const stats = ref<Stats | null>(null)

// 计算属性
const articles = computed(() => articleStore.articles)
const loading = computed(() => articleStore.loading)
const hasMore = computed(() => articleStore.hasMore)
const sources = computed(() => commonStore.sources)
const categories = computed(() => commonStore.categories)

// 监听路由查询参数变化
watch(
  () => route.query,
  (newQuery) => {
    const filters = {
      category: newQuery.category as string || '',
      source_id: newQuery.source_id ? parseInt(newQuery.source_id as string) : undefined,
    }
    articleStore.setFilters(filters)
  },
  { immediate: true }
)

// 生命周期
onMounted(async () => {
  await loadInitialData()
})

// 方法
const loadInitialData = async () => {
  try {
    // 加载统计数据
    stats.value = await systemApi.getStats()
    
    // 加载文章数据
    await articleStore.fetchArticles()
  } catch (error) {
    console.error('Failed to load initial data:', error)
    ElMessage.error('加载数据失败')
  }
}

const handleArticleClick = (article: Article) => {
  // 跳转到文章详情页
  router.push({
    name: 'article-detail',
    params: { id: article.id.toString() }
  })
}

const handleFilterChange = (filters: any) => {
  // 更新路由查询参数
  router.push({
    query: {
      ...route.query,
      category: filters.category || undefined,
      source_id: filters.source_id?.toString() || undefined,
    }
  })
}

const handleLoadMore = async () => {
  try {
    await articleStore.loadMore()
  } catch (error) {
    console.error('Failed to load more articles:', error)
    ElMessage.error('加载更多失败')
  }
}
</script>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  background: var(--bg-color);
  border: 1px solid var(--border-color-lighter);
  border-radius: var(--radius-base);
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: var(--shadow-light);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0;
}

.page-stats {
  display: flex;
  gap: 32px;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .page-stats {
    width: 100%;
    justify-content: space-between;
    gap: 16px;
  }
}
</style>
