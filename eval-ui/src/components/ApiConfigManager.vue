<template>
  <div class="api-config-manager">
    <h2>API配置管理</h2>
    
    <!-- 配置列表 -->
    <div class="config-list">
      <el-table :data="configs" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="配置名称" width="180"></el-table-column>
        <el-table-column prop="type" label="类型" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.type === 'cloud' ? 'primary' : 'success'">
              {{ scope.row.type === 'cloud' ? '云侧' : '边侧' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="provider" label="提供商" width="120"></el-table-column>
        <el-table-column prop="endpoint" label="API端点"></el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editConfig(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteConfig(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 添加/编辑配置表单 -->
    <div class="config-form">
      <el-button type="primary" @click="showCreateForm">新增配置</el-button>
      
      <el-dialog v-model="dialogVisible" :title="editingConfig ? '编辑配置' : '新增配置'" width="600px">
        <el-form :model="form" label-width="120px">
          <el-form-item label="配置名称">
            <el-input v-model="form.name" placeholder="请输入配置名称"></el-input>
          </el-form-item>
          
          <el-form-item label="类型">
            <el-select v-model="form.type" placeholder="请选择类型">
              <el-option label="云侧API" value="cloud"></el-option>
              <el-option label="边侧API" value="edge"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="提供商">
            <el-input v-model="form.provider" placeholder="例如: openai, azure, custom"></el-input>
          </el-form-item>
          
          <el-form-item label="API端点">
            <el-input v-model="form.endpoint" placeholder="例如: https://api.openai.com/v1/chat/completions"></el-input>
          </el-form-item>
          
          <el-form-item label="认证配置">
            <el-input 
              v-model="form.auth_config.api_key" 
              type="password" 
              placeholder="请输入API密钥"
              show-password
            ></el-input>
          </el-form-item>
          
          <el-form-item label="协议类型">
            <el-select v-model="form.protocol_type" placeholder="请选择协议类型">
              <el-option label="OpenAI" value="openai"></el-option>
              <el-option label="RESTful" value="restful"></el-option>
              <el-option label="JSON-RPC" value="jsonrpc"></el-option>
              <el-option label="自定义" value="custom"></el-option>
            </el-select>
          </el-form-item>
          
          <div v-if="form.type === 'edge'">
            <el-form-item label="请求映射">
              <el-input 
                v-model="protocolConfigInput.request_mapping" 
                type="textarea" 
                placeholder='{"prompt": "input.text", "max_tokens": "params.max_new_tokens"}'
              ></el-input>
            </el-form-item>
            
            <el-form-item label="响应映射">
              <el-input 
                v-model="protocolConfigInput.response_mapping" 
                type="textarea" 
                placeholder='{"result": "data.result"}'
              ></el-input>
            </el-form-item>
          </div>
        </el-form>
        
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="saveConfig">保存</el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface ApiConfig {
  id: string
  name: string
  type: 'cloud' | 'edge'
  provider: string
  endpoint: string
  auth_config: Record<string, any>
  protocol_type: string
  protocol_config?: Record<string, any>
  default_params?: Record<string, any>
  is_active: boolean
  created_at: string
  updated_at: string
}

// 状态管理
const configs = ref<ApiConfig[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingConfig = ref<ApiConfig | null>(null)

// 表单数据
const form = reactive({
  name: '',
  type: 'cloud',
  provider: '',
  endpoint: '',
  auth_config: {
    api_key: ''
  },
  protocol_type: 'openai',
  protocol_config: {} as Record<string, any>
})

// 协议配置输入（用于文本框显示）
const protocolConfigInput = reactive({
  request_mapping: '',
  response_mapping: ''
})

// 获取配置列表
const fetchConfigs = async () => {
  loading.value = true
  try {
    // 模拟API调用
    // const response = await fetch('/api/configs')
    // configs.value = await response.json()
    
    // 模拟数据
    configs.value = [
      {
        id: '1',
        name: 'OpenAI Production',
        type: 'cloud',
        provider: 'openai',
        endpoint: 'https://api.openai.com/v1/chat/completions',
        auth_config: { api_key: 'sk-xxx***xyz' },
        protocol_type: 'openai',
        is_active: true,
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z'
      },
      {
        id: '2',
        name: 'Edge Model Dev',
        type: 'edge',
        provider: 'custom',
        endpoint: 'http://localhost:8000/api/v1/chat',
        auth_config: { api_key: 'sk-abc***def' },
        protocol_type: 'restful',
        protocol_config: {
          request_mapping: { prompt: 'input.text' },
          response_mapping: { result: 'data.result' }
        },
        is_active: true,
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z'
      }
    ]
  } catch (error) {
    ElMessage.error('获取配置列表失败')
  } finally {
    loading.value = false
  }
}

// 显示创建表单
const showCreateForm = () => {
  editingConfig.value = null
  Object.assign(form, {
    name: '',
    type: 'cloud',
    provider: '',
    endpoint: '',
    auth_config: { api_key: '' },
    protocol_type: 'openai',
    protocol_config: {}
  })
  protocolConfigInput.request_mapping = ''
  protocolConfigInput.response_mapping = ''
  dialogVisible.value = true
}

// 编辑配置
const editConfig = (config: ApiConfig) => {
  editingConfig.value = config
  Object.assign(form, { ...config })
  
  // 处理协议配置显示
  if (config.protocol_config) {
    protocolConfigInput.request_mapping = config.protocol_config.request_mapping 
      ? JSON.stringify(config.protocol_config.request_mapping) 
      : ''
    protocolConfigInput.response_mapping = config.protocol_config.response_mapping 
      ? JSON.stringify(config.protocol_config.response_mapping) 
      : ''
  } else {
    protocolConfigInput.request_mapping = ''
    protocolConfigInput.response_mapping = ''
  }
  
  dialogVisible.value = true
}

// 保存配置
const saveConfig = async () => {
  try {
    // 处理协议配置
    if (form.type === 'edge' && (protocolConfigInput.request_mapping || protocolConfigInput.response_mapping)) {
      form.protocol_config = {}
      if (protocolConfigInput.request_mapping) {
        form.protocol_config.request_mapping = JSON.parse(protocolConfigInput.request_mapping)
      }
      if (protocolConfigInput.response_mapping) {
        form.protocol_config.response_mapping = JSON.parse(protocolConfigInput.response_mapping)
      }
    }
    
    if (editingConfig.value) {
      // 更新配置
      // await fetch(`/api/configs/${editingConfig.value.id}`, {
      //   method: 'PUT',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(form)
      // })
      ElMessage.success('配置更新成功')
    } else {
      // 创建配置
      // await fetch('/api/configs', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(form)
      // })
      ElMessage.success('配置创建成功')
    }
    
    dialogVisible.value = false
    fetchConfigs() // 刷新列表
  } catch (error) {
    ElMessage.error('保存配置失败')
  }
}

// 删除配置
const deleteConfig = async (id: string) => {
  ElMessageBox.confirm('确定要删除这个配置吗？', '确认删除', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      // await fetch(`/api/configs/${id}`, { method: 'DELETE' })
      ElMessage.success('配置删除成功')
      fetchConfigs() // 刷新列表
    } catch (error) {
      ElMessage.error('删除配置失败')
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 组件挂载时获取数据
onMounted(() => {
  fetchConfigs()
})
</script>

<style scoped>
.api-config-manager {
  padding: 20px;
}

.config-list {
  margin-bottom: 20px;
}

.config-form {
  margin-top: 20px;
}

.dialog-footer {
  text-align: right;
}
</style>