<template>
  <div class="tag-detail-page">
    <div class="page-header" v-loading="loadingTag">
      <div class="header-content" v-if="tag">
        <div class="tag-meta">
          <h1 class="tag-name">
            <span class="prefix">#</span>
            {{ tag.name }}
          </h1>
          <el-button
            type="primary"
            :icon="isFollowed ? Check : Plus"
            circle
            @click="toggleFollow"
            :loading="loadingFollow"
            :class="{ 'is-followed': isFollowed }"
          />
        </div>
        <p class="tag-stats">{{ tag.article_count || 0 }} 篇文章</p>
      </div>
      <div class="error-state" v-else-if="!loadingTag">
        <el-empty description="标签不存在" />
      </div>
    </div>

    <div class="page-content">
      <ArticleList
        :articles="articleStore.articles"
        :loading="articleStore.loading"
        :has-more="articleStore.hasMore"
        @load-more="articleStore.loadMore"
        @click="goToArticle"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Plus, Check } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import ArticleList from "@/components/ArticleList.vue";
import { useArticleStore } from "@/stores/article";
import { tagApi } from "@/api";
import type { Tag, Article } from "@/types";

const route = useRoute();
const router = useRouter();
const articleStore = useArticleStore();

const tagId = computed(() => parseInt(route.params.id as string));
const tag = ref<Tag | null>(null);
const loadingTag = ref(false);
const loadingFollow = ref(false);
const isFollowed = ref(false); // This should ideally come from backend user-pref

onMounted(async () => {
  if (isNaN(tagId.value)) {
    router.push("/404");
    return;
  }

  await fetchTagDetails();

  // Initialize filter
  articleStore.resetFilters();
  articleStore.setFilters({ tag_id: tagId.value });
});

// Watch route change to reload
watch(
  () => route.params.id,
  async (newId) => {
    if (newId) {
      articleStore.resetFilters();
      articleStore.setFilters({ tag_id: parseInt(newId as string) });
      await fetchTagDetails();
    }
  }
);

const fetchTagDetails = async () => {
  loadingTag.value = true;
  try {
    const res = await tagApi.get(tagId.value);
    // @ts-ignore
    tag.value = res; // Axios response wrapper handling might depend on ApiClient
  } catch (error) {
    console.error("Failed to fetch tag:", error);
    ElMessage.error("获取标签信息失败");
  } finally {
    loadingTag.value = false;
  }
};

const toggleFollow = async () => {
  if (!tag.value) return;

  loadingFollow.value = true;
  try {
    if (isFollowed.value) {
      await tagApi.unfollow(tag.value.id);
      isFollowed.value = false;
      ElMessage.success("已取消关注");
    } else {
      await tagApi.follow(tag.value.id);
      isFollowed.value = true;
      ElMessage.success("关注成功");
    }
  } catch (error) {
    ElMessage.error("操作失败");
  } finally {
    loadingFollow.value = false;
  }
};

const goToArticle = (article: Article) => {
  router.push(`/article/${article.id}`);
};
</script>

<style scoped>
.tag-detail-page {
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  background: var(--bg-color);
  padding: 32px 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  border: 1px solid var(--border-color-lighter);
  text-align: center;
}

.tag-meta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 8px;
}

.tag-name {
  font-size: 32px;
  font-weight: 700;
  margin: 0;
  color: var(--text-color-primary);
  display: flex;
  align-items: center;
}

.prefix {
  color: var(--primary-color);
  margin-right: 4px;
  font-weight: 400;
}

.tag-stats {
  color: var(--text-color-secondary);
  font-size: 14px;
  margin: 0;
}

.is-followed {
  background-color: var(--success-color);
  border-color: var(--success-color);
}
</style>
