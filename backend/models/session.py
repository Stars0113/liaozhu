# 1. 导入需要的模块
from sqlalchemy import Column, String, DateTime
from datetime import datetime
from database import Base  # 从刚才写的 database.py 导入基类


# 2. 定义会话模型（对应数据库中的 sessions 表）
class Session(Base):
    __tablename__ = "sessions"  # 数据库表名

    # 字段定义
    id = Column(String, primary_key=True, index=True)  # 唯一标识（UUID）
    name = Column(String, index=True)  # 对方昵称
    persona = Column(String)  # 人设标签：crush / pursuer / friend / elder
    style = Column(String)  # 默认回复风格
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow)  # 更新时间
