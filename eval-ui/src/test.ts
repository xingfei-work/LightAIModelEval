// 简单的测试文件，用于验证TypeScript配置
import { createApp } from 'vue'
import ElementPlus from 'element-plus'

console.log('TypeScript配置测试')
console.log('Element Plus版本:', (ElementPlus as any).version)

// 测试Vue应用创建
const app = createApp({
  template: '<div>测试应用</div>'
})

console.log('Vue应用创建成功')