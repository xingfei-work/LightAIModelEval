<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h2>AI模型评测平台</h2>
        <p>登录到您的账户</p>
      </div>
      
      <el-form 
        ref="loginFormRef" 
        :model="loginForm" 
        :rules="loginRules" 
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="email">
          <el-input 
            v-model="loginForm.email" 
            placeholder="请输入邮箱"
            type="email"
            size="large"
            prefix-icon="Message"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            placeholder="请输入密码"
            type="password"
            size="large"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            style="width: 100%"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <p>还没有账户？ <el-button type="text" @click="showRegister">立即注册</el-button></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

interface LoginForm {
  email: string
  password: string
}

const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive<LoginForm>({
  email: '',
  password: ''
})

const loginRules = reactive<FormRules>({
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
})

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 模拟登录请求
        // 在实际应用中，这里应该发送登录请求到后端
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 模拟登录成功
        ElMessage.success('登录成功')
        
        // 在实际应用中，这里应该保存token并跳转到主页
        // localStorage.setItem('token', 'your-jwt-token')
        // router.push('/')
      } catch (error) {
        ElMessage.error('登录失败，请检查邮箱和密码')
      } finally {
        loading.value = false
      }
    }
  })
}

const showRegister = () => {
  ElMessage.info('注册功能正在开发中')
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.login-box {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.login-header p {
  margin: 0;
  color: #909399;
}

.login-form {
  margin-bottom: 20px;
}

.login-footer {
  text-align: center;
  color: #909399;
}

.login-footer p {
  margin: 0;
}
</style>