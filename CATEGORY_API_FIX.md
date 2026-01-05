# 分类 API 修复说明

## 问题描述

前端多处引用分类API（`/api/v1/categories`），但后端未实现对应路由，导致前端分类页面和相关功能无法正常工作。

## 修复内容

### 1. 新增文件

#### 后端核心文件

1. **`app/schemas/category.py`** - 分类相关的 Pydantic Schema
   - `CategoryBase` - 基础分类模型
   - `CategoryCreate` - 创建分类模型
   - `CategoryUpdate` - 更新分类模型
   - `Category` - 完整分类模型
   - `CategoryListResponse` - 分类列表响应模型

2. **`app/services/category_service.py`** - 分类业务逻辑服务
   - `get_category()` - 获取单个分类
   - `get_categories()` - 获取分类列表
   - `create_category()` - 创建分类
   - `update_category()` - 更新分类
   - `delete_category()` - 删除分类
   - `get_category_by_name()` - 根据名称查询分类
   - `ensure_default_categories()` - 确保默认分类存在

3. **`app/api/v1/categories.py`** - 分类 API 路由
   - `GET /api/v1/categories` - 获取分类列表
   - `GET /api/v1/categories/{id}` - 获取单个分类
   - `GET /api/v1/categories/{id}/articles` - 获取分类下的文章
   - `POST /api/v1/categories` - 创建新分类
   - `PUT /api/v1/categories/{id}` - 更新分类
   - `DELETE /api/v1/categories/{id}` - 删除分类

#### 测试和工具文件

4. **`tests/test_api/test_categories.py`** - 分类API测试文件

5. **`scripts/test_categories_api.py`** - 分类API手动测试工具

### 2. 修改的文件

1. **`app/main.py`**
   - 导入 `categories` 路由模块
   - 注册分类路由到应用

2. **`scripts/seed_data.py`**
   - 添加 `import_categories()` 函数
   - 在种子数据导入时自动创建默认分类

### 3. 默认分类

系统会自动创建以下9个默认分类：

| 分类名 | 描述 |
|--------|------|
| 科技 | 科技、互联网、AI等相关新闻 |
| 财经 | 金融、商业、经济相关新闻 |
| 体育 | 体育赛事、运动相关新闻 |
| 娱乐 | 娱乐、影视、音乐相关新闻 |
| 政治 | 政治、国际关系相关新闻 |
| 社会 | 社会民生、生活相关新闻 |
| 教育 | 教育、学术相关新闻 |
| 健康 | 健康、医疗、养生相关新闻 |
| 其他 | 其他未分类新闻 |

## 使用说明

### 初始化数据库和分类

```bash
# 1. 初始化数据库（如果还未初始化）
python scripts/init_db.py

# 2. 导入种子数据（包括默认分类）
python scripts/seed_data.py
```

### 测试分类API

```bash
# 确保后端服务已启动
make run
# 或
uvicorn app.main:app --reload

# 在另一个终端运行测试
python scripts/test_categories_api.py
```

### API 使用示例

#### 获取所有分类
```bash
curl http://localhost:8000/api/v1/categories
```

响应示例：
```json
{
  "categories": [
    {
      "id": 1,
      "name": "科技",
      "description": "科技、互联网、AI等相关新闻",
      "parent_id": null,
      "is_active": true
    },
    ...
  ],
  "total": 9
}
```

#### 获取单个分类
```bash
curl http://localhost:8000/api/v1/categories/1
```

#### 获取分类下的文章
```bash
curl http://localhost:8000/api/v1/categories/1/articles?page=1&size=20
```

#### 创建新分类
```bash
curl -X POST http://localhost:8000/api/v1/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "新分类",
    "description": "新分类描述",
    "is_active": true
  }'
```

## 技术细节

### 分类服务特性

1. **自动初始化** - 首次访问分类API时，会自动创建默认分类
2. **名称唯一性** - 分类名称不能重复
3. **层级支持** - 支持 `parent_id` 实现分类层级（当前未启用）
4. **状态管理** - 支持 `is_active` 标记分类启用状态

### 与现有功能的集成

1. **文章分类** - 文章表中的 `category` 字段存储分类名称
2. **筛选功能** - 文章列表API支持按分类筛选
3. **前端联动** - 前端分类页面现在可以正常工作

## API 端点清单

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v1/categories` | 获取分类列表 |
| GET | `/api/v1/categories/{id}` | 获取单个分类详情 |
| GET | `/api/v1/categories/{id}/articles` | 获取分类下的文章 |
| POST | `/api/v1/categories` | 创建新分类 |
| PUT | `/api/v1/categories/{id}` | 更新分类 |
| DELETE | `/api/v1/categories/{id}` | 删除分类 |

## 验证清单

- [x] 创建分类 Schema
- [x] 创建分类 Service
- [x] 创建分类 API 路由
- [x] 在主应用中注册路由
- [x] 更新种子数据脚本
- [x] 创建测试文件
- [x] 创建测试工具
- [x] 无语法错误
- [x] 与前端API调用匹配

## 后续建议

1. **增加分类统计** - 显示每个分类下的文章数量
2. **分类层级** - 实现多级分类功能
3. **分类图标** - 为每个分类添加图标字段
4. **智能推荐** - 基于用户浏览历史推荐分类
5. **集成测试** - 补充完整的端到端测试

## 修复状态

✅ **已完成** - 分类API功能已完全实现并可用

前端现在可以正常：
- 访问 `/categories` 页面
- 显示分类列表
- 按分类筛选文章
- 查看分类下的文章
