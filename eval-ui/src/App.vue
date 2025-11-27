<script setup lang="ts">
import { ref } from 'vue'
import ApiConfigManager from './components/ApiConfigManager.vue'
import EvaluationTask from './components/EvaluationTask.vue'
import ResultsAnalysis from './components/ResultsAnalysis.vue'
import HelloWorld from './components/HelloWorld.vue'

const activeTab = ref('home')
</script>

<template>
  <div class="app-wrapper">
    <!-- 顶部导航栏 -->
    <el-menu 
      :default-active="activeTab" 
      class="el-menu-demo" 
      mode="horizontal" 
      @select="activeTab = $event"
    >
      <el-menu-item index="home">首页</el-menu-item>
      <el-menu-item index="api-config">API配置管理</el-menu-item>
      <el-menu-item index="evaluation">评测任务</el-menu-item>
      <el-menu-item index="results">结果分析</el-menu-item>
    </el-menu>
    
    <!-- 页面内容 -->
    <div class="main-content">
      <div v-if="activeTab === 'home'">
        <div class="header">
          <img src="/vite.svg" class="logo" alt="Vite logo" />
          <img src="./assets/vue.svg" class="logo vue" alt="Vue logo" />
        </div>
        <HelloWorld msg="AI模型评测平台" />
      </div>
      
      <div v-else-if="activeTab === 'api-config'">
        <ApiConfigManager />
      </div>
      
      <div v-else-if="activeTab === 'evaluation'">
        <EvaluationTask />
      </div>
      
      <div v-else-if="activeTab === 'results'">
        <ResultsAnalysis />
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-wrapper {
  min-height: 100vh;
}

.el-menu-demo {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.main-content {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 20px 0;
}

.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}

.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}

.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>