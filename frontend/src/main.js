// 1. 导入 Vue 的 createApp 函数
import { createApp } from 'vue'

// 2. 导入全局样式（Tailwind CSS）
import './style.css'

// 3. 导入根组件 App.vue
import App from './App.vue'

// 4. 创建 Vue 应用实例
const app = createApp(App)

// 5. 将应用挂载到 HTML 中的 #app 元素上
app.mount('#app')

