<template>
  <div class="not-found-page">
    <div class="not-found-content">
      <div class="not-found-icon">
        <el-icon size="120"><WarnTriangleFilled /></el-icon>
      </div>
      <h1 class="not-found-title">页面未找到</h1>
      <p class="not-found-description">
        抱歉，您访问的页面不存在或已被移除。
      </p>
      <div class="not-found-actions">
        <el-button type="primary" @click="goHome">
          返回首页
        </el-button>
        <el-button @click="goBack">
          返回上页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { WarnTriangleFilled } from '@element-plus/icons-vue'

const router = useRouter()

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.not-found-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 40px 20px;
}

.not-found-content {
  text-align: center;
  max-width: 500px;
}

.not-found-icon {
  color: var(--text-color-placeholder);
  margin-bottom: 24px;
}

.not-found-title {
  font-size: 32px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 16px 0;
}

.not-found-description {
  font-size: 16px;
  color: var(--text-color-secondary);
  margin: 0 0 32px 0;
  line-height: 1.6;
}

.not-found-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}
</style>
