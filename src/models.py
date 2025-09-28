# src/models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from src.database import Base

class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    image_url = Column(String(512))  # 存储相对路径，如 "modules/struct.png"
    industry = Column(String(50))    # 行业
    subject = Column(String(50))     # 模块

class Partner(Base):
    __tablename__ = "partners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    logo_url = Column(String(512))   # 存储相对路径，如 "partners/huawei.png"

class Client(Base): # 文档中叫 "合作单位表"，但示例是 clients，这里保持一致
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50))        # 类型 (e.g., 'partner', 'client')
    name = Column(String(100))       # 名称
    value = Column(String(100))      # 值 (可能用于关联或描述)

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(512))  # 案例图片相对路径
    case = Column(String(100))       # 案例名称
    value = Column(String(100))      # 案例描述或值

# 注意：文档中提到 "行业列表" 和 "模块列表"，这些可能是通过 Module 表的 industry 和 subject 字段动态获取的，
# 或者可以创建单独的 Industry 和 Subject 表。这里我们先假设它们来自 Module 表。