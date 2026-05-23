<template>
  <!-- 页面容器 -->
  <div class="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50">

    <!-- 头部区域 -->
    <header class="bg-white shadow-sm">
      <div class="max-w-md mx-auto px-4 py-4">
        <h1 class="text-2xl font-bold text-gray-800">聊助</h1>
        <p class="text-sm text-gray-500 mt-1">让每一次回复，都恰到好处</p>
      </div>
    </header>

    <!-- 新建会话按钮 -->
    <div class="max-w-md mx-auto px-4 py-4">
      <button
        @click="showCreateModal = true"
        class="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 px-4 rounded-xl font-medium shadow-lg hover:shadow-xl transition-all"
      >
        + 新建会话
      </button>
    </div>

    <!-- 会话列表 -->
    <div class="max-w-md mx-auto px-4">
      <!-- 空状态 -->
      <div v-if="sessions.length === 0" class="text-center py-12">
        <div class="text-6xl mb-4">💬</div>
        <p class="text-gray-500">还没有会话，点击上方按钮开始</p>
      </div>

      <!-- 会话列表项 -->
      <div v-else class="space-y-3">
        <div
          v-for="session in sessions"
          :key="session.id"
          @click="$emit('select', session)"
          class="bg-white p-4 rounded-xl shadow-sm hover:shadow-md cursor-pointer transition-all border border-gray-100"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <!-- 用户头像（使用昵称首字母） -->
              <div class="w-10 h-10 rounded-full bg-gradient-to-r from-purple-400 to-pink-400 flex items-center justify-center text-white font-medium">
                {{ session.name.charAt(0) }}
              </div>
              <div>
                <h3 class="font-medium text-gray-800">{{ session.name }}</h3>
                <p class="text-xs text-gray-500">{{ getPersonaLabel(session.persona) }}</p>
              </div>
            </div>
            <!-- 删除按钮 -->
            <button
              @click.stop="deleteSession(session.id)"
              class="text-gray-400 hover:text-red-500 transition-colors"
            >
              ✕
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建会话弹窗 -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl p-6 w-full max-w-sm">
        <h2 class="text-xl font-bold text-gray-800 mb-4">新建会话</h2>

        <div class="space-y-4">
          <!-- 昵称输入 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">对方昵称</label>
            <input
              v-model="newSession.name"
              type="text"
              placeholder="输入对方昵称"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <!-- 人设选择 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">人设标签</label>
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="persona in personas"
                :key="persona.value"
                @click="newSession.persona = persona.value"
                :class="[
                  'py-2 px-3 rounded-lg text-sm font-medium transition-all',
                  newSession.persona === persona.value
                    ? 'bg-purple-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                ]"
              >
                {{ persona.label }}
              </button>
            </div>
          </div>
        </div>

        <!-- 弹窗按钮 -->
        <div class="flex gap-3 mt-6">
          <button
            @click="showCreateModal = false"
            class="flex-1 py-2 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
          >
            取消
          </button>
          <button
            @click="createSession"
            :disabled="!newSession.name || !newSession.persona"
            :class="[
              'flex-1 py-2 px-4 rounded-lg font-medium transition-all',
              newSession.name && newSession.persona
                ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            ]"
          >
            创建
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 1. 导入需要的模块和 API
import { ref, onMounted } from 'vue'
import { sessionAPI } from '../api/index.js'

// 2. 定义事件发射器（用于与父组件通信）
const emit = defineEmits(['select', 'create'])

// 3. 定义响应式状态
const sessions = ref([])           // 会话列表
const showCreateModal = ref(false) // 是否显示新建会话弹窗
const newSession = ref({           // 新建会话表单数据
  name: '',
  persona: ''
})

// 4. 人设标签配置
const personas = [
  { value: 'crush', label: '💕 Crush' },
  { value: 'pursuer', label: '💘 追求者' },
  { value: 'friend', label: '👫 朋友' },
  { value: 'elder', label: '👴 长辈' }
]

// 5. 辅助函数：获取人设标签的显示文本
const getPersonaLabel = (value) => {
  const persona = personas.find(p => p.value === value)
  return persona ? persona.label : value
}

// 6. 加载会话列表
const loadSessions = async () => {
  try {
    const response = await sessionAPI.getSessions()
    sessions.value = response.data
  } catch (error) {
    console.error('加载会话失败:', error)
  }
}

// 7. 创建新会话
const createSession = async () => {
  if (!newSession.value.name || !newSession.value.persona) return

  try {
    const response = await sessionAPI.createSession({
      name: newSession.value.name,
      persona: newSession.value.persona,
      style: 'warm'
    })

    const session = response.data
    sessions.value.unshift(session)  // 添加到列表开头
    showCreateModal.value = false   // 关闭弹窗
    newSession.value = { name: '', persona: '' }  // 重置表单

    // 通知父组件创建成功
    emit('create', session)
  } catch (error) {
    console.error('创建会话失败:', error)
  }
}

// 8. 删除会话
const deleteSession = async (id) => {
  if (!confirm('确定要删除这个会话吗？')) return

  try {
    await sessionAPI.deleteSession(id)
    sessions.value = sessions.value.filter(s => s.id !== id)
  } catch (error) {
    console.error('删除会话失败:', error)
  }
}

// 9. 组件挂载时加载会话列表
onMounted(loadSessions)
</script>
