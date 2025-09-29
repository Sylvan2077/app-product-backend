# src/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from src.api import routes
from src.database import engine, Base
import os
from fastapi.middleware.cors import CORSMiddleware

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Product Library API", version="0.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或指定 ["http://localhost:5174"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

if __name__ == '__main__':
    name_app = os.path.splitext(os.path.basename(__file__))[0]
    uvicorn.run(app=f"{name_app}:app", host="0.0.0.0",port=8000)