<template>
  <div class="article-card">
    <div class="article-header">
      <div class="article-meta">
        <el-tag
          size="small"
          :type="getProcessingStatusType(article.llm_processing_status)"
        >
          {{ getProcessingStatusText(article.llm_processing_status) }}
        </el-tag>
        <span class="article-source">{{ article.source?.name }}</span>
        <span class="article-time">{{
          formatRelativeTime(article.published_at)
        }}</span>
      </div>
      <div class="article-actions">
        <el-button
          type="text"
          size="small"
          @click="copyLink"
          :icon="CopyDocument"
        >
          复制链接
        </el-button>
        <el-button type="text" size="small" @click="openOriginal" :icon="Link">
          原文
        </el-button>
      </div>
    </div>

    <div class="article-content" @click="handleClick">
      <h3 class="article-title">
        {{ displayTitle }}
      </h3>

      <div class="article-summary" v-if="displaySummary">
        {{ displaySummary }}
      </div>

      <div class="article-tags" v-if="article.tags && article.tags.length > 0">
        <el-tag
          v-for="item in article.tags.slice(0, 5)"
          :key="item.tag.id"
          size="small"
          type="info"
          effect="plain"
        >
          {{ item.tag.name }}
        </el-tag>
      </div>
    </div>

    <div class="article-footer" v-if="article.author">
      <div class="article-author">
        <el-icon><User /></el-icon>
        <span>{{ article.author }}</span>
      </div>
      <div class="article-language" v-if="article.original_language">
        <el-tag size="small" type="warning" effect="plain">
          {{ getLanguageName(article.original_language) }}
        </el-tag>
      </div>

      <div class="article-metrics" v-if="'view_count' in article">
        <span class="metric-item" title="阅读">
          <el-icon><View /></el-icon>
          {{ article.view_count || 0 }}
        </span>
        <!-- Likes and Shares could be added here similarly -->
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { ElMessage } from "element-plus";
import {
  CopyDocument,
  Link,
  User,
  View,
  Star,
  Share,
} from "@element-plus/icons-vue";
import type { Article, TodayArticle } from "@/types";
import {
  formatRelativeTime,
  getLanguageName,
  getProcessingStatusText,
  getProcessingStatusType,
  copyToClipboard,
  truncateText,
} from "@/utils";

interface Props {
  article: Article | TodayArticle;
  clickable?: boolean;
  showSummary?: boolean;
  maxTitleLength?: number;
  maxSummaryLength?: number;
}

const props = withDefaults(defineProps<Props>(), {
  clickable: true,
  showSummary: true,
  maxTitleLength: 100,
  maxSummaryLength: 200,
});

const emit = defineEmits<{
  click: [article: Article | TodayArticle];
}>();

// 计算显示的标题
const displayTitle = computed(() => {
  if ("chinese_title" in props.article && props.article.chinese_title) {
    return truncateText(props.article.chinese_title, props.maxTitleLength);
  }
  const title =
    "original_title" in props.article
      ? props.article.original_title
      : props.article.title;
  return truncateText(title, props.maxTitleLength);
});

// 计算显示的摘要
const displaySummary = computed(() => {
  if (!props.showSummary) return "";

  let summary = "";
  if ("llm_summary" in props.article && props.article.llm_summary) {
    summary = props.article.llm_summary;
  } else if (props.article.summary) {
    summary = props.article.summary;
  }

  return summary ? truncateText(summary, props.maxSummaryLength) : "";
});

// 处理点击事件
const handleClick = () => {
  if (props.clickable) {
    emit("click", props.article);
  }
};

// 复制链接
const copyLink = async () => {
  try {
    await copyToClipboard(props.article.url);
    ElMessage.success("链接已复制到剪贴板");
  } catch (error) {
    ElMessage.error("复制失败");
  }
};

// 打开原文
const openOriginal = () => {
  window.open(props.article.url, "_blank");
};
</script>

<style scoped>
.article-card {
  background: var(--bg-color);
  border: 1px solid var(--border-color-lighter);
  border-radius: var(--radius-base);
  padding: 16px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.article-card:hover {
  box-shadow: var(--shadow-light);
  border-color: var(--border-color-light);
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
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
  cursor: pointer;
}

.article-content:hover .article-title {
  color: var(--primary-color);
}

.article-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 8px 0;
  line-height: 1.4;
  transition: color 0.3s ease;
}

.article-summary {
  font-size: 14px;
  color: var(--text-color-regular);
  line-height: 1.5;
  margin-bottom: 12px;
}

.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
}

.article-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
  border-top: 1px solid var(--border-color-extra-light);
  font-size: 12px;
  color: var(--text-color-secondary);
}

.article-author {
  display: flex;
  align-items: center;
  gap: 4px;
}

@media (max-width: 768px) {
  .article-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .article-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .article-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    gap: 8px;
  }
}

.article-metrics {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-color-secondary);
  font-size: 12px;
}
</style>
