# init_db.py
# 运行此脚本以初始化数据库并添加示例数据
from src.database import SessionLocal, engine
from src.models import Base, Module, Partner, Client, Case

# 创建表
Base.metadata.create_all(bind=engine)

# 获取数据库会话
db = SessionLocal()

try:
    # 检查是否有数据，避免重复初始化
    if db.query(Module).first() is None:
        # 添加示例数据
        module1 = Module(
            title="茉莉平台 结构振动仿真模块",
            description="用于结构振动特性的精确分析",
            image_url="images/modules/struct.png", # 相对路径
            industry="航空",
            subject="结构仿真模块"
        )
        module2 = Module(
            title="茉莉平台 流体振动仿真模块",
            description="用于流体振动特性的精确分析",
            image_url="images/modules/fluid.png", # 相对路径
            industry="船舶",
            subject="流体仿真模块"
        )
        partner1 = Partner(
            name="HUAWEI",
            logo_url="images/partners/huawei.png" # 相对路径
        )
        client1 = Client(type="合作单位", name="Example Corp", value="Key Client")
        case1 = Case(image_url="images/cases/case1.jpg", case="航空发动机振动分析", value="成功案例")

        db.add_all([module1, module2, partner1, client1, case1])
        db.commit()
        print("Database initialized with sample data.")
    else:
        print("Database already has data, skipping initialization.")

finally:
    db.close()
