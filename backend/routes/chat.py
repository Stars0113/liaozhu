# 1. 导入需要的模块
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
from database import get_db
from models.session import Session as SessionModel
from models.message import Message as MessageModel
from schemas.chat import ChatRequest, ChatResponse
from services.ai_service import generate_response

# 2. 创建路由对象
router = APIRouter()


# 3. 发送消息并获取 AI 回复
@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    发送消息并获取 AI 生成的回复

    - 如果没有 session_id，会自动创建新会话
    - 需要提供 name 和 persona（新建会话时）
    """

    # 处理会话逻辑
    if not request.session_id:
        # 新建会话
        if not request.name or not request.persona:
            raise HTTPException(status_code=400, detail="新建会话需要提供 name 和 persona")

        # 创建新会话
        new_session = SessionModel(
            id=str(uuid4()),
            name=request.name,
            persona=request.persona,
            style=request.style,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        session_id = new_session.id
        persona = request.persona
    else:
        # 使用现有会话
        session = db.query(SessionModel).filter(SessionModel.id == request.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        session_id = request.session_id
        persona = session.persona

    # 获取历史消息
    history = db.query(MessageModel).filter(MessageModel.session_id == session_id).order_by(
        MessageModel.created_at).all()
    chat_history = [{"role": m.role, "content": m.content} for m in history]

    # 调用 AI 生成回复
    result = generate_response(request.content, request.style, persona, chat_history)

    # 保存用户消息到数据库
    user_message = MessageModel(
        id=str(uuid4()),
        session_id=session_id,
        role="user",
        content=request.content,
        created_at=datetime.utcnow()
    )
    db.add(user_message)

    # 保存 AI 回复到数据库
    for reply in result["replies"]:
        ai_message = MessageModel(
            id=str(uuid4()),
            session_id=session_id,
            role="assistant",
            content=reply,
            emotion=result["emotion"],
            strategy=result["strategy"],
            style_tag=request.style,
            created_at=datetime.utcnow()
        )
        db.add(ai_message)

    # 更新会话的更新时间
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    session.updated_at = datetime.utcnow()

    # 提交所有数据库操作
    db.commit()

    return result


# 4. 获取会话的消息历史
@router.get("/chat/{session_id}")
def get_messages(session_id: str, db: Session = Depends(get_db)):
    """获取指定会话的所有消息记录"""
    messages = db.query(MessageModel).filter(MessageModel.session_id == session_id).order_by(
        MessageModel.created_at).all()

    # 格式化返回数据
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "emotion": m.emotion,
            "strategy": m.strategy,
            "style_tag": m.style_tag,
            "created_at": m.created_at.isoformat()
        } for m in messages
    ]

