<template>
  <div class="evaluation-task">
    <h2>评测任务管理</h2>
    
    <!-- 创建任务表单 -->
    <el-card class="create-task-card">
      <template #header>
        <div class="card-header">
          <span>创建评测任务</span>
        </div>
      </template>
      
      <el-form :model="taskForm" label-width="120px">
        <el-form-item label="任务名称">
          <el-input v-model="taskForm.name" placeholder="请输入任务名称"></el-input>
        </el-form-item>
        
        <el-form-item label="任务描述">
          <el-input 
            v-model="taskForm.description" 
            type="textarea" 
            placeholder="请输入任务描述"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="云侧API">
          <el-select v-model="taskForm.cloudConfigId" placeholder="请选择云侧API配置">
            <el-option 
              v-for="config in apiConfigs" 
              :key="config.id" 
              :label="config.name" 
              :value="config.id"
            ></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="边侧API">
          <el-select v-model="taskForm.edgeConfigId" placeholder="请选择边侧API配置">
            <el-option 
              v-for="config in apiConfigs" 
              :key="config.id" 
              :label="config.name" 
              :value="config.id"
            ></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="数据集">
          <el-select v-model="taskForm.dataset" placeholder="请选择数据集">
            <el-option label="GSM8K" value="gsm8k"></el-option>
            <el-option label="MMLU" value="mmlu"></el-option>
            <el-option label="HumanEval" value="humaneval"></el-option>
            <el-option label="Custom Dataset" value="custom"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="评测指标">
          <el-checkbox-group v-model="taskForm.metrics">
            <el-checkbox label="accuracy">准确率</el-checkbox>
            <el-checkbox label="latency">时延</el-checkbox>
            <el-checkbox label="throughput">吞吐量</el-checkbox>
            <el-checkbox label="stability">稳定性</el-checkbox>
            <el-checkbox label="consistency">一致性</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="createTask" :loading="creating">创建任务</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 任务列表 -->
    <el-card class="task-list-card">
      <template #header>
        <div class="card-header">
          <span>任务列表</span>
          <el-button @click="fetchTasks" type="primary" icon="Refresh" circle></el-button>
        </div>
      </template>
      
      <el-table :data="tasks" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="任务名称" width="180"></el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dataset" label="数据集" width="120">
          <template #default="scope">
            {{ scope.row.dataset_info?.dataset || '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="200">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="completedAt" label="完成时间" width="200">
          <template #default="scope">
            {{ formatDateTime(scope.row.completed_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="viewTask(scope.row)">查看</el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="cancelTask(scope.row.id)"
              :disabled="scope.row.status !== 'running'"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'

interface ApiConfig {
  id: string
  name: string
  type: 'cloud' | 'edge'
  provider: string
  endpoint: string
}

interface EvaluationTask {
  id: string
  name: string
  description: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  cloud_config_id: string
  edge_config_id: string
  dataset_info: {
    dataset: string
  }
  metrics_config: Record<string, any>
  created_at: string
  updated_at: string
  completed_at?: string
}

// 表单数据
const taskForm = reactive({
  name: '',
  description: '',
  cloudConfigId: '',
  edgeConfigId: '',
  dataset: '',
  metrics: ['accuracy', 'latency']
})

// 状态管理
const apiConfigs = ref<ApiConfig[]>([])
const tasks = ref<EvaluationTask[]>([])
const loading = ref(false)
const creating = ref(false)

// 获取API配置列表
const fetchApiConfigs = async () => {
  try {
    const response = await fetch('/api/configs')
    if (response.ok) {
      apiConfigs.value = await response.json()
    } else {
      ElMessage.error('获取API配置失败')
    }
  } catch (error) {
    console.error('获取API配置失败:', error)
    ElMessage.error('获取API配置失败')
  }
}

// 获取任务列表
const fetchTasks = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/tasks')
    if (response.ok) {
      tasks.value = await response.json()
    } else {
      ElMessage.error('获取任务列表失败')
    }
  } catch (error) {
    console.error('获取任务列表失败:', error)
    ElMessage.error('获取任务列表失败')
  } finally {
    loading.value = false
  }
}

// 创建任务
const createTask = async () => {
  if (!taskForm.name || !taskForm.cloudConfigId || !taskForm.edgeConfigId || !taskForm.dataset) {
    ElMessage.warning('请填写必填项')
    return
  }
  
  creating.value = true
  try {
    const taskData = {
      name: taskForm.name,
      description: taskForm.description,
      cloud_config_id: taskForm.cloudConfigId,
      edge_config_id: taskForm.edgeConfigId,
      dataset_info: {
        dataset: taskForm.dataset
      },
      metrics_config: {
        metrics: taskForm.metrics
      }
    }
    
    const response = await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(taskData)
    })
    
    if (response.ok) {
      ElMessage.success('任务创建成功')
      fetchTasks() // 刷新任务列表
      
      // 重置表单
      Object.assign(taskForm, {
        name: '',
        description: '',
        cloudConfigId: '',
        edgeConfigId: '',
        dataset: '',
        metrics: ['accuracy', 'latency']
      })
    } else {
      const errorData = await response.json()
      ElMessage.error(`任务创建失败: ${errorData.detail || '未知错误'}`)
    }
  } catch (error) {
    console.error('任务创建失败:', error)
    ElMessage.error('任务创建失败')
  } finally {
    creating.value = false
  }
}

// 查看任务详情
const viewTask = (task: EvaluationTask) => {
  ElMessage.info(`查看任务: ${task.name}`)
  // 在实际应用中，这里会跳转到任务详情页面
}

// 取消任务
const cancelTask = async (taskId: string) => {
  try {
    const response = await fetch(`/api/tasks/${taskId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'cancelled' })
    })
    
    if (response.ok) {
      ElMessage.success('任务取消成功')
      fetchTasks() // 刷新任务列表
    } else {
      const errorData = await response.json()
      ElMessage.error(`任务取消失败: ${errorData.detail || '未知错误'}`)
    }
  } catch (error) {
    console.error('任务取消失败:', error)
    ElMessage.error('任务取消失败')
  }
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

// 格式化日期时间
const formatDateTime = (dateString: string | undefined) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 组件挂载时获取数据
onMounted(() => {
  fetchApiConfigs()
  fetchTasks()
})
</script>

<style scoped>
.evaluation-task {
  padding: 20px;
}

.create-task-card,
.task-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>