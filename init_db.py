# init_db.py
# 运行此脚本以初始化数据库并从JSON文件导入数据
import json
import os
from src.database import SessionLocal, engine
from src.models import Base, Module, Partner, Client, Case, Banner

# 创建表结构
def init_db():
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 处理数据导入
        import_data(db)
        db.commit()
        print("数据库初始化成功")
    except Exception as e:
        print(f"初始化数据库时出错: {str(e)}")
        db.rollback()
    finally:
        db.close()

# 导入数据函数
def import_data(db):
    json_file_path = "data.json"
    
    # 检查JSON文件是否存在
    if not os.path.exists(json_file_path):
        print("使用默认示例数据初始化数据库")
        import_default_data(db)
        return
    
    # 从JSON文件读取数据
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print(f"从 {json_file_path} 文件读取数据并导入数据库")
    
    # 处理不同类型的数据
    models = [
        # 模型类, 数据键名, 路径字段, 路径前缀
        (Module, "modules", "image_url", "images/"),
        (Partner, "partners", "logo_url", "images/"),
        (Banner, "banners", "img", "images/")
    ]
    
    # 处理常规模型数据
    for Model, key, path_field, prefix in models:
        process_and_add_data(db, data, Model, key, path_field, prefix)
    
    # 特殊处理categories数据转换为Client模型
    process_clients_data(db, data)

# 处理并添加数据（以id为唯一标识符）
def process_and_add_data(db, data, Model, data_key, path_field, prefix):
    added_count = 0
    skipped_count = 0
    
    for item_data in data.get(data_key, []):
        # 添加前缀到路径字段
        if path_field in item_data and not item_data[path_field].startswith(prefix):
            item_data[path_field] = f"{prefix}{item_data[path_field]}"
        
        # 获取item_data中的id
        item_id = item_data.get("id")
        
        # 检查数据是否已存在
        if item_id is not None:
            # 以id作为唯一标识符检查数据是否已存在
            existing_item = db.query(Model).filter(Model.id == item_id).first()
            if existing_item:
                print(f"跳过已存在的数据（ID: {item_id}，模型: {Model.__name__}）")
                skipped_count += 1
                continue
        
        # 移除id字段，使用数据库自增主键
        item_data.pop("id", None)
        
        # 添加新数据
        new_item = Model(**item_data)
        db.add(new_item)
        added_count += 1
        
    print(f"{Model.__name__}数据处理完成：添加 {added_count} 条，跳过 {skipped_count} 条")

# 处理客户端数据（categories转换为Client）
def process_clients_data(db, data):
    added_count = 0
    skipped_count = 0
    
    for category_data in data.get("categories", []):
        client_data = {
            "type": category_data.get("type", "category"),
            "name": category_data.get("name", ""),
            "value": category_data.get("value", "")
        }
        
        # 获取category_data中的id
        item_id = category_data.get("id")
        
        # 检查数据是否已存在
        if item_id is not None:
            # 以id作为唯一标识符检查数据是否已存在
            existing_client = db.query(Client).filter(Client.id == item_id).first()
            if existing_client:
                print(f"跳过已存在的客户端数据（ID: {item_id}）")
                skipped_count += 1
                continue
        
        # 移除id字段，使用数据库自增主键
        category_data.pop("id", None)
        
        # 添加新数据
        new_client = Client(**client_data)
        db.add(new_client)
        added_count += 1
        
    print(f"Client数据处理完成：添加 {added_count} 条，跳过 {skipped_count} 条")

# 导入默认示例数据
def import_default_data(db):
    # 默认示例数据没有指定id，所以直接添加
    module1 = Module(title="茉莉平台 结构振动仿真模块", description="用于结构振动特性的精确分析", 
                     image_url="images/modules/struct.png", industry="航空", subject="结构仿真模块")
    module2 = Module(title="茉莉平台 流体振动仿真模块", description="用于流体振动特性的精确分析", 
                     image_url="images/modules/fluid.png", industry="船舶", subject="流体仿真模块")
    partner1 = Partner(name="HUAWEI", logo_url="images/partners/huawei.png")
    client1 = Client(type="合作单位", name="Example Corp", value="Key Client")
    case1 = Case(image_url="images/cases/case1.jpg", case="航空发动机振动分析", value="成功案例")
    
    # 检查这些默认数据是否已存在（使用标题/名称等作为标识）
    default_items = [
        (Module, module1, "title", module1.title),
        (Module, module2, "title", module2.title),
        (Partner, partner1, "name", partner1.name),
        (Client, client1, "name", client1.name),
        (Case, case1, "case", case1.case)
    ]
    
    items_to_add = []
    for Model, item, field_name, field_value in default_items:
        # 构建查询条件
        query = db.query(Model)
        filter_expr = getattr(Model, field_name) == field_value
        existing_item = query.filter(filter_expr).first()
        
        if not existing_item:
            items_to_add.append(item)
            print(f"添加默认数据：{Model.__name__} - {field_value}")
        else:
            print(f"跳过已存在的默认数据：{Model.__name__} - {field_value}")
    
    if items_to_add:
        db.add_all(items_to_add)
        print(f"共添加 {len(items_to_add)} 条默认数据")

# 执行初始化
if __name__ == "__main__":
    init_db()