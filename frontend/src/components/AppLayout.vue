<template>
  <div class="app-layout">
    <!-- 顶部导航 -->
    <el-header class="app-header">
      <div class="header-content">
        <!-- Logo 和标题 -->
        <div class="header-left">
          <div class="logo" @click="goHome">
            <el-icon size="24"><Reading /></el-icon>
            <span class="logo-text">AI 新闻</span>
          </div>
        </div>

        <!-- 导航菜单 -->
        <div class="header-center">
          <el-menu
            :default-active="activeMenu"
            mode="horizontal"
            @select="handleMenuSelect"
            class="header-menu"
          >
            <el-menu-item index="home">首页</el-menu-item>
            <el-menu-item index="today">今日精选</el-menu-item>
            <el-menu-item index="search">搜索</el-menu-item>
            <el-menu-item index="categories">分类</el-menu-item>
          </el-menu>
        </div>

        <!-- 右侧操作 -->
        <div class="header-right">
          <!-- 主题切换 -->
          <el-tooltip content="切换主题">
            <el-button
              :icon="isDark ? Sunny : Moon"
              circle
              @click="toggleTheme"
            />
          </el-tooltip>

          <!-- 刷新 -->
          <el-tooltip content="刷新">
            <el-button
              :icon="Refresh"
              circle
              @click="handleRefresh"
              :loading="refreshLoading"
            />
          </el-tooltip>

          <!-- 设置 -->
          <el-tooltip content="设置">
            <el-button
              :icon="Setting"
              circle
              @click="showSettings = true"
            />
          </el-tooltip>
        </div>
      </div>
    </el-header>

    <!-- 主要内容区域 -->
    <el-container class="main-container">
      <!-- 侧边栏 -->
      <el-aside :width="sidebarWidth" class="app-sidebar" v-if="showSidebar">
        <div class="sidebar-content">
          <!-- 快速导航 -->
          <div class="sidebar-section">
            <h4 class="sidebar-title">快速导航</h4>
            <el-menu
              :default-active="activeMenu"
              @select="handleMenuSelect"
            >
              <el-menu-item index="home">
                <el-icon><House /></el-icon>
                <span>首页</span>
              </el-menu-item>
              <el-menu-item index="today">
                <el-icon><Calendar /></el-icon>
                <span>今日精选</span>
              </el-menu-item>
              <el-menu-item index="search">
                <el-icon><Search /></el-icon>
                <span>搜索</span>
              </el-menu-item>
            </el-menu>
          </div>

          <!-- 分类导航 -->
          <div class="sidebar-section">
            <h4 class="sidebar-title">分类</h4>
            <div class="category-list">
              <div
                v-for="category in categories"
                :key="category.id"
                class="category-item"
                :class="{ active: selectedCategory === category.name }"
                @click="selectCategory(category.name)"
              >
                {{ category.name }}
              </div>
            </div>
          </div>

          <!-- 新闻源 -->
          <div class="sidebar-section">
            <h4 class="sidebar-title">新闻源</h4>
            <div class="source-list">
              <div
                v-for="source in sources"
                :key="source.id"
                class="source-item"
                :class="{ active: selectedSource === source.id }"
                @click="selectSource(source.id)"
              >
                <span class="source-name">{{ source.name }}</span>
                <el-tag
                  size="small"
                  :type="source.is_active ? 'success' : 'info'"
                  effect="plain"
                >
                  {{ source.is_active ? '活跃' : '停用' }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </el-aside>

      <!-- 主内容 -->
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>

    <!-- 设置弹窗 -->
    <el-dialog
      v-model="showSettings"
      title="设置"
      width="500px"
    >
      <div class="settings-content">
        <el-form label-width="100px">
          <el-form-item label="主题">
            <el-switch
              v-model="isDark"
              @change="toggleTheme"
              active-text="深色"
              inactive-text="浅色"
            />
          </el-form-item>
          <el-form-item label="显示侧边栏">
            <el-switch
              v-model="showSidebar"
              active-text="显示"
              inactive-text="隐藏"
            />
          </el-form-item>
          <el-form-item label="自动刷新">
            <el-switch
              v-model="autoRefresh"
              active-text="开启"
              inactive-text="关闭"
            />
          </el-form-item>
          <el-form-item label="刷新间隔" v-if="autoRefresh">
            <el-select v-model="refreshInterval">
              <el-option label="1分钟" :value="60000" />
              <el-option label="5分钟" :value="300000" />
              <el-option label="10分钟" :value="600000" />
              <el-option label="30分钟" :value="1800000" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Reading,
  House,
  Calendar,
  Search,
  Setting,
  Refresh,
  Moon,
  Sunny,
} from '@element-plus/icons-vue'
import { useCommonStore } from '@/stores/common'
import type { NewsSource, Category } from '@/types'

// 路由
const router = useRouter()
const route = useRoute()

// Store
const commonStore = useCommonStore()

// 响应式状态
const showSettings = ref(false)
const showSidebar = ref(true)
const isDark = ref(false)
const autoRefresh = ref(false)
const refreshInterval = ref(300000) // 5分钟
const refreshLoading = ref(false)
const selectedCategory = ref('')
const selectedSource = ref<number | undefined>()

// 自动刷新定时器
let refreshTimer: NodeJS.Timeout | null = null

// 计算属性
const activeMenu = computed(() => {
  return route.name as string || 'home'
})

const sidebarWidth = computed(() => {
  return showSidebar.value ? '250px' : '0px'
})

const categories = computed(() => commonStore.categories)
const sources = computed(() => commonStore.sources)

// 生命周期
onMounted(async () => {
  await commonStore.initializeData()
  loadSettings()
  setupAutoRefresh()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})

// 方法
const goHome = () => {
  router.push('/')
}

const handleMenuSelect = (index: string) => {
  router.push({ name: index })
}

const handleRefresh = async () => {
  refreshLoading.value = true
  try {
    await commonStore.initializeData()
    // 刷新当前页面数据
    if (typeof window !== 'undefined') {
      window.location.reload()
    }
  } finally {
    refreshLoading.value = false
  }
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  saveSettings()
}

const selectCategory = (category: string) => {
  selectedCategory.value = selectedCategory.value === category ? '' : category
  router.push({
    name: 'home',
    query: { category: selectedCategory.value || undefined }
  })
}

const selectSource = (sourceId: number) => {
  selectedSource.value = selectedSource.value === sourceId ? undefined : sourceId
  router.push({
    name: 'home',
    query: { source_id: selectedSource.value?.toString() || undefined }
  })
}

const setupAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  
  if (autoRefresh.value) {
    refreshTimer = setInterval(() => {
      handleRefresh()
    }, refreshInterval.value)
  }
}

const saveSettings = () => {
  const settings = {
    isDark: isDark.value,
    showSidebar: showSidebar.value,
    autoRefresh: autoRefresh.value,
    refreshInterval: refreshInterval.value,
  }
  localStorage.setItem('ai-news-settings', JSON.stringify(settings))
}

const loadSettings = () => {
  try {
    const settings = localStorage.getItem('ai-news-settings')
    if (settings) {
      const parsed = JSON.parse(settings)
      isDark.value = parsed.isDark || false
      showSidebar.value = parsed.showSidebar !== false
      autoRefresh.value = parsed.autoRefresh || false
      refreshInterval.value = parsed.refreshInterval || 300000
      
      document.documentElement.classList.toggle('dark', isDark.value)
    }
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
}
</script>

<style scoped>
.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: var(--bg-color);
  border-bottom: 1px solid var(--border-color-lighter);
  box-shadow: var(--shadow-base);
  padding: 0;
  height: var(--header-height);
}

.header-content {
  height: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color-primary);
  transition: color 0.3s;
}

.logo:hover {
  color: var(--primary-color);
}

.logo-text {
  font-size: 20px;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.header-menu {
  border-bottom: none;
  background: transparent;
}

.header-right {
  display: flex;
  gap: 8px;
  align-items: center;
}

.main-container {
  flex: 1;
  overflow: hidden;
}

.app-sidebar {
  background: var(--bg-color);
  border-right: 1px solid var(--border-color-lighter);
  transition: width 0.3s ease;
  overflow: hidden;
}

.sidebar-content {
  padding: 16px;
  height: 100%;
  overflow-y: auto;
}

.sidebar-section {
  margin-bottom: 24px;
}

.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color-secondary);
  margin: 0 0 12px 0;
  padding: 0 16px;
}

.category-list,
.source-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.category-item,
.source-item {
  padding: 8px 16px;
  border-radius: var(--radius-small);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.category-item:hover,
.source-item:hover {
  background-color: var(--bg-color-page);
}

.category-item.active,
.source-item.active {
  background-color: var(--primary-color);
  color: white;
}

.source-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.source-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.app-main {
  background: var(--bg-color-page);
  overflow-y: auto;
  padding: 20px;
}

.settings-content {
  padding: 16px 0;
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
  }

  .header-center {
    display: none;
  }

  .logo-text {
    display: none;
  }

  .app-sidebar {
    position: fixed;
    left: 0;
    top: var(--header-height);
    height: calc(100vh - var(--header-height));
    z-index: 1000;
    box-shadow: var(--shadow-dark);
  }

  .app-main {
    padding: 16px;
  }
}
</style>
