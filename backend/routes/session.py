# 1. 导入需要的模块
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from database import get_db
from models.session import Session as SessionModel
from schemas.chat import SessionCreate, SessionResponse

# 2. 创建路由对象
router = APIRouter()

# 3. 获取所有会话列表
@router.get("/sessions", response_model=list[SessionResponse])
def get_sessions(db: Session = Depends(get_db)):
    """获取所有会话列表（按更新时间倒序）"""
    sessions = db.query(SessionModel).order_by(SessionModel.updated_at.desc()).all()
    return sessions


# 4. 创建新会话
@router.post("/sessions", response_model=SessionResponse)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    """创建新的聊天会话"""
    # 生成唯一ID（UUID）
    new_session = SessionModel(
        id=str(uuid4()),
        name=session.name,
        persona=session.persona,
        style=session.style or "warm",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # 保存到数据库
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session


# 5. 获取单个会话详情
@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """获取指定会话的详情"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    return session


# 6. 删除会话
@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """删除指定会话"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    db.delete(session)
    db.commit()

    return {"message": "会话删除成功"}
