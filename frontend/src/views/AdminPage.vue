<template>
  <div class="admin-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><Setting /></el-icon>
        管理后台
      </h1>
      <p class="page-description">系统管理和配置</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card">
        <el-statistic
          title="总文章数"
          :value="stats?.total_articles || 0"
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
          title="已处理文章"
          :value="stats?.processed_articles || 0"
          suffix="篇"
        >
          <template #title>
            <div class="stat-title">
              <el-icon><Check /></el-icon>
              已处理文章
            </div>
          </template>
        </el-statistic>
      </el-card>

      <el-card class="stat-card">
        <el-statistic
          title="今日新增"
          :value="stats?.today_articles || 0"
          suffix="篇"
        >
          <template #title>
            <div class="stat-title">
              <el-icon><Plus /></el-icon>
              今日新增
            </div>
          </template>
        </el-statistic>
      </el-card>

      <el-card class="stat-card">
        <el-statistic
          title="活跃源"
          :value="stats?.active_sources || 0"
          suffix="个"
        >
          <template #title>
            <div class="stat-title">
              <el-icon><Link /></el-icon>
              活跃源
            </div>
          </template>
        </el-statistic>
      </el-card>
    </div>

    <!-- 管理选项卡 -->
    <el-tabs v-model="activeTab" class="admin-tabs">
      <!-- 新闻源管理 -->
      <el-tab-pane label="新闻源管理" name="sources">
        <div class="sources-management">
          <div class="section-header">
            <h3>新闻源管理</h3>
            <el-button type="primary" @click="showAddSourceDialog = true">
              添加新闻源
            </el-button>
          </div>

          <el-table
            :data="sources"
            v-loading="sourcesLoading"
            stripe
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="url" label="URL" />
            <el-table-column prop="source_type" label="类型" width="100" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'danger'">
                  {{ row.is_active ? '活跃' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="fetch_interval" label="抓取间隔(分钟)" width="120" />
            <el-table-column label="最后抓取时间" width="160">
              <template #default="{ row }">
                {{ row.last_fetch_time ? formatDate(row.last_fetch_time) : '未抓取' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button
                  size="small"
                  @click="fetchSource(row.id)"
                  :loading="fetchingSourceId === row.id"
                >
                  立即抓取
                </el-button>
                <el-button
                  size="small"
                  type="primary"
                  @click="editSource(row)"
                >
                  编辑
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click="deleteSource(row.id)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 系统监控 -->
      <el-tab-pane label="系统监控" name="monitor">
        <div class="system-monitor">
          <h3>系统监控</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="系统状态">
              <el-tag type="success">正常运行</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="当前时间">
              {{ formatDate(new Date()) }}
            </el-descriptions-item>
            <el-descriptions-item label="总文章数">
              {{ stats?.total_articles || 0 }}
            </el-descriptions-item>
            <el-descriptions-item label="已处理文章">
              {{ stats?.processed_articles || 0 }}
            </el-descriptions-item>
            <el-descriptions-item label="今日新增">
              {{ stats?.today_articles || 0 }}
            </el-descriptions-item>
            <el-descriptions-item label="活跃源数量">
              {{ stats?.active_sources || 0 }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 添加新闻源对话框 -->
    <el-dialog
      v-model="showAddSourceDialog"
      title="添加新闻源"
      width="500px"
    >
      <el-form
        ref="sourceFormRef"
        :model="sourceForm"
        :rules="sourceRules"
        label-width="100px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="sourceForm.name" />
        </el-form-item>
        <el-form-item label="URL" prop="url">
          <el-input v-model="sourceForm.url" />
        </el-form-item>
        <el-form-item label="类型" prop="source_type">
          <el-select v-model="sourceForm.source_type" style="width: 100%">
            <el-option label="RSS" value="rss" />
            <el-option label="网页" value="web" />
          </el-select>
        </el-form-item>
        <el-form-item label="抓取间隔">
          <el-input-number
            v-model="sourceForm.fetch_interval"
            :min="1"
            :max="1440"
            suffix="分钟"
          />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="sourceForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddSourceDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="submitSourceForm"
          :loading="submitLoading"
        >
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑新闻源对话框 -->
    <el-dialog
      v-model="showEditSourceDialog"
      title="编辑新闻源"
      width="500px"
    >
      <el-form
        ref="editSourceFormRef"
        :model="editSourceForm"
        :rules="sourceRules"
        label-width="100px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="editSourceForm.name" />
        </el-form-item>
        <el-form-item label="URL" prop="url">
          <el-input v-model="editSourceForm.url" />
        </el-form-item>
        <el-form-item label="类型" prop="source_type">
          <el-select v-model="editSourceForm.source_type" style="width: 100%">
            <el-option label="RSS" value="rss" />
            <el-option label="网页" value="web" />
          </el-select>
        </el-form-item>
        <el-form-item label="抓取间隔">
          <el-input-number
            v-model="editSourceForm.fetch_interval"
            :min="1"
            :max="1440"
            suffix="分钟"
          />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="editSourceForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditSourceDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="submitEditSourceForm"
          :loading="submitLoading"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting,
  Document,
  Check,
  Plus,
  Link,
} from '@element-plus/icons-vue'
import { adminApi, systemApi } from '@/api'
import { formatDate } from '@/utils'
import type { NewsSource, Stats } from '@/types'

// 响应式状态
const activeTab = ref('sources')
const stats = ref<Stats | null>(null)
const sources = ref<NewsSource[]>([])
const sourcesLoading = ref(false)
const fetchingSourceId = ref<number | null>(null)
const submitLoading = ref(false)

// 表单状态
const showAddSourceDialog = ref(false)
const showEditSourceDialog = ref(false)
const sourceFormRef = ref()
const editSourceFormRef = ref()
const sourceForm = ref({
  name: '',
  url: '',
  source_type: 'rss',
  fetch_interval: 60,
  is_active: true,
})
const editSourceForm = ref({
  id: 0,
  name: '',
  url: '',
  source_type: 'rss',
  fetch_interval: 60,
  is_active: true,
})

// 表单验证规则
const sourceRules = {
  name: [
    { required: true, message: '请输入新闻源名称', trigger: 'blur' }
  ],
  url: [
    { required: true, message: '请输入URL', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL', trigger: 'blur' }
  ],
  source_type: [
    { required: true, message: '请选择类型', trigger: 'change' }
  ],
}

// 生命周期
onMounted(async () => {
  await loadInitialData()
})

// 方法
const loadInitialData = async () => {
  await Promise.all([
    loadStats(),
    loadSources(),
  ])
}

const loadStats = async () => {
  try {
    stats.value = await systemApi.getStats()
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const loadSources = async () => {
  try {
    sourcesLoading.value = true
    sources.value = await adminApi.sources.list()
  } catch (error) {
    console.error('Failed to load sources:', error)
    ElMessage.error('加载新闻源失败')
  } finally {
    sourcesLoading.value = false
  }
}

const fetchSource = async (id: number) => {
  try {
    fetchingSourceId.value = id
    await adminApi.sources.fetch(id)
    ElMessage.success('抓取任务已启动')
    await loadSources()
  } catch (error) {
    console.error('Failed to fetch source:', error)
    ElMessage.error('启动抓取失败')
  } finally {
    fetchingSourceId.value = null
  }
}

const editSource = (source: NewsSource) => {
  editSourceForm.value = { ...source }
  showEditSourceDialog.value = true
}

const deleteSource = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个新闻源吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    
    await adminApi.sources.delete(id)
    ElMessage.success('删除成功')
    await loadSources()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete source:', error)
      ElMessage.error('删除失败')
    }
  }
}

const submitSourceForm = async () => {
  try {
    await sourceFormRef.value.validate()
    submitLoading.value = true
    
    await adminApi.sources.create(sourceForm.value)
    ElMessage.success('添加成功')
    showAddSourceDialog.value = false
    resetSourceForm()
    await loadSources()
  } catch (error) {
    console.error('Failed to create source:', error)
    ElMessage.error('添加失败')
  } finally {
    submitLoading.value = false
  }
}

const submitEditSourceForm = async () => {
  try {
    await editSourceFormRef.value.validate()
    submitLoading.value = true
    
    const { id, ...data } = editSourceForm.value
    await adminApi.sources.update(id, data)
    ElMessage.success('更新成功')
    showEditSourceDialog.value = false
    await loadSources()
  } catch (error) {
    console.error('Failed to update source:', error)
    ElMessage.error('更新失败')
  } finally {
    submitLoading.value = false
  }
}

const resetSourceForm = () => {
  sourceForm.value = {
    name: '',
    url: '',
    source_type: 'rss',
    fetch_interval: 60,
    is_active: true,
  }
}
</script>

<style scoped>
.admin-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0 0 8px 0;
}

.page-description {
  color: var(--text-color-secondary);
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
}

.stat-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-weight: 600;
}

.admin-tabs {
  background: var(--bg-color);
  border-radius: var(--radius-base);
  padding: 16px;
}

.sources-management {
  padding: 16px 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
  color: var(--text-color-primary);
}

.system-monitor {
  padding: 16px 0;
}

.system-monitor h3 {
  margin: 0 0 16px 0;
  color: var(--text-color-primary);
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
