# 1. 导入需要的模块
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 2. 数据库连接地址（SQLite 文件数据库）
SQLALCHEMY_DATABASE_URL = "sqlite:///./liaozhu.db"

# 3. 创建数据库引擎（相当于连接数据库）
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # SQLite 需要这个参数
)

# 4. 创建会话工厂（每次操作数据库都需要一个 session）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. 创建基类（所有数据模型都要继承这个类），SQLAlchemy 会自动管理表结构
Base = declarative_base()

# 6. 定义依赖函数（供 FastAPI 使用）
# 依赖注入函数，FastAPI 会自动调用它获取数据库连接
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()