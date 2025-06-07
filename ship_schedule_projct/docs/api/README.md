# API文档总览

## 📋 概述

船舶航线管理系统提供完整的RESTful API接口，支持船期管理、本地费用管理和用户认证等功能。所有API都基于Django REST Framework构建，提供标准的HTTP方法和状态码。

## 🔗 基础信息

### API基础URL
```
http://127.0.0.1:8000/api/
```

### 认证方式
所有API（除公开接口外）都需要JWT Token认证：
```http
Authorization: Bearer <your_access_token>
```

### 响应格式
API统一使用JSON格式响应，标准响应结构：

#### 成功响应
```json
{
    "success": true,
    "message": "操作成功",
    "data": {
        // 具体数据内容
    }
}
```

#### 错误响应
```json
{
    "success": false,
    "message": "错误描述",
    "data": null,
    "error_code": "ERROR_CODE"
}
```

## 📚 API模块

### 🔐 认证模块 (authentication)
**基础路径**: `/api/auth/`

| 功能 | 端点 | 方法 | 说明 |
|------|------|------|------|
| 用户登录 | `/login/` | POST | 用户登录获取Token |
| 用户登出 | `/logout/` | POST | 用户登出 |
| Token刷新 | `/token/refresh/` | POST | 刷新访问Token |
| 用户信息 | `/me/` | GET | 获取当前用户信息 |
| 用户权限 | `/me/permissions/` | GET | 获取当前用户权限 |
| 用户注册 | `/register/` | POST | 新用户注册 |

**详细文档**: [认证API文档](authentication.md)

### 🚢 船期管理模块 (schedules)
**基础路径**: `/api/`

#### 船舶航线管理
| 功能 | 端点 | 方法 | 说明 |
|------|------|------|------|
| 航线列表 | `/schedules/` | GET | 获取船舶航线列表 |
| 创建航线 | `/schedules/` | POST | 创建新的船舶航线 |
| 航线详情 | `/schedules/{id}/` | GET | 获取特定航线详情 |
| 更新航线 | `/schedules/{id}/` | PUT | 更新航线信息 |
| 删除航线 | `/schedules/{id}/` | DELETE | 删除航线 |

#### 船舶额外信息管理
| 功能 | 端点 | 方法 | 说明 |
|------|------|------|------|
| 信息列表 | `/vessel-info/` | GET | 获取船舶额外信息列表 |
| 创建信息 | `/vessel-info/` | POST | 创建船舶额外信息 |
| 信息详情 | `/vessel-info/{id}/` | GET | 获取特定信息详情 |
| 更新信息 | `/vessel-info/{id}/` | PUT | 更新信息 |
| 删除信息 | `/vessel-info/{id}/` | DELETE | 删除信息 |
| 批量创建 | `/vessel-info/bulk-create/` | POST | 批量创建信息 |
| 批量更新 | `/vessel-info/bulk-update/` | PATCH | 批量更新信息 |
| 批量删除 | `/vessel-info/bulk-delete/` | DELETE | 批量删除信息 |

#### 前台查询API
| 功能 | 端点 | 方法 | 说明 |
|------|------|------|------|
| 共舱分组查询 | `/schedules/cabin-grouping-with-info/` | GET | 前台船期查询（含额外信息） |
| 基础共舱分组 | `/schedules/cabin-grouping/` | GET | 基础共舱分组查询 |
| 船舶信息查询 | `/vessel-info/query/` | GET | 查询特定船舶信息 |

**详细文档**: [船期管理API文档](schedules.md)

### 💰 本地费用模块 (local_fees)
**基础路径**: `/api/local-fees/`

| 功能 | 端点 | 方法 | 说明 |
|------|------|------|------|
| 费用列表 | `/local-fees/` | GET | 获取本地费用列表 |
| 创建费用 | `/local-fees/` | POST | 创建新的本地费用 |
| 费用详情 | `/local-fees/{id}/` | GET | 获取特定费用详情 |
| 更新费用 | `/local-fees/{id}/` | PUT | 更新费用信息 |
| 删除费用 | `/local-fees/{id}/` | DELETE | 删除费用 |
| 费用查询 | `/local-fees/query/` | GET | 前台费用查询API |

**详细文档**: [本地费用API文档](local_fees.md)

## 🔑 权限系统

### 权限类型
- **vessel_info.*** - 船舶额外信息管理权限
- **vessel_schedule.*** - 船舶航线管理权限
- **vessel_schedule_list** - 航期查询权限
- **local_fee.*** - 本地费用管理权限

### 权限检查
每个API端点都有相应的权限要求，详见各模块的API文档。

## 📊 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或Token无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 🧪 测试工具

### API健康检查
```bash
curl -X GET http://127.0.0.1:8000/api/
```

### 获取访问Token
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

### 使用Token访问API
```bash
curl -X GET http://127.0.0.1:8000/api/schedules/ \
  -H "Authorization: Bearer <your_token>"
```

## 📝 注意事项

1. **认证要求**: 除了健康检查和登录接口，所有API都需要认证
2. **权限控制**: 不同操作需要相应的权限，请确保用户角色配置正确
3. **数据版本**: 船期查询API只返回最新版本数据
4. **中文支持**: 所有错误消息和提示都使用中文
5. **批量操作**: 支持批量创建、更新、删除操作，提高效率

## 🔗 相关链接

- **[认证API详细文档](authentication.md)**
- **[船期管理API详细文档](schedules.md)**
- **[本地费用API详细文档](local_fees.md)**
- **[权限系统说明](../development/permissions.md)**
