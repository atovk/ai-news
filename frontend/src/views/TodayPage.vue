<template>
  <div class="today-page">
    <!-- 页面标题和统计 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">
            <el-icon><Calendar /></el-icon>
            今日精选
          </h1>
          <p class="page-subtitle">
            {{ formatDate(new Date(), 'YYYY年MM月DD日') }} - 精心筛选的优质内容
          </p>
        </div>
        <div class="header-actions">
          <el-button
            type="primary"
            :icon="Refresh"
            @click="handleManualProcess"
            :loading="processLoading"
          >
            手动处理
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="stats-grid" v-if="todayStats">
      <el-card class="stat-card">
        <el-statistic
          title="总文章数"
          :value="todayStats.total_articles"
          suffix="篇"
        >
          <template #title>
            <div class="stat-title">
              <el-icon><Document /></el-icon>
              总文章数
            </div>
          </template>
        </el-statistic>
      </el-card>

      <el-card class="stat-card">
        <el-statistic
          title="已处理"
          :value="todayStats.processed_articles"
          suffix="篇"
        >
          <template #title>
            <div class="stat-title">
              <el-icon><Check /></el-icon>
              已处理
            </div>
          </template>
        </el-statistic>
      </el-card>

      <el-card class="stat-card">
        <el-statistic
          title="待处理"
          :value="todayStats.pending_articles"
          suffix="篇"
        >
          <template #title>
            <div class="stat-title">
              <el-icon><Clock /></el-icon>
              待处理
            </div>
          </template>
        </el-statistic>
      </el-card>

      <el-card class="stat-card">
        <el-statistic
          title="处理失败"
          :value="todayStats.failed_articles"
          suffix="篇"
        >
          <template #title>
            <div class="stat-title">
              <el-icon><Close /></el-icon>
              处理失败
            </div>
          </template>
        </el-statistic>
      </el-card>
    </div>

    <!-- 语言统计 -->
    <div class="charts-section" v-if="todayStats">
      <el-row :gutter="24">
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>语言分布</span>
              </div>
            </template>
            <div class="language-stats">
              <div
                v-for="item in todayStats.language_stats"
                :key="item.language"
                class="language-item"
              >
                <span class="language-name">
                  {{ getLanguageName(item.language) }}
                </span>
                <el-progress
                  :percentage="getLanguagePercentage(item.count)"
                  :stroke-width="8"
                  :show-text="false"
                />
                <span class="language-count">{{ item.count }}</span>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <el-icon><DataAnalysis /></el-icon>
                <span>新闻源统计</span>
              </div>
            </template>
            <div class="source-stats">
              <div
                v-for="item in todayStats.sources_stats.slice(0, 10)"
                :key="item.source_name"
                class="source-item"
              >
                <span class="source-name">{{ item.source_name }}</span>
                <div class="source-progress">
                  <el-progress
                    :percentage="getSourcePercentage(item.processed, item.total)"
                    :stroke-width="6"
                    :show-text="false"
                    :color="getProgressColor(item.processed, item.total)"
                  />
                  <span class="source-count">{{ item.processed }}/{{ item.total }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选器 -->
    <div class="filters-section">
      <el-card>
        <div class="filters-content">
          <el-select
            v-model="filters.source"
            placeholder="选择新闻源"
            clearable
            @change="handleFilterChange"
          >
            <el-option
              v-for="source in uniqueSources"
              :key="source"
              :label="source"
              :value="source"
            />
          </el-select>

          <el-select
            v-model="filters.language"
            placeholder="选择语言"
            clearable
            @change="handleFilterChange"
          >
            <el-option
              v-for="lang in uniqueLanguages"
              :key="lang"
              :label="getLanguageName(lang)"
              :value="lang"
            />
          </el-select>

          <el-button @click="resetFilters">重置筛选</el-button>
        </div>
      </el-card>
    </div>

    <!-- 今日文章列表 -->
    <div class="articles-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <el-icon><List /></el-icon>
            <span>今日文章 ({{ pagination.total }})</span>
          </div>
        </template>

        <div v-loading="loading" class="articles-container">
          <template v-if="articles.length > 0">
            <div
              v-for="article in articles"
              :key="article.id"
              class="today-article-card"
            >
              <div class="article-header">
                <div class="article-meta">
                  <el-tag size="small" type="primary" effect="plain">
                    {{ article.source_name }}
                  </el-tag>
                  <el-tag
                    size="small"
                    type="warning"
                    effect="plain"
                    v-if="article.original_language"
                  >
                    {{ getLanguageName(article.original_language) }}
                  </el-tag>
                  <span class="article-time">
                    {{ formatRelativeTime(article.published_at) }}
                  </span>
                </div>
                <div class="article-actions">
                  <el-button
                    type="text"
                    size="small"
                    @click="copyLink(article.url)"
                    :icon="CopyDocument"
                  >
                    复制
                  </el-button>
                  <el-button
                    type="text"
                    size="small"
                    @click="openOriginal(article.url)"
                    :icon="Link"
                  >
                    原文
                  </el-button>
                </div>
              </div>

              <div class="article-content">
                <h3 class="article-title">{{ article.chinese_title }}</h3>
                <div class="article-summary">{{ article.llm_summary }}</div>
                
                <div class="article-tags" v-if="article.tags && article.tags.length > 0">
                  <el-tag
                    v-for="tag in article.tags.slice(0, 8)"
                    :key="tag"
                    size="small"
                    type="info"
                    effect="plain"
                  >
                    {{ tag }}
                  </el-tag>
                </div>
              </div>

              <div class="article-footer" v-if="article.author">
                <div class="article-author">
                  <el-icon><User /></el-icon>
                  <span>{{ article.author }}</span>
                </div>
              </div>
            </div>

            <!-- 分页 -->
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="pagination.page"
                v-model:page-size="pagination.size"
                :page-sizes="[10, 20, 50]"
                :total="pagination.total"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
              />
            </div>
          </template>

          <!-- 空状态 -->
          <div class="empty-state" v-else-if="!loading">
            <div class="empty-state-icon">
              <el-icon><Document /></el-icon>
            </div>
            <div class="empty-state-text">今日暂无已处理的文章</div>
            <el-button
              type="primary"
              @click="handleManualProcess"
              :loading="processLoading"
            >
              手动处理文章
            </el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Calendar,
  Refresh,
  Document,
  Check,
  Clock,
  Close,
  TrendCharts,
  DataAnalysis,
  List,
  CopyDocument,
  Link,
  User,
} from '@element-plus/icons-vue'
import { todayApi } from '@/api'
import {
  formatDate,
  formatRelativeTime,
  getLanguageName,
  copyToClipboard,
} from '@/utils'
import type { TodayArticle, TodayStats } from '@/types'

// 响应式状态
const loading = ref(false)
const processLoading = ref(false)
const articles = ref<TodayArticle[]>([])
const todayStats = ref<TodayStats | null>(null)
const pagination = ref({
  page: 1,
  size: 20,
  total: 0,
})
const filters = ref({
  source: '',
  language: '',
})

// 计算属性
const uniqueSources = computed(() => {
  const sources = new Set(articles.value.map(article => article.source_name))
  return Array.from(sources)
})

const uniqueLanguages = computed(() => {
  const languages = new Set(
    articles.value
      .map(article => article.original_language)
      .filter(Boolean)
  )
  return Array.from(languages)
})

// 生命周期
onMounted(async () => {
  await loadInitialData()
})

// 方法
const loadInitialData = async () => {
  try {
    await Promise.all([
      loadTodayStats(),
      loadTodayArticles(),
    ])
  } catch (error) {
    console.error('Failed to load initial data:', error)
    ElMessage.error('加载数据失败')
  }
}

const loadTodayStats = async () => {
  try {
    todayStats.value = await todayApi.getTodayStats()
  } catch (error) {
    console.error('Failed to load today stats:', error)
  }
}

const loadTodayArticles = async () => {
  try {
    loading.value = true
    const response = await todayApi.getTodayArticles({
      page: pagination.value.page,
      size: pagination.value.size,
      source: filters.value.source || undefined,
      language: filters.value.language || undefined,
    })
    
    articles.value = response.articles
    pagination.value = {
      page: response.page,
      size: response.size,
      total: response.total,
    }
  } catch (error) {
    console.error('Failed to load today articles:', error)
    ElMessage.error('加载今日文章失败')
  } finally {
    loading.value = false
  }
}

const handleManualProcess = async () => {
  try {
    processLoading.value = true
    await todayApi.processTodayArticles()
    ElMessage.success('处理任务已启动，请稍后刷新页面查看结果')
    
    // 延迟刷新数据
    setTimeout(() => {
      loadInitialData()
    }, 3000)
  } catch (error) {
    console.error('Failed to process today articles:', error)
    ElMessage.error('启动处理失败')
  } finally {
    processLoading.value = false
  }
}

const handleFilterChange = () => {
  pagination.value.page = 1
  loadTodayArticles()
}

const resetFilters = () => {
  filters.value = {
    source: '',
    language: '',
  }
  handleFilterChange()
}

const handleSizeChange = (size: number) => {
  pagination.value.size = size
  pagination.value.page = 1
  loadTodayArticles()
}

const handleCurrentChange = (page: number) => {
  pagination.value.page = page
  loadTodayArticles()
}

const copyLink = async (url: string) => {
  try {
    await copyToClipboard(url)
    ElMessage.success('链接已复制')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const openOriginal = (url: string) => {
  window.open(url, '_blank')
}

const getLanguagePercentage = (count: number) => {
  if (!todayStats.value) return 0
  return Math.round((count / todayStats.value.total_articles) * 100)
}

const getSourcePercentage = (processed: number, total: number) => {
  return total > 0 ? Math.round((processed / total) * 100) : 0
}

const getProgressColor = (processed: number, total: number) => {
  const percentage = getSourcePercentage(processed, total)
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 50) return '#e6a23c'
  return '#f56c6c'
}
</script>

<style scoped>
.today-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  background: linear-gradient(135deg, var(--primary-color), #66b1ff);
  color: white;
  border-radius: var(--radius-base);
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: var(--shadow-light);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}

.header-actions {
  flex-shrink: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--bg-color);
  border: 1px solid var(--border-color-lighter);
}

.stat-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--text-color-secondary);
}

.charts-section {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--text-color-primary);
}

.language-stats,
.source-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.language-item,
.source-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.language-name,
.source-name {
  min-width: 80px;
  font-size: 14px;
  color: var(--text-color-regular);
}

.language-count,
.source-count {
  min-width: 40px;
  text-align: right;
  font-size: 12px;
  color: var(--text-color-secondary);
}

.source-progress {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.filters-section {
  margin-bottom: 24px;
}

.filters-content {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.articles-section {
  margin-bottom: 24px;
}

.articles-container {
  min-height: 300px;
}

.today-article-card {
  background: var(--bg-color);
  border: 1px solid var(--border-color-lighter);
  border-radius: var(--radius-base);
  padding: 20px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.today-article-card:hover {
  box-shadow: var(--shadow-light);
  border-color: var(--border-color-light);
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-color-secondary);
}

.article-actions {
  display: flex;
  gap: 4px;
}

.article-content {
  margin-bottom: 16px;
}

.article-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.article-summary {
  font-size: 15px;
  color: var(--text-color-regular);
  line-height: 1.6;
  margin-bottom: 12px;
}

.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.article-footer {
  padding-top: 12px;
  border-top: 1px solid var(--border-color-extra-light);
  font-size: 13px;
  color: var(--text-color-secondary);
}

.article-author {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-color-secondary);
}

.empty-state-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state-text {
  font-size: 16px;
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .page-title {
    font-size: 24px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .filters-content {
    flex-direction: column;
    align-items: stretch;
  }

  .article-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .article-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
