<template>
  <!-- 页面容器 -->
  <div class="min-h-screen bg-gray-100 flex flex-col">

    <!-- 顶部导航栏 -->
    <header class="bg-white shadow-sm flex items-center justify-between px-4 py-3">
      <!-- 返回按钮 -->
      <button
        @click="$emit('back')"
        class="flex items-center gap-2 text-gray-600 hover:text-gray-800"
      >
        ← 返回
      </button>

      <!-- 会话信息 -->
      <div class="text-center">
        <h2 class="font-medium text-gray-800">{{ session.name }}</h2>
        <p class="text-xs text-gray-500">{{ getPersonaLabel(session.persona) }}</p>
      </div>

      <!-- 占位（保持布局对称） -->
      <div class="w-16"></div>
    </header>

    <!-- 消息列表 -->
    <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
      <!-- 空状态 -->
      <div v-if="messages.length === 0" class="text-center py-12">
        <div class="text-6xl mb-4">💬</div>
        <p class="text-gray-500">开始聊天吧！</p>
      </div>

      <!-- 消息列表项 -->
      <div v-for="message in messages" :key="message.id">
        <!-- 用户消息 -->
        <div v-if="message.role === 'user'" class="flex justify-end">
          <div class="max-w-xs md:max-w-md bg-gradient-to-r from-purple-500 to-pink-500 text-white p-3 rounded-xl rounded-tr-sm">
            {{ message.content }}
          </div>
        </div>

        <!-- AI 回复 -->
        <div v-else class="flex justify-start">
          <div class="max-w-xs md:max-w-md bg-white p-3 rounded-xl rounded-tl-sm shadow-sm">
            <!-- 情绪和策略 -->
            <div v-if="message.emotion || message.strategy" class="mb-2">
              <div class="flex items-center gap-2 text-xs text-gray-500">
                <span>⚠️ {{ message.emotion }}</span>
              </div>
              <div class="text-xs text-gray-600 mt-1">
                💡 {{ message.strategy }}
              </div>
            </div>

            <!-- 回复内容 -->
            {{ message.content }}

            <!-- 反馈按钮 -->
            <div class="flex gap-2 mt-2">
              <button
                @click="sendFeedback(message.id, 'good')"
                class="text-xs text-green-500 hover:text-green-600"
              >
                👍 好用
              </button>
              <button
                @click="sendFeedback(message.id, 'bad')"
                class="text-xs text-red-500 hover:text-red-600"
              >
                👎 不好用
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="flex justify-center">
        <div class="animate-spin rounded-full h-6 w-6 border-2 border-purple-500 border-t-transparent"></div>
      </div>
    </div>

    <!-- 风格选择器 -->
    <div class="bg-white border-t p-3">
      <div class="flex gap-2 overflow-x-auto pb-2">
        <button
          v-for="style in styles"
          :key="style.value"
          @click="selectedStyle = style.value"
          :class="[
            'px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all',
            selectedStyle === style.value
              ? 'bg-purple-500 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          ]"
        >
          {{ style.label }}
        </button>
      </div>
    </div>

    <!-- 输入框区域 -->
    <div class="bg-white border-t p-4">
      <div class="flex gap-3">
        <!-- 图片上传按钮 -->
        <button
          @click="uploadImage"
          class="w-10 h-10 flex items-center justify-center rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
        >
          📷
        </button>

        <!-- 文字输入框 -->
        <input
          ref="inputRef"
          v-model="inputContent"
          type="text"
          placeholder="输入对方发来的消息..."
          @keyup.enter="sendMessage"
          class="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-purple-500"
        />

        <!-- 发送按钮 -->
        <button
          @click="sendMessage"
          :disabled="!inputContent.trim() || loading"
          :class="[
            'w-10 h-10 flex items-center justify-center rounded-full transition-all',
            inputContent.trim() && !loading
              ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          ]"
        >
          →
        </button>
      </div>

      <!-- 隐藏的文件选择器 -->
      <input
        ref="fileInputRef"
        type="file"
        accept="image/*"
        class="hidden"
        @change="handleImageUpload"
      />
    </div>
  </div>
</template>

<script setup>
// 1. 导入需要的模块和 API
import { ref, onMounted, nextTick, watch } from 'vue'
import { chatAPI } from '../api/index.js'

// 2. 定义 props（从父组件接收的数据）
const props = defineProps({
  session: {
    type: Object,
    required: true
  }
})

// 3. 定义事件发射器
defineEmits(['back'])

// 4. 定义响应式状态
const messages = ref([])           // 消息列表
const inputContent = ref('')       // 输入框内容
const selectedStyle = ref('warm')  // 当前选择的风格
const loading = ref(false)         // 加载状态
const messagesContainer = ref(null) // 消息容器引用
const inputRef = ref(null)          // 输入框引用
const fileInputRef = ref(null)      // 文件选择器引用

// 5. 风格配置
const styles = [
  { value: 'warm', label: '🟢 热情主动' },
  { value: 'cute', label: '🟡 俏皮暧昧' },
  { value: 'sincere', label: '🔵 稳重真诚' },
  { value: 'playful', label: '🟣 欲擒故纵' },
  { value: 'cold', label: '⚪ 冷淡疏离' }
]

// 6. 人设标签配置
const personaLabels = {
  crush: '💕 Crush',
  pursuer: '💘 追求者',
  friend: '👫 朋友',
  elder: '👴 长辈'
}

// 7. 辅助函数：获取人设标签的显示文本
const getPersonaLabel = (value) => {
  return personaLabels[value] || value
}

// 8. 滚动到消息底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 9. 加载消息历史
const loadMessages = async () => {
  try {
    const response = await chatAPI.getMessages(props.session.id)
    messages.value = response.data
    scrollToBottom()
  } catch (error) {
    console.error('加载消息失败:', error)
  }
}

// 10. 发送文字消息
const sendMessage = async () => {
  if (!inputContent.value.trim() || loading.value) return

  loading.value = true

  try {
    // 调用聊天 API
    const response = await chatAPI.chat({
      session_id: props.session.id,
      content: inputContent.value,
      style: selectedStyle.value
    })

    // 添加用户消息到列表
    messages.value.push({
      id: Date.now().toString(),
      role: 'user',
      content: inputContent.value
    })

    // 添加 AI 回复到列表
    response.data.replies.forEach(reply => {
      messages.value.push({
        id: (Date.now() + Math.random()).toString(),
        role: 'assistant',
        content: reply,
        emotion: response.data.emotion,
        strategy: response.data.strategy,
        style_tag: selectedStyle.value
      })
    })

    // 清空输入框
    inputContent.value = ''

    // 滚动到底部
    scrollToBottom()
  } catch (error) {
    console.error('发送消息失败:', error)
  } finally {
    loading.value = false
  }
}

// 11. 发送反馈
const sendFeedback = async (messageId, feedback) => {
  try {
    // 这里可以实现反馈逻辑
    console.log('反馈:', messageId, feedback)
    alert(feedback === 'good' ? '感谢你的好评！' : '感谢你的反馈，我们会继续改进！')
  } catch (error) {
    console.error('发送反馈失败:', error)
  }
}

// 12. 触发图片上传
const uploadImage = () => {
  fileInputRef.value?.click()
}

// 13. 处理图片上传
const handleImageUpload = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  loading.value = true

  try {
    // 创建 FormData
    const formData = new FormData()
    formData.append('session_id', props.session.id)
    formData.append('style', selectedStyle.value)
    formData.append('image', file)

    // 调用图片聊天 API
    const response = await chatAPI.chatWithImage(formData)

    // 添加图片消息到列表
    messages.value.push({
      id: Date.now().toString(),
      role: 'user',
      content: '[图片]'
    })

    // 添加 AI 回复到列表
    response.data.replies.forEach(reply => {
      messages.value.push({
        id: (Date.now() + Math.random()).toString(),
        role: 'assistant',
        content: reply,
        emotion: response.data.emotion,
        strategy: response.data.strategy,
        style_tag: selectedStyle.value
      })
    })

    scrollToBottom()
  } catch (error) {
    console.error('图片上传失败:', error)
  } finally {
    loading.value = false
    event.target.value = ''  // 重置文件选择器
  }
}

// 14. 组件挂载时加载消息
onMounted(() => {
  loadMessages()
})

// 15. 监听会话变化，重新加载消息
watch(() => props.session.id, loadMessages)
</script>
