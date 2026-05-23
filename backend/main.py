# 1. 导入需要的模块
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models.session import Base
from routes import session, chat

# 2. 创建数据库表（如果不存在）
Base.metadata.create_all(bind=engine)

# 3. 创建 FastAPI 应用实例
app = FastAPI(
    title="聊助 API",
    description="聊天提示生成器的后端 API",
    version="1.0"
)

# 4. 配置 CORS（跨域资源共享）
# 允许前端访问后端 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（生产环境应限制具体域名）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 5. 注册路由
app.include_router(session.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

# 6. 健康检查接口
@app.get("/")
def read_root():
    """健康检查接口"""
    return {"message": "欢迎使用聊助 API"}

# 7. 启动应用（开发模式）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 开发模式下自动重启
    )