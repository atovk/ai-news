<template>
  <div class="article-detail-page">
    <div v-loading="loading" class="detail-container">
      <template v-if="article">
        <!-- 返回按钮 -->
        <div class="back-button">
          <el-button 
            :icon="ArrowLeft" 
            @click="goBack"
            type="text"
            size="large"
          >
            返回
          </el-button>
        </div>

        <!-- 文章头部 -->
        <div class="article-header">
          <div class="article-meta">
            <el-tag 
              size="small" 
              :type="getProcessingStatusType(article.llm_processing_status)"
            >
              {{ getProcessingStatusText(article.llm_processing_status) }}
            </el-tag>
            <span class="article-source">{{ article.source?.name }}</span>
            <span class="article-time">{{ formatDate(article.published_at) }}</span>
            <span class="article-language" v-if="article.original_language">
              {{ getLanguageName(article.original_language) }}
            </span>
          </div>

          <div class="article-actions">
            <el-button
              :icon="CopyDocument"
              @click="copyLink"
              type="text"
            >
              复制链接
            </el-button>
            <el-button
              :icon="Link"
              @click="openOriginal"
              type="text"
            >
              查看原文
            </el-button>
          </div>
        </div>

        <!-- 文章标题 -->
        <div class="article-title-section">
          <h1 class="article-title">
            {{ displayTitle }}
          </h1>
          <div class="title-info" v-if="article.chinese_title && article.title !== article.chinese_title">
            <el-divider content-position="left">原文标题</el-divider>
            <p class="original-title">{{ article.title }}</p>
          </div>
        </div>

        <!-- 文章作者 -->
        <div class="article-author" v-if="article.author">
          <el-icon><User /></el-icon>
          <span>{{ article.author }}</span>
        </div>

        <!-- AI 摘要 -->
        <div class="article-summary" v-if="displaySummary">
          <el-card>
            <template #header>
              <div class="summary-header">
                <el-icon><ChatRound /></el-icon>
                <span>AI 智能摘要</span>
              </div>
            </template>
            <div class="summary-content">
              {{ displaySummary }}
            </div>
          </el-card>
        </div>

        <!-- 文章内容 -->
        <div class="article-content" v-if="article.content">
          <el-card>
            <template #header>
              <div class="content-header">
                <el-icon><Document /></el-icon>
                <span>文章内容</span>
              </div>
            </template>
            <div class="content-body" v-html="formattedContent"></div>
          </el-card>
        </div>

        <!-- 原文摘要 -->
        <div class="original-summary" v-else-if="article.summary">
          <el-card>
            <template #header>
              <div class="content-header">
                <el-icon><Document /></el-icon>
                <span>原文摘要</span>
              </div>
            </template>
            <div class="summary-content">
              {{ article.summary }}
            </div>
          </el-card>
        </div>

        <!-- 标签 -->
        <div class="article-tags" v-if="article.tags && article.tags.length > 0">
          <el-card>
            <template #header>
              <div class="tags-header">
                <el-icon><Discount /></el-icon>
                <span>相关标签</span>
              </div>
            </template>
            <div class="tags-content">
              <el-tag
                v-for="tag in article.tags"
                :key="tag"
                type="info"
                effect="plain"
                size="default"
              >
                {{ tag }}
              </el-tag>
            </div>
          </el-card>
        </div>

        <!-- 文章信息 -->
        <div class="article-info">
          <el-card>
            <template #header>
              <div class="info-header">
                <el-icon><InfoFilled /></el-icon>
                <span>文章信息</span>
              </div>
            </template>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="发布时间">
                {{ formatDate(article.published_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="获取时间">
                {{ formatDate(article.fetched_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="处理状态">
                <el-tag :type="getProcessingStatusType(article.llm_processing_status)">
                  {{ getProcessingStatusText(article.llm_processing_status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="处理时间" v-if="article.llm_processed_at">
                {{ formatDate(article.llm_processed_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="新闻源">
                {{ article.source?.name }}
              </el-descriptions-item>
              <el-descriptions-item label="分类" v-if="article.category">
                {{ article.category }}
              </el-descriptions-item>
              <el-descriptions-item label="原文语言" v-if="article.original_language">
                {{ getLanguageName(article.original_language) }}
              </el-descriptions-item>
              <el-descriptions-item label="是否已处理">
                <el-tag :type="article.is_processed ? 'success' : 'info'">
                  {{ article.is_processed ? '是' : '否' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </div>
      </template>

      <!-- 加载失败状态 -->
      <div class="error-state" v-else-if="!loading">
        <el-empty
          image="/images/error.svg"
          description="文章加载失败"
        >
          <el-button type="primary" @click="loadArticle">重试</el-button>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  CopyDocument,
  Link,
  User,
  ChatRound,
  Document,
  Discount,
  InfoFilled,
} from '@element-plus/icons-vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
import { useArticleStore } from '@/stores/article'
import {
  formatDate,
  getLanguageName,
  getProcessingStatusText,
  getProcessingStatusType,
  copyToClipboard,
} from '@/utils'
import type { Article } from '@/types'

// 路由
const route = useRoute()
const router = useRouter()

// Store
const articleStore = useArticleStore()

// Markdown 解析器
const md = new MarkdownIt({
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch (__) {}
    }
    return ''
  }
})

// 响应式状态
const loading = ref(false)
const articleId = computed(() => {
  return parseInt(route.params.id as string)
})

// 计算属性
const article = computed(() => articleStore.currentArticle)

const displayTitle = computed(() => {
  if (!article.value) return ''
  return article.value.chinese_title || article.value.title
})

const displaySummary = computed(() => {
  if (!article.value) return ''
  return article.value.llm_summary || article.value.summary
})

const formattedContent = computed(() => {
  if (!article.value?.content) return ''
  return md.render(article.value.content)
})

// 生命周期
onMounted(async () => {
  await loadArticle()
})

// 方法
const loadArticle = async () => {
  if (isNaN(articleId.value)) {
    ElMessage.error('无效的文章ID')
    router.back()
    return
  }

  try {
    loading.value = true
    await articleStore.fetchArticle(articleId.value)
    if (!article.value) {
      ElMessage.error('文章不存在')
      router.back()
    }
  } catch (error) {
    console.error('Failed to load article:', error)
    ElMessage.error('加载文章失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const copyLink = async () => {
  if (!article.value) return
  
  try {
    await copyToClipboard(article.value.url)
    ElMessage.success('链接已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const openOriginal = () => {
  if (!article.value) return
  window.open(article.value.url, '_blank')
}
</script>

<style scoped>
.article-detail-page {
  max-width: 800px;
  margin: 0 auto;
}

.detail-container {
  min-height: 400px;
}

.back-button {
  margin-bottom: 16px;
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color-lighter);
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: var(--text-color-secondary);
  flex-wrap: wrap;
}

.article-actions {
  display: flex;
  gap: 8px;
}

.article-title-section {
  margin-bottom: 24px;
}

.article-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-color-primary);
  line-height: 1.4;
  margin: 0;
}

.original-title {
  color: var(--text-color-regular);
  font-size: 16px;
  margin: 8px 0 0 0;
}

.article-author {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
  color: var(--text-color-regular);
}

.article-summary,
.article-content,
.original-summary,
.article-tags,
.article-info {
  margin-bottom: 24px;
}

.summary-header,
.content-header,
.tags-header,
.info-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.summary-content {
  font-size: 16px;
  line-height: 1.6;
  color: var(--text-color-regular);
}

.content-body {
  font-size: 16px;
  line-height: 1.7;
  color: var(--text-color-primary);
}

.content-body :deep(h1),
.content-body :deep(h2),
.content-body :deep(h3),
.content-body :deep(h4),
.content-body :deep(h5),
.content-body :deep(h6) {
  color: var(--text-color-primary);
  margin: 20px 0 12px 0;
}

.content-body :deep(p) {
  margin: 12px 0;
}

.content-body :deep(blockquote) {
  border-left: 4px solid var(--primary-color);
  padding-left: 16px;
  margin: 16px 0;
  color: var(--text-color-secondary);
}

.content-body :deep(code) {
  background-color: var(--bg-color-page);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}

.content-body :deep(pre) {
  background-color: var(--bg-color-page);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
}

.tags-content {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.error-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

@media (max-width: 768px) {
  .article-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .article-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .article-title {
    font-size: 24px;
  }

  .article-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
