<template>
  <div class="search-box">
    <div class="search-input-wrapper">
      <el-input
        v-model="searchQuery"
        placeholder="搜索新闻..."
        clearable
        size="large"
        @keyup.enter="handleSearch"
        @clear="handleClear"
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
        <template #append>
          <el-button
            type="primary"
            @click="handleSearch"
            :loading="loading"
            :icon="Search"
          >
            搜索
          </el-button>
        </template>
      </el-input>
    </div>

    <!-- 高级搜索选项 -->
    <div class="search-options" v-if="showAdvanced">
      <div class="search-filters">
        <el-select
          v-model="searchFilters.category"
          placeholder="选择分类"
          clearable
          size="small"
        >
          <el-option
            v-for="category in categories"
            :key="category.id"
            :label="category.name"
            :value="category.name"
          />
        </el-select>

        <el-select
          v-model="searchFilters.sort"
          placeholder="排序方式"
          size="small"
        >
          <el-option label="按时间排序" value="published_at" />
          <el-option label="按相关性排序" value="relevance" />
        </el-select>

        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          size="small"
          @change="handleDateChange"
        />
      </div>
    </div>

    <!-- 搜索建议 -->
    <div class="search-suggestions" v-if="showSuggestions && suggestions.length > 0">
      <div
        v-for="suggestion in suggestions"
        :key="suggestion"
        class="suggestion-item"
        @click="selectSuggestion(suggestion)"
      >
        {{ suggestion }}
      </div>
    </div>

    <!-- 热门搜索 -->
    <div class="hot-searches" v-if="showHotSearches && hotSearches.length > 0">
      <div class="hot-searches-title">热门搜索</div>
      <div class="hot-searches-list">
        <el-tag
          v-for="(keyword, index) in hotSearches"
          :key="keyword"
          :type="getHotSearchType(index)"
          effect="plain"
          @click="selectSuggestion(keyword)"
          class="hot-search-tag"
        >
          {{ keyword }}
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { debounce } from '@/utils'
import type { Category } from '@/types'

interface Props {
  loading?: boolean
  showAdvanced?: boolean
  showSuggestions?: boolean
  showHotSearches?: boolean
  categories?: Category[]
  suggestions?: string[]
  hotSearches?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  showAdvanced: false,
  showSuggestions: true,
  showHotSearches: true,
  categories: () => [],
  suggestions: () => [],
  hotSearches: () => ['AI', '科技', '财经', '体育', '娱乐', '国际', '疫情', '股市'],
})

const emit = defineEmits<{
  search: [params: {
    query: string
    category?: string
    sort?: string
    dateFrom?: string
    dateTo?: string
  }]
  'query-change': [query: string]
}>()

// 搜索状态
const searchQuery = ref('')
const searchFilters = ref({
  category: '',
  sort: 'published_at',
})
const dateRange = ref<[Date, Date] | null>(null)

// 监听搜索输入变化
const debouncedQueryChange = debounce((query: string) => {
  emit('query-change', query)
}, 300)

watch(searchQuery, (newQuery) => {
  debouncedQueryChange(newQuery)
})

// 处理搜索
const handleSearch = () => {
  if (!searchQuery.value.trim()) return

  const params = {
    query: searchQuery.value.trim(),
    category: searchFilters.value.category || undefined,
    sort: searchFilters.value.sort,
    dateFrom: dateRange.value?.[0]?.toISOString(),
    dateTo: dateRange.value?.[1]?.toISOString(),
  }

  emit('search', params)
}

// 处理清空
const handleClear = () => {
  searchQuery.value = ''
  emit('query-change', '')
}

// 处理日期变化
const handleDateChange = (dates: [Date, Date] | null) => {
  dateRange.value = dates
}

// 选择搜索建议
const selectSuggestion = (suggestion: string) => {
  searchQuery.value = suggestion
  handleSearch()
}

// 获取热门搜索标签类型
const getHotSearchType = (index: number) => {
  if (index < 3) return 'danger'
  if (index < 6) return 'warning'
  return 'info'
}
</script>

<style scoped>
.search-box {
  width: 100%;
  position: relative;
}

.search-input-wrapper {
  margin-bottom: 12px;
}

.search-input {
  width: 100%;
}

.search-options {
  background: var(--bg-color);
  border: 1px solid var(--border-color-lighter);
  border-radius: var(--radius-base);
  padding: 12px;
  margin-bottom: 12px;
}

.search-filters {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--bg-color);
  border: 1px solid var(--border-color-lighter);
  border-radius: var(--radius-base);
  box-shadow: var(--shadow-light);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.suggestion-item {
  padding: 8px 12px;
  cursor: pointer;
  border-bottom: 1px solid var(--border-color-extra-light);
  transition: background-color 0.3s;
}

.suggestion-item:hover {
  background-color: var(--bg-color-page);
}

.suggestion-item:last-child {
  border-bottom: none;
}

.hot-searches {
  background: var(--bg-color);
  border: 1px solid var(--border-color-lighter);
  border-radius: var(--radius-base);
  padding: 12px;
}

.hot-searches-title {
  font-size: 12px;
  color: var(--text-color-secondary);
  margin-bottom: 8px;
}

.hot-searches-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.hot-search-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.hot-search-tag:hover {
  opacity: 0.8;
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .search-filters {
    flex-direction: column;
    align-items: stretch;
  }

  .search-filters > * {
    width: 100%;
  }
}
</style>
