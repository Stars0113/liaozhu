// 1. 导入 axios（HTTP 客户端）
import axios from 'axios'

// 2. 创建 axios 实例，配置基础 URL
const api = axios.create({
  baseURL: '/api',  // 所有请求都会自动加上 /api 前缀
  timeout: 30000    // 请求超时时间（30秒）
})

// 3. 封装会话相关的 API
export const sessionAPI = {
  // 获取所有会话列表
  getSessions: () => api.get('/sessions'),

  // 创建新会话
  createSession: (data) => api.post('/sessions', data),

  // 获取单个会话详情
  getSession: (id) => api.get(`/sessions/${id}`),

  // 删除会话
  deleteSession: (id) => api.delete(`/sessions/${id}`)
}

// 4. 封装聊天相关的 API
export const chatAPI = {
  // 文字聊天
  chat: (data) => api.post('/chat', data),

  // 图片聊天（需要特殊处理文件上传）
  chatWithImage: (formData) => api.post('/chat/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),

  // 获取会话的消息历史
  getMessages: (sessionId) => api.get(`/chat/${sessionId}`)
}