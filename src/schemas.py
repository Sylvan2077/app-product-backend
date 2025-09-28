# src/schemas.py
from pydantic import BaseModel
from typing import List, Optional

# --- Module Schemas ---
class ModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: str
    industry: str
    subject: str

class Module(ModuleBase):
    id: int
    class Config:
        from_attributes = True # 允许从 ORM 对象创建 Pydantic 模型

# --- Partner Schemas ---
class PartnerBase(BaseModel):
    name: str
    logo_url: str

class Partner(PartnerBase):
    id: int
    class Config:
        from_attributes = True

# --- Client Schemas ---
class ClientBase(BaseModel):
    type: str
    name: str
    value: str

class Client(ClientBase):
    id: int
    class Config:
        from_attributes = True

# --- Case Schemas ---
class CaseBase(BaseModel):
    image_url: str
    case: str
    value: str

class Case(CaseBase):
    id: int
    class Config:
        from_attributes = True

# --- Banner Schemas ---
class BannerInfo(BaseModel):
    title: str
    subtitle: str
    img: str

# --- Footer Schemas ---
class FooterInfo(BaseModel):
    message: str
    version: str

# --- Import/Export Schemas ---
class ExportData(BaseModel):
    modules: List[Module]
    partners: List[Partner]
    clients: List[Client]
    cases: List[Case]
    # banner: BannerInfo # 如果 banner 信息也需要导出
    # footer: FooterInfo # 如果 footer 信息也需要导出

class ImportResponse(BaseModel):
    message: str
    filename: str

class ExportResponse(BaseModel):
    code: int
    msg: str
    filename: str