<template>
  <div class="task-detail">
    <el-page-header @back="goBack" :content="task?.name || '任务详情'"></el-page-header>
    
    <div v-if="loading" class="loading-container">
      <el-skeleton animated>
        <template #template>
          <el-skeleton-item variant="p" style="width: 100%; height: 400px" />
        </template>
      </el-skeleton>
    </div>
    
    <div v-else-if="task" class="task-content">
      <el-row :gutter="20">
        <el-col :span="16">
          <el-card class="task-info-card">
            <template #header>
              <div class="card-header">
                <span>任务信息</span>
              </div>
            </template>
            
            <el-descriptions :column="1" border>
              <el-descriptions-item label="任务名称">{{ task.name }}</el-descriptions-item>
              <el-descriptions-item label="任务描述">{{ task.description || '-' }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="getStatusTagType(task.status)">
                  {{ getStatusText(task.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="数据集">
                {{ task.dataset_info?.dataset || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="创建时间">
                {{ formatDateTime(task.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="开始时间">
                {{ formatDateTime(task.started_at) || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="完成时间">
                {{ formatDateTime(task.completed_at) || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="评测指标">
                <el-tag 
                  v-for="metric in task.metrics_config?.metrics" 
                  :key="metric" 
                  style="margin-right: 10px;"
                >
                  {{ getMetricText(metric) }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
          
          <el-card class="task-log-card" style="margin-top: 20px;">
            <template #header>
              <div class="card-header">
                <span>任务日志</span>
              </div>
            </template>
            
            <el-timeline>
              <el-timeline-item
                v-for="(log, index) in taskLogs"
                :key="index"
                :timestamp="formatDateTime(log.timestamp)"
                :type="getLogType(log.level)"
              >
                <p><strong>{{ log.level.toUpperCase() }}:</strong> {{ log.message }}</p>
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="task-actions-card">
            <template #header>
              <div class="card-header">
                <span>操作</span>
              </div>
            </template>
            
            <div class="actions">
              <el-button 
                type="primary" 
                @click="startTask" 
                :disabled="task.status !== 'pending'"
                style="width: 100%; margin-bottom: 10px;"
              >
                开始任务
              </el-button>
              <el-button 
                type="danger" 
                @click="cancelTask" 
                :disabled="task.status !== 'running'"
                style="width: 100%; margin-bottom: 10px;"
              >
                取消任务
              </el-button>
              <el-button 
                @click="exportReport" 
                :disabled="task.status !== 'completed'"
                style="width: 100%; margin-bottom: 10px;"
              >
                导出报告
              </el-button>
            </div>
          </el-card>
          
          <el-card class="task-config-card" style="margin-top: 20px;">
            <template #header>
              <div class="card-header">
                <span>配置信息</span>
              </div>
            </template>
            
            <h4>云侧API</h4>
            <p v-if="cloudConfig">{{ cloudConfig.name }}</p>
            <p v-else>加载中...</p>
            
            <h4 style="margin-top: 20px;">边侧API</h4>
            <p v-if="edgeConfig">{{ edgeConfig.name }}</p>
            <p v-else>加载中...</p>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <div v-else class="placeholder">
      <el-empty description="任务不存在或加载失败"></el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

interface Task {
  id: string
  name: string
  description: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  cloud_config_id: string
  edge_config_id: string
  dataset_info: Record<string, any>
  metrics_config: Record<string, any>
  created_at: string
  updated_at: string
  started_at?: string
  completed_at?: string
}

interface ApiConfig {
  id: string
  name: string
  type: 'cloud' | 'edge'
  provider: string
  endpoint: string
}

interface TaskLog {
  timestamp: string
  level: 'info' | 'warning' | 'error' | 'debug'
  message: string
}

const route = useRoute()
const router = useRouter()

const taskId = route.params.id as string

const task = ref<Task | null>(null)
const cloudConfig = ref<ApiConfig | null>(null)
const edgeConfig = ref<ApiConfig | null>(null)
const taskLogs = ref<TaskLog[]>([])
const loading = ref(true)

// 获取任务详情
const fetchTaskDetail = async () => {
  loading.value = true
  try {
    // 获取任务信息
    const taskResponse = await fetch(`/api/tasks/${taskId}`)
    if (taskResponse.ok) {
      task.value = await taskResponse.json()
      
      // 获取API配置信息
      if (task.value?.cloud_config_id) {
        const cloudResponse = await fetch(`/api/configs/${task.value.cloud_config_id}`)
        if (cloudResponse.ok) {
          cloudConfig.value = await cloudResponse.json()
        }
      }
      
      if (task.value?.edge_config_id) {
        const edgeResponse = await fetch(`/api/configs/${task.value.edge_config_id}`)
        if (edgeResponse.ok) {
          edgeConfig.value = await edgeResponse.json()
        }
      }
      
      // 模拟任务日志
      taskLogs.value = [
        { timestamp: new Date().toISOString(), level: 'info', message: '任务已创建' },
        { timestamp: new Date().toISOString(), level: 'info', message: '开始初始化评测环境' },
        { timestamp: new Date().toISOString(), level: 'info', message: '云侧API连接成功' },
        { timestamp: new Date().toISOString(), level: 'info', message: '边侧API连接成功' }
      ]
    } else {
      ElMessage.error('获取任务详情失败')
    }
  } catch (error) {
    console.error('获取任务详情失败:', error)
    ElMessage.error('获取任务详情失败')
  } finally {
    loading.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.push('/evaluation')
}

// 开始任务
const startTask = async () => {
  try {
    const response = await fetch(`/api/tasks/${taskId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'running', started_at: new Date().toISOString() })
    })
    
    if (response.ok) {
      ElMessage.success('任务已开始')
      fetchTaskDetail() // 刷新任务详情
    } else {
      const errorData = await response.json()
      ElMessage.error(`启动任务失败: ${errorData.detail || '未知错误'}`)
    }
  } catch (error) {
    console.error('启动任务失败:', error)
    ElMessage.error('启动任务失败')
  }
}

// 取消任务
const cancelTask = async () => {
  try {
    const response = await fetch(`/api/tasks/${taskId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'cancelled' })
    })
    
    if (response.ok) {
      ElMessage.success('任务已取消')
      fetchTaskDetail() // 刷新任务详情
    } else {
      const errorData = await response.json()
      ElMessage.error(`取消任务失败: ${errorData.detail || '未知错误'}`)
    }
  } catch (error) {
    console.error('取消任务失败:', error)
    ElMessage.error('取消任务失败')
  }
}

// 导出报告
const exportReport = () => {
  ElMessage.info('报告导出功能正在开发中')
}

// 获取状态标签类型
const getStatusTagType = (status: string) => {
  switch (status) {
    case 'completed':
      return 'success'
    case 'running':
      return 'primary'
    case 'failed':
      return 'danger'
    case 'cancelled':
      return 'warning'
    default:
      return 'info'
  }
}

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'pending':
      return '待处理'
    case 'running':
      return '运行中'
    case 'completed':
      return '已完成'
    case 'failed':
      return '失败'
    case 'cancelled':
      return '已取消'
    default:
      return status
  }
}

// 获取指标文本
const getMetricText = (metric: string) => {
  const metricMap: Record<string, string> = {
    'accuracy': '准确率',
    'latency': '时延',
    'throughput': '吞吐量',
    'stability': '稳定性',
    'consistency': '一致性'
  }
  return metricMap[metric] || metric
}

// 获取日志类型
const getLogType = (level: string) => {
  switch (level) {
    case 'error':
      return 'danger'
    case 'warning':
      return 'warning'
    default:
      return 'primary'
  }
}

// 格式化日期时间
const formatDateTime = (dateString: string | undefined) => {
  if (!dateString) return null
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 组件挂载时获取数据
onMounted(() => {
  fetchTaskDetail()
})
</script>

<style scoped>
.task-detail {
  padding: 20px;
}

.loading-container {
  padding: 50px 0;
}

.task-content {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.actions {
  text-align: center;
}

h4 {
  margin: 0 0 10px 0;
  color: #606266;
}
</style>