# 认证模块文档

## 📋 概述

认证模块是系统的安全核心，负责用户身份验证、权限管理和访问控制。基于Django的用户系统和JWT Token实现，提供完整的用户管理和权限控制功能。

**模块路径**: `authentication/`

## 🏗️ 模块架构

### 核心组件
```
authentication/
├── models.py           # 数据模型定义
├── views.py           # API视图实现
├── serializers.py     # 数据序列化器
├── permissions.py     # 权限控制逻辑
├── managers.py        # 自定义管理器
├── urls.py           # URL路由配置
├── admin.py          # 管理后台配置
└── migrations/       # 数据库迁移文件
```

### 设计模式
- **MVC模式**: 模型-视图-控制器分离
- **权限装饰器**: 基于装饰器的权限控制
- **序列化器模式**: 数据验证和序列化
- **管理器模式**: 自定义查询逻辑

## 📊 数据模型

### 1. User模型 (用户)
```python
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)           # 邮箱（登录用户名）
    first_name = models.CharField(max_length=30)     # 名字
    last_name = models.CharField(max_length=30)      # 姓氏
    is_active = models.BooleanField(default=True)    # 是否激活
    is_staff = models.BooleanField(default=False)    # 是否员工
    is_superuser = models.BooleanField(default=False) # 是否超级用户
    date_joined = models.DateTimeField(auto_now_add=True) # 注册时间
    last_login = models.DateTimeField(null=True)     # 最后登录时间
    roles = models.ManyToManyField('Role')           # 用户角色
```

#### 核心方法
- `get_full_name()` - 获取完整姓名
- `get_short_name()` - 获取简短姓名
- `has_permission(permission_code)` - 检查用户权限
- `get_all_permissions()` - 获取用户所有权限

### 2. Permission模型 (权限)
```python
class Permission(models.Model):
    code = models.CharField(max_length=100, unique=True)  # 权限代码
    name = models.CharField(max_length=100)               # 权限名称
    description = models.TextField()                      # 权限描述
    category = models.CharField(max_length=50)            # 权限分类
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
```

#### 权限分类
- **船期管理** - vessel_schedule.*
- **船舶信息管理** - vessel_info.*
- **本地费用管理** - local_fee.*
- **用户管理** - user.*
- **系统管理** - system.*

### 3. Role模型 (角色)
```python
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)   # 角色名称
    description = models.TextField()                      # 角色描述
    permissions = models.ManyToManyField('Permission')    # 角色权限
    is_active = models.BooleanField(default=True)         # 是否激活
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
```

#### 预定义角色
- **超级管理员** - 所有权限
- **船期管理员** - 船期和船舶信息管理权限
- **业务用户** - 查询和基础操作权限
- **只读用户** - 仅查看权限

## 🔐 认证机制

### JWT Token认证
```python
# Token结构
{
    "token_type": "access",
    "exp": 1716825600,        # 过期时间
    "iat": 1716824700,        # 签发时间
    "jti": "abc123",          # Token ID
    "user_id": 1,             # 用户ID
    "email": "user@example.com",
    "permissions": ["vessel_schedule_list", "vessel_info.list"]
}
```

### Token生命周期
- **访问Token**: 15分钟有效期
- **刷新Token**: 7天有效期
- **自动刷新**: 访问Token过期时自动使用刷新Token获取新Token
- **Token轮换**: 每次刷新都生成新的Token对

### 认证流程
```
1. 用户登录 → 验证邮箱密码
2. 生成Token → 返回访问Token和刷新Token
3. API请求 → 携带访问Token
4. Token验证 → 验证Token有效性和权限
5. Token刷新 → 使用刷新Token获取新的访问Token
```

## 🛡️ 权限系统

### 权限控制架构
```
用户(User) → 角色(Role) → 权限(Permission) → 资源访问
```

### 权限检查机制
```python
# 装饰器权限检查
@permission_classes([HasPermission('vessel_schedule.list')])
def vessel_schedule_list(request):
    pass

# 视图中权限检查
if not request.user.has_permission('vessel_info.create'):
    return Response({'error': '权限不足'}, status=403)
```

### 权限映射表
```python
PERMISSION_MAPPING = {
    'vessel_schedule_list': 'schedules.view_vesselschedule',
    'vessel_schedule_detail': 'schedules.view_vesselschedule',
    'vessel_schedule_create': 'schedules.add_vesselschedule',
    'vessel_schedule_update': 'schedules.change_vesselschedule',
    'vessel_schedule_delete': 'schedules.delete_vesselschedule',
    # ... 更多权限映射
}
```

## 🔧 核心功能

### 1. 用户注册
```python
def register_user(email, password, first_name, last_name):
    """用户注册"""
    # 1. 验证邮箱唯一性
    # 2. 验证密码强度
    # 3. 创建用户记录
    # 4. 分配默认角色
    # 5. 生成JWT Token
    # 6. 返回用户信息和Token
```

### 2. 用户登录
```python
def login_user(email, password):
    """用户登录"""
    # 1. 验证用户凭据
    # 2. 检查用户状态
    # 3. 更新最后登录时间
    # 4. 生成JWT Token
    # 5. 返回用户信息和Token
```

### 3. 权限验证
```python
def check_permission(user, permission_code):
    """权限验证"""
    # 1. 检查超级用户权限
    # 2. 获取用户所有角色
    # 3. 获取角色关联的权限
    # 4. 检查权限代码匹配
    # 5. 返回验证结果
```

### 4. Token管理
```python
def refresh_token(refresh_token):
    """Token刷新"""
    # 1. 验证刷新Token有效性
    # 2. 获取用户信息
    # 3. 生成新的访问Token
    # 4. 可选：生成新的刷新Token
    # 5. 返回新Token
```

## 📡 API接口

### 认证接口
| 端点 | 方法 | 功能 | 权限 |
|------|------|------|------|
| `/auth/register/` | POST | 用户注册 | 无 |
| `/auth/login/` | POST | 用户登录 | 无 |
| `/auth/logout/` | POST | 用户登出 | 认证 |
| `/auth/token/refresh/` | POST | Token刷新 | 无 |

### 用户管理接口
| 端点 | 方法 | 功能 | 权限 |
|------|------|------|------|
| `/auth/me/` | GET | 获取用户信息 | 认证 |
| `/auth/me/permissions/` | GET | 获取用户权限 | 认证 |
| `/auth/user/` | PUT | 更新用户信息 | 认证 |
| `/auth/users/` | GET | 用户列表 | 管理员 |

### 权限管理接口
| 端点 | 方法 | 功能 | 权限 |
|------|------|------|------|
| `/auth/permissions/` | GET | 权限列表 | 管理员 |
| `/auth/roles/` | GET | 角色列表 | 管理员 |
| `/auth/users/{id}/roles/` | GET/POST | 用户角色管理 | 管理员 |

## 🔒 安全特性

### 密码安全
- **加密存储**: 使用Django的PBKDF2算法加密
- **强度验证**: 最少8位，包含字母数字
- **防暴力破解**: 登录失败限制
- **密码重置**: 安全的密码重置流程

### Token安全
- **签名验证**: 使用HMAC-SHA256签名
- **过期控制**: 访问Token短期有效
- **自动轮换**: 定期更换Token
- **黑名单机制**: 支持Token撤销

### 权限安全
- **最小权限原则**: 用户只获得必要权限
- **权限继承**: 角色权限继承机制
- **动态权限**: 支持运行时权限检查
- **审计日志**: 权限操作记录

## 🧪 测试覆盖

### 单元测试
- 用户模型测试
- 权限验证测试
- Token生成测试
- 密码加密测试

### 集成测试
- 登录流程测试
- 权限控制测试
- API认证测试
- 角色权限测试

### 安全测试
- SQL注入测试
- XSS攻击测试
- CSRF保护测试
- 权限绕过测试

## 📝 使用示例

### 用户注册和登录
```python
# 注册用户
user_data = {
    'email': 'user@example.com',
    'password': 'password123',
    'first_name': '张',
    'last_name': '三'
}
response = client.post('/api/auth/register/', user_data)

# 用户登录
login_data = {
    'email': 'user@example.com',
    'password': 'password123'
}
response = client.post('/api/auth/login/', login_data)
token = response.data['tokens']['access']
```

### 权限检查
```python
# 在视图中检查权限
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    if not request.user.has_permission('vessel_schedule.list'):
        return Response({'error': '权限不足'}, status=403)
    
    # 业务逻辑
    return Response({'data': 'success'})
```

### 角色管理
```python
# 创建角色
role = Role.objects.create(
    name='船期管理员',
    description='管理船期和船舶信息'
)

# 分配权限
permissions = Permission.objects.filter(
    code__startswith='vessel_schedule'
)
role.permissions.set(permissions)

# 分配角色给用户
user.roles.add(role)
```

## ⚠️ 注意事项

1. **Token安全**: 客户端应安全存储Token，避免XSS攻击
2. **权限粒度**: 合理设计权限粒度，避免过度复杂
3. **角色设计**: 角色应反映实际业务需求
4. **密码策略**: 定期提醒用户更换密码
5. **审计日志**: 重要操作应记录审计日志
6. **性能优化**: 权限检查应考虑性能影响
