from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime
import os
import base64
import requests  # ← 添加这个
from database import get_db
from models.session import Session as SessionModel
from models.message import Message as MessageModel
from schemas.chat import ChatRequest, ChatResponse
from services.ai_service import generate_response, safe_parse_json

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

# 图片聊天接口
@router.post("/chat/image")
async def chat_with_image(
        session_id: str = None,
        style: str = "warm",
        persona: str = None,
        name: str = None,
        image: UploadFile = File(...)
):
    """
    通过图片进行聊天（直接分析图片内容并生成回复）

    参数：
    - session_id: 会话ID（可选）
    - style: 回复风格
    - persona: 人设（新建会话时需要）
    - name: 对方昵称（新建会话时需要）
    - image: 图片文件
    """
    db = next(get_db())  # 获取数据库连接

    # 1. 处理会话逻辑
    if not session_id:
        if not name or not persona:
            raise HTTPException(status_code=400, detail="新建会话需要提供 name 和 persona")

        # 创建新会话
        new_session = SessionModel(
            id=str(uuid4()),
            name=name,
            persona=persona,
            style=style,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        session_id = new_session.id
    else:
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        persona = session.persona

    # 2. 处理图片上传
    allowed_extensions = [".jpg", ".jpeg", ".png"]
    file_ext = os.path.splitext(image.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="只支持 jpg、png 格式的图片")

    # 3. 读取图片并编码为 Base64
    contents = await image.read()
    image_base64 = base64.b64encode(contents).decode("utf-8")

    # 4. 调用千问多模态 API
    headers = {
        "Authorization": f"Bearer {os.getenv('DASHSCOPE_API_KEY')}",
        "Content-Type": "application/json"
    }

    system_prompt = f"""你是聊天回复助手"聊助"。当前关系：{persona}。

分析图片中的聊天内容，然后：
1. 判断对方消息中的情绪状态
2. 给出沟通策略建议
3. 根据【{style}】风格生成3条回复选项

输出格式（JSON）：
{{
"emotion": "情绪判断",
"strategy": "建议策略",
"replies": ["回复1", "回复2", "回复3"]
}}

注意：只输出 JSON 格式，不要有其他任何文字。"""

    data = {
        "model": "qwen-vl-plus",
        "input": {
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请分析这张图片中的聊天内容，生成回复建议"},
                        {"type": "image", "image": f"data:image/png;base64,{image_base64}"}
                    ]
                }
            ]
        },
        "parameters": {"temperature": 0.7}
    }

    response = requests.post(
        "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
        headers=headers,
        json=data
    )
    response.raise_for_status()
    result = response.json()

    # 5. 解析响应
    if (result.get("output") and
            result["output"].get("choices") and
            len(result["output"]["choices"]) > 0 and
            result["output"]["choices"][0].get("message") and
            result["output"]["choices"][0]["message"].get("content") and
            len(result["output"]["choices"][0]["message"]["content"]) > 0):

        content = result["output"]["choices"][0]["message"]["content"][0]["text"]

        # 安全解析 JSON
        parsed_result = safe_parse_json(content)
        if parsed_result and all(key in parsed_result for key in ["emotion", "strategy", "replies"]):
            # 保存到数据库
            # 保存用户消息（图片内容）
            user_message = MessageModel(
                id=str(uuid4()),
                session_id=session_id,
                role="user",
                content=f"[图片] {parsed_result.get('emotion', '')}",
                created_at=datetime.utcnow()
            )
            db.add(user_message)

            # 保存 AI 回复
            for reply in parsed_result["replies"]:
                ai_message = MessageModel(
                    id=str(uuid4()),
                    session_id=session_id,
                    role="assistant",
                    content=reply,
                    emotion=parsed_result["emotion"],
                    strategy=parsed_result["strategy"],
                    style_tag=style,
                    created_at=datetime.utcnow()
                )
                db.add(ai_message)

            # 更新会话时间
            session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
            session.updated_at = datetime.utcnow()

            db.commit()
            return parsed_result

    # 6. 返回默认值
    return {
        "emotion": "无法识别",
        "strategy": "保持友好",
        "replies": ["好的", "收到", "嗯嗯"]
    }