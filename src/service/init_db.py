# src/service/init_db.py
# 数据库初始化服务类
import json
import os
from src.database import SessionLocal, engine
from src.models import Base, Module, Partner, Client, Case, Banner, About, Contact
from src.utils.logger import setup_logger


class DatabaseImportData:
    """数据库初始化器类，用于初始化数据库并导入数据"""
    
    def __init__(self):
        """初始化数据库初始化器"""
        self.logger = setup_logger(__name__)
    
    def init_db(self, data):
        """
        初始化数据库并导入数据
        
        Args:
            data: 要导入的JSON数据字典
            
        Returns:
            None
        """
        # 创建数据库表
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        
        try:
            # 处理数据导入
            self.import_data(db, data)
            db.commit()
            self.logger.info("数据库初始化成功")
        except Exception as e:
            self.logger.error(f"初始化数据库时出错: {str(e)}")
            db.rollback()
            raise  # 重新抛出异常，让调用者知道发生了错误
        finally:
            db.close()
    
    def import_data(self, db, data):
        """
        导入数据到数据库
        
        Args:
            db: 数据库会话
            data: 要导入的JSON数据字典
            
        Returns:
            None
        """
        # 处理不同类型的数据
        models = [
            # 模型类, 数据键名, 路径字段, 路径前缀
            (Module, "modules", "image_url", "images/"),
            (Partner, "partners", "logo_url", "images/"),
            (Banner, "banners", "img", "images/"),
            (About, "about", "url", ""),
            (Contact, "contact", "url", "images/")
        ]
        
        # 处理常规模型数据
        for Model, key, path_field, prefix in models:
            self.process_and_add_data(db, data, Model, key, path_field, prefix)
        
        # 特殊处理categories数据转换为Client模型
        self.process_clients_data(db, data)
    
    def process_and_add_data(self, db, data, Model, data_key, path_field, prefix):
        """
        处理并添加数据到数据库（以id为唯一标识符）
        
        Args:
            db: 数据库会话
            data: 要导入的JSON数据字典
            Model: 模型类
            data_key: 数据在字典中的键名
            path_field: 路径字段名
            prefix: 路径前缀
            
        Returns:
            None
        """
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
                    self.logger.info(f"跳过已存在的数据（ID: {item_id}，模型: {Model.__name__}）")
                    skipped_count += 1
                    continue
            
            # 移除id字段，使用数据库自增主键
            item_data.pop("id", None)
            
            # 添加新数据
            new_item = Model(**item_data)
            db.add(new_item)
            added_count += 1
        
        self.logger.info(f"{Model.__name__}数据处理完成：添加 {added_count} 条，跳过 {skipped_count} 条")
    
    def process_clients_data(self, db, data):
        """
        处理客户端数据（categories转换为Client）
        
        Args:
            db: 数据库会话
            data: 要导入的JSON数据字典
            
        Returns:
            None
        """
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
                    self.logger.info(f"跳过已存在的客户端数据（ID: {item_id}）")
                    skipped_count += 1
                    continue
            
            # 移除id字段，使用数据库自增主键
            category_data.pop("id", None)
            
            # 添加新数据
            new_client = Client(**client_data)
            db.add(new_client)
            added_count += 1
        
        self.logger.info(f"Client数据处理完成：添加 {added_count} 条，跳过 {skipped_count} 条")