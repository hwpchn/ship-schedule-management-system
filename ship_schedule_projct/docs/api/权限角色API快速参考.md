# 权限角色API快速参考

## 🚀 快速开始

### 1. 用户登录并获取权限信息
```bash
# 登录
POST /api/auth/login/
{
  "email": "admin3@example.com",
  "password": "099118aA"
}

# 获取用户权限
GET /api/auth/me/permissions/
Authorization: Bearer <token>
```

### 2. 检查用户状态
```javascript
// 登录响应中的用户信息
{
  "user": {
    "id": 19,
    "email": "admin3@example.com",
    "is_superuser": true,  // ✅ 现在有这个字段了
    "is_staff": true,      // ✅ 现在有这个字段了
    "is_active": true
  }
}
```

## 📋 核心API端点

### 权限管理
- `GET /api/auth/permissions/` - 获取权限列表
- `GET /api/auth/permissions/{id}/` - 获取权限详情

### 角色管理
- `GET /api/auth/roles/` - 获取角色列表
- `POST /api/auth/roles/` - 创建角色
- `GET /api/auth/roles/{id}/` - 获取角色详情
- `PUT /api/auth/roles/{id}/` - 更新角色
- `DELETE /api/auth/roles/{id}/` - 删除角色

### 用户管理
- `GET /api/auth/users/` - 获取用户列表（简化版）
- `GET /api/auth/users-management/` - 获取用户列表（完整版）
- `POST /api/auth/users-management/` - 创建新用户 ⭐
- `GET /api/auth/users-management/{id}/` - 获取用户详情 ⭐
- `PUT /api/auth/users-management/{id}/` - 更新用户信息 ⭐
- `DELETE /api/auth/users-management/{id}/` - 删除用户 ⭐ **已实现**
- `GET /api/auth/users/{id}/roles/` - 获取用户角色
- `POST /api/auth/users/{id}/roles/` - 分配用户角色
- `PUT /api/auth/users/{id}/roles/` - 更新用户角色
- `DELETE /api/auth/users/{id}/roles/{role_id}/` - 移除用户角色

## 🔑 重要权限代码

### 系统管理权限
- `user.list` - 查看用户列表 ⭐ **前端需要这个权限访问系统设置**
- `user.create` - 创建用户
- `user.update` - 更新用户
- `user.delete` - 删除用户

### 角色权限
- `role.list` - 查看角色列表
- `role.create` - 创建角色
- `role.update` - 更新角色
- `role.delete` - 删除角色

### 业务权限
- `vessel_schedule_list` - 船期查询
- `local_fee.list` - 查看费用列表
- `local_fee.detail` - 查看费用详情

## 🎯 前端权限检查

### 基础权限检查
```javascript
function hasPermission(user, userPermissions, requiredPermission) {
    // 超级管理员拥有所有权限
    if (user.is_superuser) {
        return true;
    }

    // 检查具体权限
    return userPermissions.includes(requiredPermission);
}

// 使用示例
const canViewUsers = hasPermission(user, permissions, 'user.list');
if (canViewUsers) {
    // 显示系统设置菜单
} else {
    // 隐藏系统设置菜单
}
```

### 路由权限检查
```javascript
// 路由守卫示例
function checkRoutePermission(route, user, permissions) {
    const routePermissions = {
        '/admin/users': 'user.list',
        '/admin/roles': 'role.list',
        '/admin/permissions': 'permission.list'
    };

    const requiredPermission = routePermissions[route];
    if (!requiredPermission) {
        return true; // 无需特殊权限的路由
    }

    return hasPermission(user, permissions, requiredPermission);
}
```

## 🚨 解决前端错误

### 问题1: is_superuser字段undefined
**原因**: 用户序列化器缺少字段
**解决**: ✅ 已修复，现在登录API返回完整用户信息

### 问题2: 权限检查失败
**检查步骤**:
1. 确认用户已登录: `user.is_authenticated`
2. 检查超级管理员: `user.is_superuser`
3. 检查具体权限: `permissions.includes('user.list')`

### 问题3: 无法访问系统设置
**解决方案**:
1. 确保用户有 `user.list` 权限
2. 或者设置用户为超级管理员: `is_superuser=true`

## 📝 常用操作示例

### 创建角色并分配权限
```bash
# 1. 创建角色
curl -X POST /api/auth/roles/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "系统管理员",
    "description": "可以管理用户和角色",
    "permission_codes": ["user.list", "user.create", "role.list", "role.create"]
  }'

# 2. 分配角色给用户
curl -X POST /api/auth/users/19/roles/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"roles": [1, 2]}'
```

### 设置超级管理员
```python
# Django shell
from authentication.models import User
user = User.objects.get(email='admin3@example.com')
user.is_superuser = True
user.is_staff = True
user.save()
```

## 🔧 调试技巧

### 1. 检查用户权限
```bash
curl -X GET /api/auth/me/permissions/ \
  -H "Authorization: Bearer <token>"
```

### 2. 检查用户信息
```bash
curl -X GET /api/auth/me/ \
  -H "Authorization: Bearer <token>"
```

### 3. 查看所有权限
```bash
curl -X GET /api/auth/permissions/ \
  -H "Authorization: Bearer <token>"
```

## ⚡ 快速修复清单

- [x] 修复用户序列化器缺少 `is_superuser`、`is_staff` 字段
- [x] 设置admin3用户为超级管理员
- [x] 完善权限和角色API文档
- [x] 添加前端权限检查示例
- [x] 提供常见错误解决方案

现在前端应该能够正确获取用户状态信息，进行权限检查，并访问系统设置了！
