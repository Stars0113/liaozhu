# 1. 导入需要的模块
from sqlalchemy import Column, String, DateTime, ForeignKey
from datetime import datetime
from database import Base


# 2. 定义消息模型（对应数据库中的 messages 表）
class Message(Base):
    __tablename__ = "messages"  # 数据库表名

    # 字段定义
    id = Column(String, primary_key=True, index=True)  # 唯一标识
    session_id = Column(String, ForeignKey("sessions.id"))  # 关联的会话ID
    role = Column(String)  # 角色：user（用户）/ assistant（AI）
    content = Column(String)  # 消息内容
    emotion = Column(String)  # AI识别的情绪
    strategy = Column(String)  # AI建议的策略
    style_tag = Column(String)  # 回复风格标签
    feedback = Column(String)  # 用户反馈：good / bad / null
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间

