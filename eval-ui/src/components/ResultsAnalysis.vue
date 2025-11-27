<template>
  <div class="results-analysis">
    <h2>评测结果分析</h2>
    
    <!-- 任务选择 -->
    <el-card class="filter-card">
      <template #header>
        <div class="card-header">
          <span>筛选条件</span>
        </div>
      </template>
      
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="选择任务">
          <el-select 
            v-model="filterForm.taskId" 
            placeholder="请选择评测任务" 
            @change="loadResults"
          >
            <el-option 
              v-for="task in tasks" 
              :key="task.id" 
              :label="task.name" 
              :value="task.id"
            ></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadResults" :loading="loading">加载结果</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 指标对比图表 -->
    <div v-if="filterForm.taskId && !loading">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>准确率对比</span>
              </div>
            </template>
            <v-chart class="chart" :option="accuracyChartOption" autoresize />
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>时延对比</span>
              </div>
            </template>
            <v-chart class="chart" :option="latencyChartOption" autoresize />
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>吞吐量对比</span>
              </div>
            </template>
            <v-chart class="chart" :option="throughputChartOption" autoresize />
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>稳定性对比</span>
              </div>
            </template>
            <v-chart class="chart" :option="stabilityChartOption" autoresize />
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 详细数据表格 -->
      <el-card style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>详细指标数据</span>
          </div>
        </template>
        
        <el-table :data="metricsData" style="width: 100%">
          <el-table-column prop="metric" label="指标" width="180"></el-table-column>
          <el-table-column prop="cloudValue" label="云侧数值" width="180">
            <template #default="scope">
              {{ formatValue(scope.row.cloudValue) }}
            </template>
          </el-table-column>
          <el-table-column prop="edgeValue" label="边侧数值" width="180">
            <template #default="scope">
              {{ formatValue(scope.row.edgeValue) }}
            </template>
          </el-table-column>
          <el-table-column prop="difference" label="差异">
            <template #default="scope">
              <span :class="getDifferenceClass(scope.row.difference)">
                {{ formatValue(scope.row.difference) }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
    
    <div v-else-if="filterForm.taskId && loading" class="placeholder">
      <el-skeleton animated>
        <template #template>
          <el-skeleton-item variant="p" style="width: 100%; height: 300px" />
        </template>
      </el-skeleton>
    </div>
    
    <div v-else class="placeholder">
      <el-empty description="请选择一个评测任务查看结果"></el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { ElMessage } from 'element-plus'

// 注册 echarts 组件
use([
  CanvasRenderer,
  BarChart,
  LineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent
])

interface EvaluationTask {
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
  completed_at?: string
}

interface MetricsResult {
  id: number
  task_id: string
  metric_type: string
  cloud_value: number | null
  edge_value: number | null
  diff_value: number | null
  details: string | null
  created_at: string
}

// 筛选表单
const filterForm = reactive({
  taskId: ''
})

// 数据
const tasks = ref<EvaluationTask[]>([])
const metricsData = ref<MetricsResult[]>([])
const loading = ref(false)

// 图表配置
const accuracyChartOption = ref<any>({})
const latencyChartOption = ref<any>({})
const throughputChartOption = ref<any>({})
const stabilityChartOption = ref<any>({})

// 获取已完成的任务列表
const fetchTasks = async () => {
  try {
    const response = await fetch('/api/tasks?status=completed')
    if (response.ok) {
      tasks.value = await response.json()
    } else {
      ElMessage.error('获取任务列表失败')
    }
  } catch (error) {
    console.error('获取任务列表失败:', error)
    ElMessage.error('获取任务列表失败')
  }
}

// 加载结果数据
const loadResults = async () => {
  if (!filterForm.taskId) return
  
  loading.value = true
  try {
    // 在实际应用中，这里应该从后端获取真实的评测结果
    // 目前我们使用模拟数据
    const results: MetricsResult[] = [
      { 
        id: 1, 
        task_id: filterForm.taskId, 
        metric_type: '准确率', 
        cloud_value: 0.85, 
        edge_value: 0.78, 
        diff_value: -0.07, 
        details: null, 
        created_at: new Date().toISOString() 
      },
      { 
        id: 2, 
        task_id: filterForm.taskId, 
        metric_type: '平均时延(ms)', 
        cloud_value: 420, 
        edge_value: 180, 
        diff_value: -240, 
        details: null, 
        created_at: new Date().toISOString() 
      },
      { 
        id: 3, 
        task_id: filterForm.taskId, 
        metric_type: '吞吐量(req/s)', 
        cloud_value: 2.4, 
        edge_value: 5.6, 
        diff_value: 3.2, 
        details: null, 
        created_at: new Date().toISOString() 
      },
      { 
        id: 4, 
        task_id: filterForm.taskId, 
        metric_type: '稳定性(标准差)', 
        cloud_value: 0.05, 
        edge_value: 0.12, 
        diff_value: 0.07, 
        details: null, 
        created_at: new Date().toISOString() 
      }
    ]
    
    metricsData.value = results
    
    // 更新图表配置
    updateChartOptions(results)
  } catch (error) {
    console.error('加载结果数据失败:', error)
    ElMessage.error('加载结果数据失败')
  } finally {
    loading.value = false
  }
}

// 更新图表配置
const updateChartOptions = (data: MetricsResult[]) => {
  // 准确率图表
  accuracyChartOption.value = {
    title: { text: '准确率对比' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['云侧', '边侧'] },
    xAxis: {
      type: 'category',
      data: data.filter(item => item.metric_type === '准确率').map(item => item.metric_type)
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '云侧',
        type: 'bar',
        data: data.filter(item => item.metric_type === '准确率').map(item => item.cloud_value),
        itemStyle: { color: '#409EFF' }
      },
      {
        name: '边侧',
        type: 'bar',
        data: data.filter(item => item.metric_type === '准确率').map(item => item.edge_value),
        itemStyle: { color: '#67C23A' }
      }
    ]
  }
  
  // 时延图表
  const latencyData = data.find(item => item.metric_type.includes('时延'))
  latencyChartOption.value = {
    title: { text: '时延对比' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['云侧', '边侧'] },
    xAxis: {
      type: 'category',
      data: latencyData ? [latencyData.metric_type] : []
    },
    yAxis: { 
      type: 'value',
      axisLabel: { formatter: '{value} ms' }
    },
    series: [
      {
        name: '云侧',
        type: 'bar',
        data: latencyData ? [latencyData.cloud_value] : [],
        itemStyle: { color: '#409EFF' }
      },
      {
        name: '边侧',
        type: 'bar',
        data: latencyData ? [latencyData.edge_value] : [],
        itemStyle: { color: '#67C23A' }
      }
    ]
  }
  
  // 吞吐量图表
  const throughputData = data.find(item => item.metric_type.includes('吞吐量'))
  throughputChartOption.value = {
    title: { text: '吞吐量对比' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['云侧', '边侧'] },
    xAxis: {
      type: 'category',
      data: throughputData ? [throughputData.metric_type] : []
    },
    yAxis: { 
      type: 'value',
      axisLabel: { formatter: '{value} req/s' }
    },
    series: [
      {
        name: '云侧',
        type: 'bar',
        data: throughputData ? [throughputData.cloud_value] : [],
        itemStyle: { color: '#409EFF' }
      },
      {
        name: '边侧',
        type: 'bar',
        data: throughputData ? [throughputData.edge_value] : [],
        itemStyle: { color: '#67C23A' }
      }
    ]
  }
  
  // 稳定性图表
  const stabilityData = data.find(item => item.metric_type.includes('稳定性'))
  stabilityChartOption.value = {
    title: { text: '稳定性对比' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['云侧', '边侧'] },
    xAxis: {
      type: 'category',
      data: stabilityData ? [stabilityData.metric_type] : []
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '云侧',
        type: 'bar',
        data: stabilityData ? [stabilityData.cloud_value] : [],
        itemStyle: { color: '#409EFF' }
      },
      {
        name: '边侧',
        type: 'bar',
        data: stabilityData ? [stabilityData.edge_value] : [],
        itemStyle: { color: '#67C23A' }
      }
    ]
  }
}

// 格式化数值显示
const formatValue = (value: number | null) => {
  if (value === null || value === undefined) return '-'
  return value.toFixed(4)
}

// 获取差异值的显示样式
const getDifferenceClass = (value: number | null) => {
  if (value === null || value === undefined) return ''
  return value > 0 ? 'positive' : value < 0 ? 'negative' : ''
}

// 组件挂载时获取任务列表
onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>
.results-analysis {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart {
  height: 300px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.placeholder {
  text-align: center;
  padding: 50px 0;
}

.positive {
  color: #67C23A;
}

.negative {
  color: #F56C6C;
}
</style>