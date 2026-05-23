# 1. 导入需要的模块
from pydantic import BaseModel
from typing import List, Optional

# 2. 定义聊天请求 Schema（前端发送给后端的数据格式）
class ChatRequest(BaseModel):
    session_id: Optional[str] = None  # 会话ID（可选，新建会话时不需要）
    content: str  # 用户输入的内容（必填）
    style: str  # 回复风格（必填）
    persona: Optional[str] = None  # 人设（新建会话时需要）
    name: Optional[str] = None  # 对方昵称（新建会话时需要）

# 3. 定义聊天响应 Schema（后端返回给前端的数据格式）
class ChatResponse(BaseModel):
    emotion: str  # AI识别的情绪
    strategy: str  # AI建议的沟通策略
    replies: List[str]  # 生成的回复列表

# 4. 定义会话创建请求 Schema
class SessionCreate(BaseModel):
    name: str  # 对方昵称（必填）
    persona: str  # 人设标签（必填）
    style: Optional[str] = "warm"  # 默认风格（可选，默认为 warm）

# 5. 定义会话响应 Schema
class SessionResponse(BaseModel):
    id: str  # 会话ID
    name: str  # 对方昵称
    persona: str  # 人设标签
    style: str  # 默认风格
    created_at: str  # 创建时间
    updated_at: str  # 更新时间
