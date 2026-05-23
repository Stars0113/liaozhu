<template>
  <!-- 外层容器，最小高度占满屏幕 -->
  <div class="min-h-screen bg-gray-100">

    <!-- 条件渲染：如果没有选中会话，显示会话列表 -->
    <SessionList
      v-if="!currentSession"
      @select="openChat"
      @create="createSession"
    />

    <!-- 条件渲染：如果选中了会话，显示聊天窗口 -->
    <ChatWindow
      v-else
      :session="currentSession"
      @back="currentSession = null"
    />
  </div>
</template>

<script setup>
// 1. 导入 Vue 的 ref 响应式函数
import { ref } from 'vue'

// 2. 导入页面组件
import SessionList from './views/SessionList.vue'
import ChatWindow from './views/ChatWindow.vue'

// 3. 定义响应式状态：当前选中的会话
const currentSession = ref(null)

// 4. 定义方法：打开聊天窗口
const openChat = (session) => {
  currentSession.value = session
}

// 5. 定义方法：创建会话后打开聊天窗口
const createSession = (session) => {
  currentSession.value = session
}
</script>
