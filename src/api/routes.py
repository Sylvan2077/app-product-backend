# src/api/routes.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import distinct
import json
import zipfile
import os
from datetime import datetime
from src import models, schemas, database
from typing import List, Optional

router = APIRouter()

# --- 依赖项 ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 辅助函数 ---
def get_static_url(relative_path: str) -> str:
    """将相对路径转换为静态文件URL"""
    if relative_path:
        return f"/static/{relative_path}"
    return ""

# --- API 路由 ---

@router.get("/products", response_model=List[schemas.Module])
async def get_products(industry: Optional[str] = None, subject: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Module)
    if industry:
        query = query.filter(models.Module.industry == industry)
    if subject:
        query = query.filter(models.Module.subject == subject)

    modules = query.all()
    # 转换 image_url 为完整的静态 URL
    for mod in modules:
        mod.image_url = get_static_url(mod.image_url)
    return modules

@router.get("/products/{id}", response_model=schemas.Module)
async def get_product(id: int, db: Session = Depends(get_db)):
    module = db.query(models.Module).filter(models.Module.id == id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    module.image_url = get_static_url(module.image_url)
    return module

@router.get("/industries")
async def get_industries(db: Session = Depends(get_db)):
    industries = db.query(distinct(models.Module.industry)).all()
    return [{"name": ind[0]} for ind in industries if ind[0]] # 过滤掉 None 值

@router.get("/modules")
async def get_modules(db: Session = Depends(get_db)):
    subjects = db.query(distinct(models.Module.subject)).all()
    return [{"name": sub[0]} for sub in subjects if sub[0]] # 过滤掉 None 值

@router.get("/cases", response_model=List[schemas.Case])
async def get_cases(db: Session = Depends(get_db)):
    cases = db.query(models.Case).all()
    for case in cases:
        case.image_url = get_static_url(case.image_url)
    return cases

@router.get("/partners", response_model=List[schemas.Partner])
async def get_partners(db: Session = Depends(get_db)):
    partners = db.query(models.Partner).all()
    for partner in partners:
        partner.logo_url = get_static_url(partner.logo_url)
    return partners

@router.get("/banner", response_model=schemas.BannerInfo)
async def get_banner():
    # 假设 banner 信息是固定的，或从数据库中某个特定记录获取
    # 这里使用示例数据
    return schemas.BannerInfo(
        title="铸软件基石 擎装备重器",
        subtitle="致力于成为xxxxxxxxxx",
        img="/static/banner.jpg" # 直接返回静态路径
    )

@router.get("/footer", response_model=schemas.FooterInfo)
async def get_footer():
    # 假设版本信息是固定的，或从配置文件获取
    return schemas.FooterInfo(
        message="成功",
        version="v0.0.1"
    )

@router.post("/import", response_model=schemas.ImportResponse)
async def import_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(('.json')):
         raise HTTPException(status_code=400, detail="Only JSON files are allowed")

    try:
        contents = await file.read()
        data = json.loads(contents.decode('utf-8'))

        # 开始数据库事务
        db.begin()
        try:
            # 清空现有数据 (全量导入)
            db.query(models.Module).delete()
            db.query(models.Partner).delete()
            db.query(models.Client).delete()
            db.query(models.Case).delete()

            # 插入新数据
            modules_data = data.get('modules', [])
            partners_data = data.get('partners', [])
            clients_data = data.get('clients', [])
            cases_data = data.get('cases', [])

            for mod_data in modules_data:
                mod = models.Module(**mod_data)
                db.add(mod)
            for partner_data in partners_data:
                partner = models.Partner(**partner_data)
                db.add(partner)
            for client_data in clients_data:
                client = models.Client(**client_data)
                db.add(client)
            for case_data in cases_data:
                case = models.Case(**case_data)
                db.add(case)

            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

        return schemas.ImportResponse(
            message="数据导入成功",
            filename=file.filename
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export", response_model=schemas.ExportResponse)
async def export_data(db: Session = Depends(get_db)):
    # 获取所有数据
    modules = db.query(models.Module).all()
    partners = db.query(models.Partner).all()
    clients = db.query(models.Client).all()
    cases = db.query(models.Case).all()

    # 转换为字典列表，并移除静态 URL 前缀，只保留相对路径用于导出
    def remove_static_prefix(item):
        if hasattr(item, 'image_url') and item.image_url:
            item.image_url = item.image_url.replace('/static/', '', 1)
        if hasattr(item, 'logo_url') and item.logo_url:
            item.logo_url = item.logo_url.replace('/static/', '', 1)
        return item

    export_data = {
        "modules": [remove_static_prefix(m).__dict__ for m in modules],
        "partners": [remove_static_prefix(p).__dict__ for p in partners],
        "clients": [c.__dict__ for c in clients],
        "cases": [remove_static_prefix(ca).__dict__ for ca in cases]
    }
    # 移除 SQLAlchemy 添加的特殊属性
    for category in export_data.values():
        for item in category:
            item.pop('_sa_instance_state', None)


    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"product_library_export_{timestamp}.json"

    # 写入 JSON 文件
    filepath = os.path.join("exports", filename) # 假设有一个 exports 目录
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    # TODO: 如果需要打包静态文件，可以在这里创建 ZIP
    # zip_filename = f"product_library_export_{timestamp}.zip"
    # with zipfile.ZipFile(zip_filename, 'w') as zipf:
    #     zipf.write(filepath, os.path.basename(filepath))
    #     # 添加静态文件目录 (需要遍历 static 目录)
    #     # for root, dirs, files in os.walk("static"):
    #     #     for file in files:
    #     #         zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(os.getcwd())))

    return schemas.ExportResponse(
        code=200,
        msg="导出成功",
        filename=filename # 这里返回文件名，实际应用中可能需要提供下载链接
    )
