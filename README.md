# app-product-backend
产品库后端

# 后端开发方案（基于 FastAPI + Python）

## 一、技术选型
- 框架：FastAPI
- 语言：Python 3.8+
- 本地存储 + /static静态目录服务
- 数据存储：SQLite（开发/演示）
- 数据导入导出：JSON 文件

## 二、设计图
![alt text](<Untitled diagram _ Mermaid Chart-2025-09-23-081952-1.png>)

## 三、主要接口设计
1. 首页/产品页数据
- GET /api/products 获取所有产品（支持行业/模块筛选）
- GET /api/products/{id} 获取单个产品详情
- GET /api/industries 获取行业列表
- GET /api/modules 获取模块列表
- GET /api/cases 获取案例列表

接口返回示例：
- /api/products 返回：
```json
[
  {
    "id": 1,
    "title": "茉莉平台 结构振动仿真模块",
    "desc": "用于结构振动特性的精确分析",
    "industry": "航空",
    "module": "结构仿真模块",
    "img": "/static/products/1.jpg"
  },
    {
    "id": 2,
    "title": "茉莉平台 流体振动仿真模块",
    "desc": "用于流体振动特性的精确分析",
    "industry": "船舶",
    "module": "流体仿真模块",
    "img": "/static/products/1.jpg"
  },
  ...
]
```

2. 合作伙伴
- GET /api/partners 获取所有合作伙伴（含logo图片url）

接口返回示例：
- /api/partners 返回：
```json
[
  {
    "name": "HUAWEI",
    "logo": "/static/partners/huawei.png"
  },
  ...
]
```


3. 首页Banner/头图
- GET /api/banner 获取首页banner信息（图片、标题、描述等）

接口返回示例：
- /api/banner 返回：
```json
{
  "title": "铸软件基石 擎装备重器",
  "subtitle": "致力于成为xxxxxxxxxx",
  "img": "/static/banner.jpg"
}
```

4. 导入导出
- GET /api/export 导出所有数据为JSON，图片等打包成zip等格式

接口返回示例：
- /api/export 返回：
```json
{
  "code": 200,
  "msg": "导出成功",
  "filename": "product_library_export.json"
}
```

- POST /api/import 导入JSON等数据并覆盖/合并,后端解析并更新数据库，前端自动刷新

接口请求示例：
- /api/import 请求：
```json
{
    "file": "product_library_export.json"
}
```


接口返回示例:
- /api/import 返回：
```json
{
  "message": "数据导入成功",
  "filename": "product_library_export.json"
}
```


5. 其它
- GET /api/footer 获取底部版本等信息
接口返回示例:
- /api/footer 返回：
```json
{
  "message": "成功",
  "version": "v0.0.1"
}
```


##  四、数据库设计
预计所需：产品模块表、合作伙伴表、合作单位表、客户案例信息表等
```python
class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    image_url = Column(String(512))  
    industry = Column(String(50))    
    subject = Column(String(50))     

class Partner(Base):
    __tablename__ = "partners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    logo_url = Column(String(512))   

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50))        
    name = Column(String(100))       
    value = Column(String(100))

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(50))        
    case = Column(String(100))       
    value = Column(String(100))          
```

##  五、静态文件存放示例
- 模块图片 → static/images/modules/xxx.png
- 合作伙伴Logo → static/images/partners/xxx.png

- 前端访问路径示例：
```
http://localhost:8000/static/images/modules/struct.png
http://localhost:8000/static/images/partners/huawei.png
```

##  六、跨环境数据迁移
### 1. 请求接口  /api/export 
下载 如 product_library_export.json：


注意：
两个环境（源端 + 目标端）：
 - 使用相同的数据库结构（models.py 一致）
 - 静态资源目录结构一致（static/images/modules/, static/images/partners/）
 - 图片文件名一致（或手动同步图片）

 - 示例：导出的 JSON 数据结构
```json
{
  "modules": [
    {
      "id": 1,
      "title": "某平台 结构振动仿真模块",
      "description": "结构仿真核心模块",
      "image_url": "modules/struct.png",
      "industry": "aviation",
      "subject": "structure"
    }
  ],
  "partners": [
    {
      "id": 1,
      "name": "华为",
      "logo_url": "partners/huawei.png"
    }
  ],
  "categories": [
    {
      "id": 1,
      "type": "industry",
      "name": "航空",
      "value": "aviation"
    }
  ]
}
```


 - 静态文件调用脚本示例：
 ```
 zip -r static_images.zip static/images/
 ```

将该文件复制到目标服务器

### 2. 导入接口：调用 POST /api/import，上传json文件

接口响应：
```json
{
  "message": "数据导入成功",
  "filename": "product_library_export.json"
}
```
调用脚本解压静态文件示例：
```
unzip static_images.zip -d /path/to/backend/
```

导入方式：全量或增量
- 全量同步: 导入先清空所有表，再插入新数据
- 增量同步：模型中增加updated_at 时间戳（用于比对）
json文件增加updated_at字段，示例：
```json
{
  "modules": [
    {
      "id": 1,
      "title": "结构仿真模块",
      "updated_at": "2025-04-05T10:30:00"
    }
  ]
}
```
存在？ → 比较时间戳，决定是否更新

不存在？ → 直接插入

### 3. 其他方面

- 事务安全：当前导入在单个数据库事务中完成，失败会回滚

- 前端配合（如需要该功能需要权限控制）

导出：直接下载 product_library_export.json

导入：用 <el-upload> 或表单上传 JSON 文件，导入后刷新页面
