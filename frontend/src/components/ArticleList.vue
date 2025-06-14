<template>
  <div class="article-list">
    <!-- 筛选器 -->
    <div class="article-filters" v-if="showFilters">
      <div class="filter-group">
        <el-select
          v-model="localFilters.category"
          placeholder="选择分类"
          clearable
          @change="handleFilterChange"
        >
          <el-option
            v-for="category in categories"
            :key="category.id"
            :label="category.name"
            :value="category.name"
          />
        </el-select>

        <el-select
          v-model="localFilters.source_id"
          placeholder="选择新闻源"
          clearable
          @change="handleFilterChange"
        >
          <el-option
            v-for="source in sources"
            :key="source.id"
            :label="source.name"
            :value="source.id"
          />
        </el-select>

        <el-button @click="resetFilters" type="default">
          重置筛选
        </el-button>
      </div>
    </div>

    <!-- 文章列表 -->
    <div class="articles-container" v-loading="loading">
      <template v-if="articles.length > 0">
        <ArticleCard
          v-for="article in articles"
          :key="article.id"
          :article="article"
          @click="handleArticleClick"
        />
        
        <!-- 加载更多 -->
        <div class="load-more" v-if="hasMore">
          <el-button
            @click="loadMore"
            :loading="loading"
            type="primary"
            plain
          >
            加载更多
          </el-button>
        </div>
      </template>

      <!-- 空状态 -->
      <div class="empty-state" v-else-if="!loading">
        <div class="empty-state-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="empty-state-text">暂无文章</div>
      </div>
    </div>

    <!-- 分页器 -->
    <div class="pagination-container" v-if="showPagination && totalPages > 1">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Document } from '@element-plus/icons-vue'
import ArticleCard from './ArticleCard.vue'
import type { Article, NewsSource, Category } from '@/types'

interface Props {
  articles: Article[]
  loading?: boolean
  showFilters?: boolean
  showPagination?: boolean
  hasMore?: boolean
  total?: number
  page?: number
  pageSize?: number
  sources?: NewsSource[]
  categories?: Category[]
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  showFilters: true,
  showPagination: false,
  hasMore: false,
  total: 0,
  page: 1,
  pageSize: 20,
  sources: () => [],
  categories: () => [],
})

const emit = defineEmits<{
  'article-click': [article: Article]
  'filter-change': [filters: any]
  'load-more': []
  'page-change': [page: number]
  'size-change': [size: number]
}>()

// 本地筛选状态
const localFilters = ref({
  category: '',
  source_id: undefined as number | undefined,
})

// 分页状态
const currentPage = ref(props.page)
const pageSize = ref(props.pageSize)

// 计算属性
const totalPages = computed(() => {
  return Math.ceil(props.total / pageSize.value)
})

// 监听props变化
watch(
  () => props.page,
  (newPage) => {
    currentPage.value = newPage
  }
)

watch(
  () => props.pageSize,
  (newSize) => {
    pageSize.value = newSize
  }
)

// 处理文章点击
const handleArticleClick = (article: Article) => {
  emit('article-click', article)
}

// 处理筛选变化
const handleFilterChange = () => {
  emit('filter-change', { ...localFilters.value })
}

// 重置筛选
const resetFilters = () => {
  localFilters.value = {
    category: '',
    source_id: undefined,
  }
  handleFilterChange()
}

// 加载更多
const loadMore = () => {
  emit('load-more')
}

// 处理页码变化
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  emit('page-change', page)
}

// 处理页面大小变化
const handleSizeChange = (size: number) => {
  pageSize.value = size
  emit('size-change', size)
}
</script>

<style scoped>
.article-list {
  width: 100%;
}

.article-filters {
  background: var(--bg-color);
  border: 1px solid var(--border-color-lighter);
  border-radius: var(--radius-base);
  padding: 16px;
  margin-bottom: 16px;
}

.filter-group {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.articles-container {
  min-height: 200px;
}

.load-more {
  text-align: center;
  padding: 20px;
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
}

@media (max-width: 768px) {
  .filter-group {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group > * {
    width: 100%;
  }
}
</style>
