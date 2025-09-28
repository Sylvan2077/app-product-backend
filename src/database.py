# src/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite 数据库 URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./product_library.db"

# 创建引擎，使用 aiosqlite 以支持异步操作（虽然 FastAPI 0.104 中 SQLAlchemy 的异步支持有限，但这是推荐方式）
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} # SQLite 特定参数
)

# 创建本地会话类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基础类，其他模型将继承它
Base = declarative_base()

def get_db():
    """
    依赖项，用于获取数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
