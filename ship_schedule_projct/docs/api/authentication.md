# 认证API文档

## 📋 概述

认证模块提供用户注册、登录、权限管理等功能，基于JWT Token实现安全的用户认证机制。

**基础路径**: `/api/auth/`

## 🔐 认证接口

### 1. 用户登录

**端点**: `POST /api/auth/login/`
**权限**: 无需认证
**描述**: 用户登录获取访问Token

#### 请求参数
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | string | 是 | 用户邮箱地址 |
| password | string | 是 | 用户密码 |

#### 响应示例
```json
{
    "message": "登录成功",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "张",
        "last_name": "三",
        "full_name": "张三",
        "short_name": "张三",
        "date_joined": "2025-05-27T10:00:00Z",
        "last_login": "2025-05-27T15:30:00Z"
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### 错误响应
- **400**: 邮箱或密码错误
- **400**: 用户账户已被禁用

### 2. 用户登出

**端点**: `POST /api/auth/logout/`
**权限**: 需要认证
**描述**: 用户登出，使Token失效

#### 请求参数
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| refresh | string | 是 | 刷新Token |

#### 响应示例
```json
{
    "message": "登出成功"
}
```

### 3. Token刷新

**端点**: `POST /api/auth/token/refresh/`
**权限**: 无需认证
**描述**: 使用刷新Token获取新的访问Token

#### 请求参数
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 响应示例
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 4. 用户注册

**端点**: `POST /api/auth/register/`
**权限**: 无需认证
**描述**: 新用户注册

#### 请求参数
```json
{
    "email": "newuser@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "李",
    "last_name": "四"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | string | 是 | 邮箱地址，用于登录 |
| password | string | 是 | 密码，至少8位 |
| password_confirm | string | 是 | 确认密码，必须与密码一致 |
| first_name | string | 否 | 名字 |
| last_name | string | 否 | 姓氏 |

#### 响应示例
```json
{
    "message": "注册成功",
    "user": {
        "id": 2,
        "email": "newuser@example.com",
        "first_name": "李",
        "last_name": "四",
        "full_name": "李四",
        "short_name": "李四",
        "date_joined": "2025-05-27T16:00:00Z",
        "last_login": null
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

## 👤 用户信息接口

### 1. 获取当前用户信息

**端点**: `GET /api/auth/me/`
**权限**: 需要认证
**描述**: 获取当前登录用户的详细信息

#### 响应示例
```json
{
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "张",
        "last_name": "三",
        "full_name": "张三",
        "short_name": "张三",
        "avatar": "/media/user_avatars/1/avatar_1.jpg",
        "avatar_url": "http://127.0.0.1:8000/media/user_avatars/1/avatar_1.jpg",
        "is_superuser": false,
        "is_staff": false,
        "is_active": true,
        "date_joined": "2025-05-27T10:00:00Z",
        "last_login": "2025-05-27T15:30:00Z"
    }
}
```

### 2. 获取用户权限

**端点**: `GET /api/auth/me/permissions/`
**权限**: 需要认证
**描述**: 获取当前用户的所有权限

#### 响应示例
```json
{
    "permissions": [
        "vessel_schedule_list",
        "vessel_info.list",
        "vessel_info.detail",
        "local_fee.query"
    ],
    "roles": [
        "业务用户",
        "船期查询员"
    ]
}
```

### 3. 更新用户信息

**端点**: `PUT /api/auth/user/`
**权限**: 需要认证
**描述**: 更新当前用户的基本信息

#### 请求参数
```json
{
    "first_name": "张",
    "last_name": "三丰",
    "current_password": "oldpassword",
    "new_password": "newpassword123"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| first_name | string | 否 | 名字 |
| last_name | string | 否 | 姓氏 |
| current_password | string | 否 | 当前密码（修改密码时必填） |
| new_password | string | 否 | 新密码（修改密码时必填） |

### 4. 用户头像管理

#### 4.1 上传头像

**端点**: `POST /api/auth/me/avatar/`
**权限**: 需要认证
**描述**: 上传用户头像，支持jpg、png、gif格式，最大5MB

##### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| avatar | file | 是 | 头像图片文件 |

##### 文件要求
- **支持格式**: jpg、jpeg、png、gif
- **最大大小**: 5MB
- **最大尺寸**: 2048x2048像素
- **存储路径**: `user_avatars/{user_id}/avatar_{user_id}.{ext}`

##### 响应示例
```json
{
    "success": true,
    "message": "头像上传成功",
    "data": {
        "avatar_url": "http://127.0.0.1:8000/media/user_avatars/1/avatar_1.jpg",
        "user": {
            "id": 1,
            "email": "user@example.com",
            "first_name": "张",
            "last_name": "三",
            "full_name": "张三",
            "short_name": "张三",
            "avatar": "/media/user_avatars/1/avatar_1.jpg",
            "avatar_url": "http://127.0.0.1:8000/media/user_avatars/1/avatar_1.jpg",
            "is_superuser": false,
            "is_staff": false,
            "is_active": true,
            "date_joined": "2025-05-28T10:00:00Z",
            "last_login": "2025-05-28T15:30:00Z"
        }
    }
}
```

##### 错误响应
```json
{
    "success": false,
    "message": "头像上传失败",
    "data": null,
    "errors": {
        "avatar": ["头像文件大小不能超过5MB"]
    }
}
```

#### 4.2 删除头像

**端点**: `DELETE /api/auth/me/avatar/`
**权限**: 需要认证
**描述**: 删除用户头像

##### 响应示例
```json
{
    "success": true,
    "message": "头像删除成功",
    "data": {
        "user": {
            "id": 1,
            "email": "user@example.com",
            "first_name": "张",
            "last_name": "三",
            "full_name": "张三",
            "short_name": "张三",
            "avatar": null,
            "avatar_url": null,
            "is_superuser": false,
            "is_staff": false,
            "is_active": true,
            "date_joined": "2025-05-28T10:00:00Z",
            "last_login": "2025-05-28T15:30:00Z"
        }
    }
}
```

##### 错误响应
```json
{
    "success": false,
    "message": "用户暂无头像",
    "data": null
}
```

## 🔐 权限管理接口

### 1. 获取权限列表

**端点**: `GET /api/auth/permissions/`
**权限**: 需要认证 + `permission.list` 权限
**描述**: 获取系统所有权限列表

#### 查询参数
| 参数 | 类型 | 说明 |
|------|------|------|
| category | string | 按权限分类过滤 |
| search | string | 搜索权限名称或代码 |

#### 响应示例
```json
{
    "count": 15,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "code": "user.list",
            "name": "查看用户列表",
            "description": "查看系统用户列表",
            "category": "用户管理",
            "created_at": "2025-05-27T10:00:00Z"
        },
        {
            "id": 2,
            "code": "role.create",
            "name": "创建角色",
            "description": "创建新的用户角色",
            "category": "角色管理",
            "created_at": "2025-05-27T10:00:00Z"
        },
        {
            "id": 3,
            "code": "vessel_schedule_list",
            "name": "船期查询",
            "description": "查看船期列表和详情",
            "category": "船期管理",
            "created_at": "2025-05-27T10:00:00Z"
        }
    ]
}
```

### 2. 获取权限详情

**端点**: `GET /api/auth/permissions/{id}/`
**权限**: 需要认证 + `permission.detail` 权限
**描述**: 获取特定权限的详细信息

#### 响应示例
```json
{
    "id": 1,
    "code": "user.list",
    "name": "查看用户列表",
    "description": "查看系统用户列表，包括用户基本信息和状态",
    "category": "用户管理",
    "created_at": "2025-05-27T10:00:00Z"
}
```

## 👥 角色管理接口

### 1. 获取角色列表

**端点**: `GET /api/auth/roles/`
**权限**: 需要认证 + `role.list` 权限
**描述**: 获取系统所有角色列表

#### 查询参数
| 参数 | 类型 | 说明 |
|------|------|------|
| is_active | boolean | 过滤激活状态的角色 |
| search | string | 搜索角色名称 |

#### 响应示例
```json
{
    "count": 4,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "超级管理员",
            "description": "拥有系统所有权限",
            "is_active": true,
            "permission_count": 15,
            "created_at": "2025-05-27T10:00:00Z",
            "updated_at": "2025-05-27T10:00:00Z"
        },
        {
            "id": 2,
            "name": "业务用户",
            "description": "可以查询船期和费用信息",
            "is_active": true,
            "permission_count": 3,
            "created_at": "2025-05-27T10:00:00Z",
            "updated_at": "2025-05-27T10:00:00Z"
        }
    ]
}
```

### 2. 获取角色详情

**端点**: `GET /api/auth/roles/{id}/`
**权限**: 需要认证 + `role.detail` 权限
**描述**: 获取特定角色的详细信息，包括权限列表

#### 响应示例
```json
{
    "id": 2,
    "name": "业务用户",
    "description": "可以查询船期和费用信息",
    "is_active": true,
    "permissions": [
        {
            "id": 3,
            "code": "vessel_schedule_list",
            "name": "船期查询",
            "description": "查看船期列表和详情",
            "category": "船期管理",
            "created_at": "2025-05-27T10:00:00Z"
        },
        {
            "id": 4,
            "code": "local_fee.list",
            "name": "查看费用列表",
            "description": "查看本地费用信息",
            "category": "费用管理",
            "created_at": "2025-05-27T10:00:00Z"
        }
    ],
    "created_at": "2025-05-27T10:00:00Z",
    "updated_at": "2025-05-27T10:00:00Z"
}
```

### 3. 创建角色

**端点**: `POST /api/auth/roles/`
**权限**: 需要认证 + `role.create` 权限
**描述**: 创建新的用户角色

#### 请求参数
```json
{
    "name": "船期管理员",
    "description": "负责船期信息的管理和维护",
    "is_active": true,
    "permission_codes": [
        "vessel_schedule_list",
        "vessel_schedule.create",
        "vessel_schedule.update"
    ]
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 角色名称，必须唯一 |
| description | string | 否 | 角色描述 |
| is_active | boolean | 否 | 是否激活，默认true |
| permission_codes | array | 否 | 权限代码列表 |

#### 响应示例
```json
{
    "id": 5,
    "name": "船期管理员",
    "description": "负责船期信息的管理和维护",
    "is_active": true,
    "permissions": [
        {
            "id": 3,
            "code": "vessel_schedule_list",
            "name": "船期查询",
            "description": "查看船期列表和详情",
            "category": "船期管理",
            "created_at": "2025-05-27T10:00:00Z"
        }
    ],
    "created_at": "2025-05-27T15:30:00Z",
    "updated_at": "2025-05-27T15:30:00Z"
}
```

### 4. 更新角色

**端点**: `PUT /api/auth/roles/{id}/`
**权限**: 需要认证 + `role.update` 权限
**描述**: 更新角色信息和权限

#### 请求参数
```json
{
    "name": "高级业务用户",
    "description": "可以查询和管理船期费用信息",
    "is_active": true,
    "permission_codes": [
        "vessel_schedule_list",
        "local_fee.list",
        "local_fee.detail",
        "local_fee.create"
    ]
}
```

#### 响应示例
```json
{
    "id": 2,
    "name": "高级业务用户",
    "description": "可以查询和管理船期费用信息",
    "is_active": true,
    "permissions": [
        {
            "id": 3,
            "code": "vessel_schedule_list",
            "name": "船期查询",
            "description": "查看船期列表和详情",
            "category": "船期管理",
            "created_at": "2025-05-27T10:00:00Z"
        },
        {
            "id": 4,
            "code": "local_fee.list",
            "name": "查看费用列表",
            "description": "查看本地费用信息",
            "category": "费用管理",
            "created_at": "2025-05-27T10:00:00Z"
        }
    ],
    "created_at": "2025-05-27T10:00:00Z",
    "updated_at": "2025-05-27T15:45:00Z"
}
```

### 5. 删除角色

**端点**: `DELETE /api/auth/roles/{id}/`
**权限**: 需要认证 + `role.delete` 权限
**描述**: 删除指定角色

#### 响应示例
```json
{
    "message": "角色删除成功"
}
```

## 👤 用户管理接口

### 1. 获取用户列表

**端点**: `GET /api/auth/users/`
**权限**: 需要认证 + `user.list` 权限
**描述**: 获取系统用户列表

#### 查询参数
| 参数 | 类型 | 说明 |
|------|------|------|
| page | integer | 页码，默认1 |
| page_size | integer | 每页数量，默认20 |
| search | string | 搜索用户邮箱或姓名 |
| is_active | boolean | 过滤活跃用户 |

#### 响应示例
```json
{
    "users": [
        {
            "id": 1,
            "email": "admin@example.com",
            "first_name": "管理",
            "last_name": "员",
            "full_name": "管理员",
            "short_name": "管理员",
            "is_superuser": true,
            "is_staff": true,
            "is_active": true,
            "date_joined": "2025-05-27T10:00:00Z",
            "last_login": "2025-05-27T15:30:00Z"
        },
        {
            "id": 2,
            "email": "user@example.com",
            "first_name": "普通",
            "last_name": "用户",
            "full_name": "普通用户",
            "short_name": "普通用户",
            "is_superuser": false,
            "is_staff": false,
            "is_active": true,
            "date_joined": "2025-05-27T11:00:00Z",
            "last_login": "2025-05-27T14:20:00Z"
        }
    ],
    "total": 2,
    "page": 1,
    "page_size": 20
}
```

### 2. 创建新用户

**端点**: `POST /api/auth/users-management/`
**权限**: 需要认证 + `user.create` 权限
**描述**: 创建新的用户账户

#### 请求参数
```json
{
    "email": "newuser@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "新",
    "last_name": "用户"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | string | 是 | 邮箱地址，必须唯一 |
| password | string | 是 | 密码，至少8位 |
| password_confirm | string | 是 | 确认密码 |
| first_name | string | 否 | 名字 |
| last_name | string | 否 | 姓氏 |

#### 响应示例
```json
{
    "message": "用户创建成功",
    "user": {
        "id": 24,
        "email": "newuser@example.com",
        "first_name": "新",
        "last_name": "用户",
        "full_name": "新用户",
        "short_name": "新用户",
        "is_superuser": false,
        "is_staff": false,
        "is_active": true,
        "date_joined": "2025-05-28T15:30:00Z",
        "last_login": null
    }
}
```

### 3. 获取用户详情

**端点**: `GET /api/auth/users-management/{id}/`
**权限**: 需要认证 + `user.detail` 权限
**描述**: 获取指定用户的详细信息

#### 响应示例
```json
{
    "user": {
        "id": 24,
        "email": "newuser@example.com",
        "first_name": "新",
        "last_name": "用户",
        "full_name": "新用户",
        "short_name": "新用户",
        "is_superuser": false,
        "is_staff": false,
        "is_active": true,
        "date_joined": "2025-05-28T15:30:00Z",
        "last_login": "2025-05-28T16:00:00Z"
    }
}
```

### 4. 更新用户信息

**端点**: `PUT /api/auth/users-management/{id}/`
**权限**: 需要认证 + `user.update` 权限
**描述**: 更新指定用户的信息

#### 请求参数
```json
{
    "first_name": "更新",
    "last_name": "用户名"
}
```

#### 响应示例
```json
{
    "message": "用户信息更新成功",
    "user": {
        "id": 24,
        "email": "newuser@example.com",
        "first_name": "更新",
        "last_name": "用户名",
        "full_name": "更新用户名",
        "short_name": "更新用户名",
        "is_superuser": false,
        "is_staff": false,
        "is_active": true,
        "date_joined": "2025-05-28T15:30:00Z",
        "last_login": "2025-05-28T16:00:00Z"
    }
}
```

### 5. 删除用户

**端点**: `DELETE /api/auth/users-management/{id}/`
**权限**: 需要认证 + `user.delete` 权限
**描述**: 删除指定用户（软删除，设置为非活跃状态）

#### 安全限制
- 无法删除超级管理员账户
- 无法删除自己的账户

#### 响应示例
```json
{
    "message": "用户 newuser@example.com 已被删除"
}
```

#### 错误响应
```json
{
    "error": "无法删除超级管理员账户"
}
```

```json
{
    "error": "无法删除自己的账户"
}
```

## 🔗 用户角色分配接口

### 1. 获取用户角色

**端点**: `GET /api/auth/users/{user_id}/roles/`
**权限**: 需要认证 + `user.role.view` 权限
**描述**: 获取指定用户的角色信息

#### 响应示例
```json
{
    "user_id": 2,
    "roles": [
        {
            "id": 2,
            "name": "业务用户",
            "description": "可以查询船期和费用信息",
            "is_active": true,
            "permission_count": 3,
            "created_at": "2025-05-27T10:00:00Z",
            "updated_at": "2025-05-27T10:00:00Z"
        },
        {
            "id": 3,
            "name": "查询员",
            "description": "专门负责信息查询",
            "is_active": true,
            "permission_count": 2,
            "created_at": "2025-05-27T10:00:00Z",
            "updated_at": "2025-05-27T10:00:00Z"
        }
    ]
}
```

### 2. 分配用户角色

**端点**: `POST /api/auth/users/{user_id}/roles/`
**权限**: 需要认证 + `user.role.assign` 权限
**描述**: 给指定用户分配角色

#### 请求参数
```json
{
    "roles": [2, 3, 5]
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| roles | array | 是 | 角色ID列表 |

#### 响应示例
```json
{
    "message": "角色分配成功",
    "user_id": 2,
    "roles": [
        {
            "id": 2,
            "name": "业务用户",
            "description": "可以查询船期和费用信息",
            "is_active": true,
            "permission_count": 3,
            "created_at": "2025-05-27T10:00:00Z",
            "updated_at": "2025-05-27T10:00:00Z"
        },
        {
            "id": 3,
            "name": "查询员",
            "description": "专门负责信息查询",
            "is_active": true,
            "permission_count": 2,
            "created_at": "2025-05-27T10:00:00Z",
            "updated_at": "2025-05-27T10:00:00Z"
        },
        {
            "id": 5,
            "name": "船期管理员",
            "description": "负责船期信息的管理和维护",
            "is_active": true,
            "permission_count": 5,
            "created_at": "2025-05-27T15:30:00Z",
            "updated_at": "2025-05-27T15:30:00Z"
        }
    ]
}
```

### 3. 更新用户角色

**端点**: `PUT /api/auth/users/{user_id}/roles/`
**权限**: 需要认证 + `user.role.assign` 权限
**描述**: 更新指定用户的角色（替换现有角色）

#### 请求参数
```json
{
    "roles": [2, 5]
}
```

#### 响应示例
```json
{
    "message": "角色分配成功",
    "user_id": 2,
    "roles": [
        {
            "id": 2,
            "name": "业务用户",
            "description": "可以查询船期和费用信息",
            "is_active": true,
            "permission_count": 3,
            "created_at": "2025-05-27T10:00:00Z",
            "updated_at": "2025-05-27T10:00:00Z"
        },
        {
            "id": 5,
            "name": "船期管理员",
            "description": "负责船期信息的管理和维护",
            "is_active": true,
            "permission_count": 5,
            "created_at": "2025-05-27T15:30:00Z",
            "updated_at": "2025-05-27T15:30:00Z"
        }
    ]
}
```

### 4. 移除用户角色

**端点**: `DELETE /api/auth/users/{user_id}/roles/{role_id}/`
**权限**: 需要认证 + `user.role.remove` 权限
**描述**: 移除用户的特定角色

#### 响应示例
```json
{
    "message": "成功移除用户 user@example.com 的角色 查询员"
}
```

## 📊 权限代码参考

### 用户管理权限
| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `user.list` | 查看用户列表 | 查看系统所有用户 |
| `user.detail` | 查看用户详情 | 查看特定用户信息 |
| `user.create` | 创建用户 | 创建新用户账户 |
| `user.update` | 更新用户 | 修改用户信息 |
| `user.delete` | 删除用户 | 删除用户账户 |

### 角色管理权限
| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `role.list` | 查看角色列表 | 查看系统所有角色 |
| `role.detail` | 查看角色详情 | 查看特定角色信息 |
| `role.create` | 创建角色 | 创建新角色 |
| `role.update` | 更新角色 | 修改角色信息和权限 |
| `role.delete` | 删除角色 | 删除角色 |

### 权限管理权限
| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `permission.list` | 查看权限列表 | 查看系统所有权限 |
| `permission.detail` | 查看权限详情 | 查看特定权限信息 |

### 用户角色分配权限
| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `user.role.view` | 查看用户角色 | 查看用户拥有的角色 |
| `user.role.assign` | 分配用户角色 | 给用户分配或修改角色 |
| `user.role.remove` | 移除用户角色 | 移除用户的特定角色 |

### 业务权限
| 权限代码 | 权限名称 | 说明 |
|----------|----------|------|
| `vessel_schedule_list` | 船期查询 | 查看船期列表和详情 |
| `vessel_schedule.create` | 创建船期 | 创建新的船期信息 |
| `vessel_schedule.update` | 更新船期 | 修改船期信息 |
| `vessel_schedule.delete` | 删除船期 | 删除船期信息 |
| `local_fee.list` | 查看费用列表 | 查看本地费用信息 |
| `local_fee.detail` | 查看费用详情 | 查看特定费用详情 |
| `local_fee.create` | 创建费用 | 创建新的费用记录 |
| `local_fee.update` | 更新费用 | 修改费用信息 |
| `local_fee.delete` | 删除费用 | 删除费用记录 |

## ⚠️ 常见错误和解决方案

### 1. 权限不足错误
```json
{
    "detail": "您没有权限执行此操作，需要权限: user.list"
}
```
**解决方案**: 确保用户拥有相应权限，或联系管理员分配权限

### 2. 角色不存在错误
```json
{
    "roles": ["以下角色ID不存在或未激活: 999"]
}
```
**解决方案**: 检查角色ID是否正确，确保角色处于激活状态

### 3. 权限代码不存在错误
```json
{
    "permission_codes": ["以下权限代码不存在: invalid.permission"]
}
```
**解决方案**: 检查权限代码是否正确，参考权限代码参考表

### 4. 用户不存在错误
```json
{
    "detail": "未找到"
}
```
**解决方案**: 检查用户ID是否正确，确保用户存在

### 5. 角色名称重复错误
```json
{
    "name": ["具有该 角色名称 的 角色 已存在。"]
}
```
**解决方案**: 使用不同的角色名称

## 🛡️ 安全说明

### Token机制
- **访问Token**: 有效期较短（通常15分钟），用于API访问
- **刷新Token**: 有效期较长（通常7天），用于获取新的访问Token
- **Token轮换**: 每次刷新都会生成新的Token对

### 密码要求
- 最少8位字符
- 建议包含大小写字母、数字和特殊字符
- 不能与常见密码相同

### 权限控制
- 基于角色的权限控制（RBAC）
- 细粒度权限分配
- 支持权限继承和组合

## 📝 使用示例

### 完整登录流程
```bash
# 1. 用户登录
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# 2. 使用Token访问API
curl -X GET http://127.0.0.1:8000/api/auth/me/ \
  -H "Authorization: Bearer <access_token>"

# 3. 刷新Token
curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

### 权限管理示例
```bash
# 1. 获取所有权限列表
curl -X GET http://127.0.0.1:8000/api/auth/permissions/ \
  -H "Authorization: Bearer <access_token>"

# 2. 创建新角色
curl -X POST http://127.0.0.1:8000/api/auth/roles/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "船期管理员",
    "description": "负责船期信息的管理和维护",
    "permission_codes": ["vessel_schedule_list", "vessel_schedule.create", "vessel_schedule.update"]
  }'

# 3. 给用户分配角色
curl -X POST http://127.0.0.1:8000/api/auth/users/2/roles/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"roles": [2, 3]}'

# 4. 获取用户权限
curl -X GET http://127.0.0.1:8000/api/auth/me/permissions/ \
  -H "Authorization: Bearer <access_token>"
```

### 头像管理示例
```bash
# 1. 上传头像
curl -X POST http://127.0.0.1:8000/api/auth/me/avatar/ \
  -H "Authorization: Bearer <access_token>" \
  -F "avatar=@/path/to/avatar.jpg"

# 2. 删除头像
curl -X DELETE http://127.0.0.1:8000/api/auth/me/avatar/ \
  -H "Authorization: Bearer <access_token>"

# 3. 获取用户信息（包含头像URL）
curl -X GET http://127.0.0.1:8000/api/auth/me/ \
  -H "Authorization: Bearer <access_token>"
```

### 前端权限检查示例
```javascript
// 前端权限检查函数
function hasPermission(userPermissions, requiredPermission) {
    // 检查是否为超级管理员
    if (user.is_superuser) {
        return true;
    }

    // 检查具体权限
    return userPermissions.includes(requiredPermission);
}

// 使用示例
const userPermissions = ['vessel_schedule_list', 'local_fee.list'];
const canViewUsers = hasPermission(userPermissions, 'user.list');

if (canViewUsers) {
    // 显示用户管理菜单
    showUserManagementMenu();
} else {
    // 隐藏用户管理菜单
    hideUserManagementMenu();
}
```

### Vue Element-Plus头像上传示例
```vue
<template>
  <div class="avatar-upload">
    <!-- 头像显示 -->
    <el-avatar
      :size="100"
      :src="userInfo.avatar_url"
      :icon="UserFilled"
      class="avatar-display"
    />

    <!-- 头像上传组件 -->
    <el-upload
      class="avatar-uploader"
      action="/api/auth/me/avatar/"
      :headers="uploadHeaders"
      :show-file-list="false"
      :on-success="handleAvatarSuccess"
      :on-error="handleAvatarError"
      :before-upload="beforeAvatarUpload"
      accept=".jpg,.jpeg,.png,.gif"
    >
      <el-button type="primary" :icon="Upload">上传头像</el-button>
    </el-upload>

    <!-- 删除头像按钮 -->
    <el-button
      v-if="userInfo.avatar_url"
      type="danger"
      :icon="Delete"
      @click="deleteAvatar"
    >
      删除头像
    </el-button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, Delete, UserFilled } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo)

// 上传请求头
const uploadHeaders = computed(() => ({
  'Authorization': `Bearer ${userStore.accessToken}`
}))

// 上传前验证
const beforeAvatarUpload = (file) => {
  const isValidType = ['image/jpeg', 'image/png', 'image/gif'].includes(file.type)
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isValidType) {
    ElMessage.error('头像格式不支持，请上传jpg、png或gif格式的图片')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('头像文件大小不能超过5MB')
    return false
  }
  return true
}

// 上传成功回调
const handleAvatarSuccess = (response) => {
  if (response.success) {
    ElMessage.success(response.message)
    // 更新用户信息
    userStore.updateUserInfo(response.data.user)
  } else {
    ElMessage.error(response.message || '头像上传失败')
  }
}

// 上传失败回调
const handleAvatarError = (error) => {
  console.error('头像上传失败:', error)
  ElMessage.error('头像上传失败，请重试')
}

// 删除头像
const deleteAvatar = async () => {
  try {
    const response = await fetch('/api/auth/me/avatar/', {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${userStore.accessToken}`
      }
    })

    const result = await response.json()

    if (result.success) {
      ElMessage.success(result.message)
      // 更新用户信息
      userStore.updateUserInfo(result.data.user)
    } else {
      ElMessage.error(result.message || '头像删除失败')
    }
  } catch (error) {
    console.error('删除头像失败:', error)
    ElMessage.error('头像删除失败，请重试')
  }
}
</script>

<style scoped>
.avatar-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.avatar-display {
  border: 2px solid #dcdfe6;
}

.avatar-uploader {
  display: flex;
  justify-content: center;
}
</style>
```

## ⚠️ 注意事项

### 🔒 安全相关
1. **Token安全**: 请妥善保管Token，不要在客户端明文存储
2. **密码安全**: 使用强密码，定期更换
3. **权限最小化**: 只分配必要的权限给用户
4. **登出处理**: 应用退出时记得调用登出接口
5. **Token过期**: 访问Token过期时使用刷新Token获取新Token

### 🎯 前端开发重点
1. **用户状态检查**: 登录后必须检查 `is_superuser` 和 `is_staff` 字段
2. **权限验证**: 使用 `/api/auth/me/permissions/` 获取用户权限列表
3. **超级管理员**: `is_superuser=true` 的用户拥有所有权限
4. **错误处理**: 权限不足时显示友好的错误提示
5. **菜单控制**: 根据用户权限动态显示/隐藏菜单项

### 📋 API调用规范
1. **认证头**: 所有需要认证的API都要携带 `Authorization: Bearer <token>`
2. **错误码**: 401表示未认证，403表示权限不足
3. **分页**: 列表API支持 `page` 和 `page_size` 参数
4. **搜索**: 支持 `search` 参数进行模糊搜索
5. **过滤**: 支持各种过滤参数，如 `is_active`

### 🚨 常见问题解决
1. **权限字段undefined**: 确保使用最新的用户序列化器，包含 `is_superuser`、`is_staff` 字段
2. **权限检查失败**: 检查用户是否已分配相应角色和权限
3. **Token过期**: 实现自动刷新Token机制
4. **角色分配失败**: 确保角色ID存在且处于激活状态
5. **权限代码错误**: 参考权限代码参考表，使用正确的权限代码
