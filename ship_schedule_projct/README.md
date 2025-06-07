# 🚢 船舶航线管理系统

[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14.0-blue.svg)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

基于Django REST Framework的现代化船舶航线管理系统，提供完整的船期管理、本地费用管理和用户权限控制功能。

## ✨ 核心特性

- 🚢 **船舶航线管理** - 完整的船期信息管理和查询
- 📊 **船舶额外信息** - 价格、舱位、截关时间等补充信息管理
- 🔄 **数据同步** - 自动同步船期和额外信息
- 👥 **权限管理** - 基于角色的细粒度权限控制
- 🔍 **前台查询** - 专用的前台船期查询API
- 💰 **本地费用** - 完整的本地费用管理功能
- 🔐 **JWT认证** - 安全的Token认证机制
- 📱 **RESTful API** - 标准的REST API设计
- 🌐 **中文支持** - 全面的中文错误提示和文档

## 📋 最新更新记录

### 2025年5月26日 - 权限系统修复 ✅
- **修复问题**: 前台用户无法访问船期查询API的权限问题
- **修复内容**: 在权限映射表中添加 `vessel_schedule_list` 权限映射
- **影响范围**: 修复后所有业务用户可正常使用前台船期查询功能
- **测试状态**: 所有权限测试通过 (14/14) ✓
- **相关文档**:
  - 详细修复记录：`PERMISSION_FIX_RECORD.md`
  - 权限使用指南：`api/permissions.md`
  - 权限测试用例：`tests/test_permission_system.py`

## 项目概述

基于Django REST Framework的船舶航线管理系统，提供船舶航线信息管理、共舱分组、船舶额外信息管理以及前台船期查询页面等功能。系统支持完整的权限管理和JWT认证，适用于航运企业的内部管理和对外信息展示。

## 📁 项目结构

```
ship_schedule_projct/
├── 🔧 核心应用
│   ├── ship_schedule/      # Django项目设置
│   ├── authentication/    # 用户认证和权限管理
│   ├── schedules/         # 船期管理核心模块
│   └── manage.py          # Django管理脚本
├── 📚 文档系统
│   ├── docs/              # 详细文档目录
│   ├── api/               # API文档
│   └── PROJECT_INDEX.md   # 项目总览索引
├── 🛠️ 工具脚本
│   ├── scripts/testing/   # 测试脚本集合
│   ├── scripts/debugging/ # 调试分析工具
│   └── scripts/maintenance/ # 维护管理工具
├── 🧪 测试套件
│   └── tests/             # 正式测试用例
└── 📝 日志缓存
    ├── logs/              # 应用日志
    └── __pycache__/       # Python缓存
```

**快速导航**: 查看 [`PROJECT_INDEX.md`](PROJECT_INDEX.md) 获取完整的项目结构指南和常用操作。

## 核心功能

- 🚢 **船舶航线管理**: VesselSchedule模型，管理船舶基本航线信息
- 📊 **船舶额外信息管理**: VesselInfoFromCompany模型，管理价格、舱位、截关时间等补充信息
- 🔄 **数据同步**: 自动同步VesselSchedule到VesselInfoFromCompany
- 👥 **权限管理**: 基于角色的权限控制系统，确保不同用户角色拥有对应权限
- 🔍 **航期查询**: 前台航期查询页面专用API，支持起运港/目的港筛选和共舱分组
- 🖥️ **前台展示**: 提供船期查询页面，包含搜索功能、结果分组展示和详情查看

## 技术栈

- **后端**: Django 4.2.7 + Django REST Framework 3.14.0
- **认证**: JWT Token认证 (djangorestframework-simplejwt 5.3.0)
- **数据库**: MySQL / SQLite
- **权限**: 自定义角色与权限系统
- **前端**: 支持现代前端框架集成

## 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd ship_schedule_projct

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置
```bash
# 执行迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 创建测试用普通用户（可选，用于权限测试）
python manage.py shell -c "from authentication.models import User; User.objects.create_user(email='user@example.com', password='user123456', first_name='测试', last_name='用户')"
```

### 3. 启动服务
```bash
python manage.py runserver
```

访问 `http://127.0.0.1:8000/api/` 查看API健康状态

## 核心API

### 前台查询API
```bash
# 航期查询（前台页面专用API）- 需要vessel_schedule_list权限
GET /api/schedules/cabin-grouping-with-info/?polCd=CNSHA&podCd=USNYC

# 基础共舱分组
GET /api/schedules/cabin-grouping/?polCd=CNSHA&podCd=USNYC

# 船舶信息查询
GET /api/vessel-info/query/?vessel=TEST&voyage=V001&carriercd=ONE&polCd=CNSHA&podCd=USNYC
```

### 管理后台API
```bash
# 船舶额外信息管理
GET    /api/vessel-info/                # 列表查询
POST   /api/vessel-info/                # 创建
GET    /api/vessel-info/{id}/           # 详情
PUT    /api/vessel-info/{id}/           # 更新
DELETE /api/vessel-info/{id}/           # 删除

# 批量操作
POST   /api/vessel-info/bulk-create/    # 批量创建
PATCH  /api/vessel-info/bulk-update/    # 批量更新
DELETE /api/vessel-info/bulk-delete/    # 批量删除

# 共舱配置管理
GET    /api/cabin-config/detail/        # 配置详情
PUT    /api/cabin-config/update/        # 更新配置
DELETE /api/cabin-config/delete/        # 删除配置
POST   /api/cabin-config/bulk-update/   # 批量更新
```

### 认证API
```bash
# 用户认证
POST   /api/auth/login/                 # 用户登录
POST   /api/auth/logout/                # 用户登出
POST   /api/auth/token/refresh/         # 刷新Token
GET    /api/auth/me/                    # 获取当前用户信息
```

## 前台船期查询页面

系统提供完整的前台船期查询页面功能，布局和功能如下：

### 页面布局
1. **左上方搜索区域** (占页面上方1/3宽度)
   - 起运港输入框
   - 目的港输入框
   - 搜索按钮

2. **右上方宣传区域** (占页面上方2/3宽度)
   - 公司宣传图或视频轮播
   - 与搜索区域等高

3. **下方查询结果区域**
   - 按共舱分组显示查询结果
   - 每个分组以表格形式展示
   - 表格之间有间隙

### 功能特点
- **分组展示**: 根据group_id将航线分组
- **详细信息**: 显示船司代码、计划开船天数、航程时间等信息
- **舱位信息**: 显示20尺/40尺集装箱现舱情况("有现舱"或"--")
- **交互功能**: 点击航程时间可查看详情
- **编辑权限**: 仅管理员可编辑vessel_info信息

### API调用
前台页面主要使用`cabin-grouping-with-info` API，返回结构化的分组数据：
```json
{
  "success": true,
  "message": "共舱分组数据获取成功",
  "data": {
    "groups": [
      {
        "group_id": "group_1",
        "cabins_count": 2,
        "carrier_codes": ["MSK", "ONE"],
        "plan_open": "3",
        "plan_duration": 30,
        "cabin_price": 4500,
        "is_has_gp_20": "有现舱",
        "is_has_hq_40": "有现舱",
        "schedules": [
          {
            "id": 123,
            "vessel": "VESSEL_NAME",
            "voyage": "VOYAGE_NUM",
            "polCd": "CNSHA",
            "podCd": "USNYC",
            "pol": "上海",
            "pod": "纽约",
            "eta": "2025-05-28",
            "etd": "2025-05-01",
            "routeEtd": "3",
            "carriercd": "MSK",
            "totalDuration": 30,
            "shareCabins": [{"carrierCd": "MSK"}, {"carrierCd": "ONE"}],
            "vessel_info": {
              "id": 456,
              "gp_20": "100",
              "hq_40": "50",
              "price": 4500,
              "cut_off_time": "2025-04-30"
            }
          }
        ]
      }
    ],
    "total_groups": 1,
    "version": "20250525",
    "filter": {"polCd": "CNSHA", "podCd": "USNYC"}
  }
}
```

#### 响应字段说明
- **plan_open**: 计划开船日，可能是单个值或多个值的数组
- **plan_duration**: 计划航程时间（天数）
- **cabin_price**: 舱位价格，可能是数值或"--"字符串
- **is_has_gp_20/is_has_hq_40**: 是否有20尺/40尺集装箱现舱，值为"有现舱"或"--"
- **vessel_info**: 船舶额外信息对象，包含价格、舱位和截关时间等信息

## 权限说明

### 权限类型
- `vessel_info.*`: 船舶额外信息管理权限
- `vessel_schedule.*`: 船舶航线管理权限
- `vessel_schedule_list`: 航期查询所需权限

### 角色定义
- **超级管理员**: 所有权限
- **船舶信息管理员**: vessel_info.* 权限
- **航线查询员**: vessel_schedule.list 权限

### 权限控制特点
- **前端UI控制**: 基于用户角色动态显示/隐藏编辑功能
- **API权限验证**: 后端验证确保只有有权限的用户能执行操作
- **JWT集成**: 权限信息包含在JWT token中

## 测试

### 运行测试脚本
```bash
# API综合测试（推荐）
python tests/api_full_test.py

# 或使用提供的测试脚本
./run_api_test.sh

# 其他专项测试
python tests/test_api.py                          # API基础测试
python tests/test_cabin_grouping_with_info_api.py # 航期查询API测试
python tests/test_vessel_info_bulk_operations.py  # 船舶信息管理测试
python tests/test_cabin_config_api.py             # 共舱配置管理测试
python tests/test_permission_api.py               # 权限系统测试
```

### 测试覆盖内容
- **基础API**: 健康检查、认证等
- **用户认证**: 登录、获取信息、token刷新等
- **船期查询**: cabin-grouping-with-info API
- **船舶信息**: vessel-info 相关API
- **权限控制**: 验证不同角色权限控制

## 数据模型

### VesselSchedule (船舶航线)
- **基础字段**:
  - `polCd`: 起运港代码
  - `podCd`: 目的港代码
  - `vessel`: 船名
  - `voyage`: 航次
  - `carriercd`: 承运人代码
  - `routeEtd`: 路线预计出发时间
  - `eta`: 预计到达时间
  - `etd`: 预计出发时间
  - `status`: 状态
  - `data_version`: 数据版本
- **共舱信息**: `shareCabins`字段存储JSON格式的共舱配置

### VesselInfoFromCompany (船舶额外信息)
- **基础字段**: 与VesselSchedule相同的关联字段
- **补充信息**:
  - `gp_20`: 20尺普通集装箱数量
  - `hq_40`: 40尺高箱数量
  - `price`: 价格
  - `cut_off_time`: 截关时间
  - `remark`: 备注信息

## 注意事项

1. **认证**: 所有API都需要JWT Token认证，请求头需要包含`Authorization: Bearer <token>`
2. **权限**: 编辑操作需要相应权限，请确保用户角色配置正确
3. **数据版本**: 航期查询API只返回最新版本数据(data_version最大值)
4. **舱位显示**: "有现舱"表示有足够的舱位，"--"表示无舱位或信息未知
5. **中文支持**: 系统全面支持中文，错误消息和提示均使用中文
6. **测试模式**: 测试脚本中的模拟数据仅用于测试，实际环境需替换为真实数据

## 联系方式

- 技术支持: support@example.com
- 开发团队: dev@example.com

## 最后更新

文档更新时间: 2025-05-25# ship-schedule-management
