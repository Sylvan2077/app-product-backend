# src/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.api import routes
from src.database import engine, Base
import os

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Product Library API", version="0.0.1")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 包含 API 路由
app.include_router(routes.router, prefix="/api", tags=["api"])

# 可选：根路径
@app.get("/")
def read_root():
    return {"message": "Welcome to Product Library Backend API", "version": "0.0.1"}

# 可选：健康检查
@app.get("/health")
def health_check():
    return {"status": "healthy"}
