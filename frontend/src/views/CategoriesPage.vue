<template>
  <div class="categories-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">新闻分类</h1>
      <p class="page-description">按分类浏览新闻内容</p>
    </div>

    <!-- 分类网格 -->
    <div class="categories-grid" v-loading="loading">
      <div
        v-for="category in categories"
        :key="category.id"
        class="category-card"
        @click="selectCategory(category)"
      >
        <div class="category-info">
          <h3 class="category-name">{{ category.name }}</h3>
          <p class="category-description" v-if="category.description">
            {{ category.description }}
          </p>
        </div>
        <div class="category-meta">
          <el-tag :type="category.is_active ? 'success' : 'info'">
            {{ category.is_active ? '活跃' : '停用' }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 选中分类的文章 -->
    <div class="category-articles" v-if="selectedCategory">
      <div class="section-header">
        <h2 class="section-title">
          {{ selectedCategory.name }} - 相关文章
        </h2>
        <el-button @click="clearSelection" type="text">
          清除选择
        </el-button>
      </div>

      <ArticleList
        :articles="categoryArticles"
        :loading="articlesLoading"
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ArticleList from '@/components/ArticleList.vue'
import { categoryApi } from '@/api'
import { useCommonStore } from '@/stores/common'
import type { Category, Article } from '@/types'

// Router
const router = useRouter()

// Store
const commonStore = useCommonStore()

// 响应式状态
const loading = ref(false)
const articlesLoading = ref(false)
const selectedCategory = ref<Category | null>(null)
const categoryArticles = ref<Article[]>([])
const pagination = ref({
  page: 1,
  size: 20,
  total: 0,
})

// 计算属性
const categories = computed(() => commonStore.categories)

// 生命周期
onMounted(async () => {
  if (categories.value.length === 0) {
    await commonStore.fetchCategories()
  }
})

// 方法
const selectCategory = async (category: Category) => {
  selectedCategory.value = category
  await loadCategoryArticles(1)
}

const clearSelection = () => {
  selectedCategory.value = null
  categoryArticles.value = []
}

const loadCategoryArticles = async (page: number) => {
  if (!selectedCategory.value) return

  try {
    articlesLoading.value = true
    const response = await categoryApi.getCategoryArticles(
      selectedCategory.value.id,
      {
        page,
        size: pagination.value.size,
      }
    )

    categoryArticles.value = response.articles
    pagination.value = {
      page: response.page,
      size: response.size,
      total: response.total,
    }
  } catch (error) {
    console.error('Failed to load category articles:', error)
    ElMessage.error('加载分类文章失败')
  } finally {
    articlesLoading.value = false
  }
}

const handleArticleClick = (article: Article) => {
  router.push({
    name: 'article-detail',
    params: { id: article.id.toString() }
  })
}

const handlePageChange = (page: number) => {
  pagination.value.page = page
  loadCategoryArticles(page)
}

const handleSizeChange = (size: number) => {
  pagination.value.size = size
  loadCategoryArticles(1)
}
</script>

<style scoped>
.categories-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 16px;
  color: var(--text-color-secondary);
  margin: 0;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.category-card {
  background: var(--bg-color);
  border: 1px solid var(--border-color-lighter);
  border-radius: var(--radius-base);
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.category-card:hover {
  box-shadow: var(--shadow-light);
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.category-info {
  flex: 1;
}

.category-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 8px 0;
}

.category-description {
  font-size: 14px;
  color: var(--text-color-secondary);
  margin: 0;
  line-height: 1.5;
}

.category-meta {
  flex-shrink: 0;
  margin-left: 16px;
}

.category-articles {
  margin-top: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0;
}

@media (max-width: 768px) {
  .categories-grid {
    grid-template-columns: 1fr;
  }

  .category-card {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .category-meta {
    margin-left: 0;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
