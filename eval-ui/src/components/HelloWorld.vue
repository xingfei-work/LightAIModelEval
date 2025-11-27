<template>
  <div class="hello">
    <h1>{{ msg }}</h1>
    <h2>基于OpenCompass的AI模型API评测平台</h2>
    <p>
      这是一个专注于通过API形式进行大模型评测的系统，支持云侧和边侧模型的协同评测与对比分析。
    </p>
    
    <div class="features">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="feature-card">
            <template #header>
              <div class="card-header">
                <el-icon><Setting /></el-icon>
                <span>统一API适配</span>
              </div>
            </template>
            <p>支持多种AI模型API协议，包括OpenAI标准、自定义RESTful等</p>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="feature-card">
            <template #header>
              <div class="card-header">
                <el-icon><Monitor /></el-icon>
                <span>云边协同评测</span>
              </div>
            </template>
            <p>同时评测云侧和边侧模型，提供全面的性能对比分析</p>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="feature-card">
            <template #header>
              <div class="card-header">
                <el-icon><DataAnalysis /></el-icon>
                <span>多维度指标</span>
              </div>
            </template>
            <p>支持准确率、时延、吞吐量、稳定性等多项指标评测</p>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <div class="quick-start">
      <h3>快速开始</h3>
      <p>点击上方导航栏开始使用：</p>
      <ul>
        <li><strong>API配置管理</strong> - 配置云侧和边侧模型的API接入</li>
        <li><strong>评测任务</strong> - 创建和管理评测任务</li>
        <li><strong>结果分析</strong> - 查看和分析评测结果</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Ref } from 'vue'
import { Setting, Monitor, DataAnalysis } from '@element-plus/icons-vue'

defineProps<{ msg: string }>()

const count: Ref<number> = ref(0)
</script>

<style scoped>
.hello {
  text-align: center;
  padding: 20px;
}

h1 {
  font-size: 2rem;
  margin-bottom: 10px;
}

h2 {
  font-size: 1.5rem;
  color: #646cff;
  margin-bottom: 20px;
}

h3 {
  margin-top: 30px;
  margin-bottom: 15px;
}

.features {
  margin: 30px 0;
}

.feature-card {
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quick-start {
  text-align: left;
  max-width: 600px;
  margin: 0 auto;
}

.quick-start ul {
  padding-left: 20px;
}

.quick-start li {
  margin-bottom: 10px;
}
</style>