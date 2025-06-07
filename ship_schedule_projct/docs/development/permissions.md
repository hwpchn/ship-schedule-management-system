# 权限系统说明

## 📋 概述

船舶航线管理系统采用基于角色的访问控制（RBAC）模型，提供细粒度的权限管理功能。权限系统确保不同用户只能访问其被授权的资源和操作。

## 🏗️ 权限架构

### 权限模型
```
用户(User) ←→ 角色(Role) ←→ 权限(Permission) → 资源访问
```

### 核心组件
- **User** - 系统用户
- **Role** - 用户角色
- **Permission** - 具体权限
- **PermissionMapping** - 权限映射表

## 📊 数据模型

### Permission模型
```python
class Permission(models.Model):
    code = models.CharField(max_length=100, unique=True)  # 权限代码
    name = models.CharField(max_length=100)               # 权限名称
    description = models.TextField()                      # 权限描述
    category = models.CharField(max_length=50)            # 权限分类
    created_at = models.DateTimeField(auto_now_add=True)
```

### Role模型
```python
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)   # 角色名称
    description = models.TextField()                      # 角色描述
    permissions = models.ManyToManyField('Permission')    # 角色权限
    is_active = models.BooleanField(default=True)         # 是否激活
    created_at = models.DateTimeField(auto_now_add=True)
```

### User扩展
```python
class User(AbstractBaseUser, PermissionsMixin):
    # ... 其他字段
    roles = models.ManyToManyField('Role')                # 用户角色
    
    def has_permission(self, permission_code):
        """检查用户是否拥有特定权限"""
        if self.is_superuser:
            return True
        
        user_permissions = self.get_all_permissions()
        return permission_code in user_permissions
    
    def get_all_permissions(self):
        """获取用户所有权限"""
        permissions = set()
        for role in self.roles.filter(is_active=True):
            for permission in role.permissions.all():
                permissions.add(permission.code)
        return permissions
```

## 🔑 权限分类

### 船期管理权限
| 权限代码 | 权限名称 | 描述 |
|----------|----------|------|
| vessel_schedule.list | 船期列表查看 | 查看船舶航线列表 |
| vessel_schedule.detail | 船期详情查看 | 查看船舶航线详情 |
| vessel_schedule.create | 船期创建 | 创建新的船舶航线 |
| vessel_schedule.update | 船期更新 | 修改船舶航线信息 |
| vessel_schedule.delete | 船期删除 | 删除船舶航线 |
| vessel_schedule_list | 前台船期查询 | 前台船期查询专用权限 |

### 船舶信息管理权限
| 权限代码 | 权限名称 | 描述 |
|----------|----------|------|
| vessel_info.list | 船舶信息列表 | 查看船舶额外信息列表 |
| vessel_info.detail | 船舶信息详情 | 查看船舶额外信息详情 |
| vessel_info.create | 船舶信息创建 | 创建船舶额外信息 |
| vessel_info.update | 船舶信息更新 | 修改船舶额外信息 |
| vessel_info.delete | 船舶信息删除 | 删除船舶额外信息 |
| vessel_info.query | 船舶信息查询 | 查询特定船舶信息 |

### 本地费用管理权限
| 权限代码 | 权限名称 | 描述 |
|----------|----------|------|
| local_fee.list | 本地费用列表 | 查看本地费用列表 |
| local_fee.detail | 本地费用详情 | 查看本地费用详情 |
| local_fee.create | 本地费用创建 | 创建本地费用 |
| local_fee.update | 本地费用更新 | 修改本地费用 |
| local_fee.delete | 本地费用删除 | 删除本地费用 |
| local_fee.query | 本地费用查询 | 前台费用查询专用权限 |

### 用户管理权限
| 权限代码 | 权限名称 | 描述 |
|----------|----------|------|
| user.list | 用户列表 | 查看用户列表 |
| user.detail | 用户详情 | 查看用户详情 |
| user.create | 用户创建 | 创建新用户 |
| user.update | 用户更新 | 修改用户信息 |
| user.delete | 用户删除 | 删除用户 |
| user.role_manage | 用户角色管理 | 管理用户角色分配 |

## 👥 预定义角色

### 超级管理员
```python
{
    "name": "超级管理员",
    "description": "拥有系统所有权限",
    "permissions": ["*"]  # 所有权限
}
```

### 船期管理员
```python
{
    "name": "船期管理员",
    "description": "管理船期和船舶信息",
    "permissions": [
        "vessel_schedule.*",
        "vessel_info.*",
        "vessel_schedule_list"
    ]
}
```

### 业务用户
```python
{
    "name": "业务用户",
    "description": "基础业务操作权限",
    "permissions": [
        "vessel_schedule.list",
        "vessel_schedule.detail",
        "vessel_schedule_list",
        "vessel_info.list",
        "vessel_info.detail",
        "vessel_info.query",
        "local_fee.list",
        "local_fee.detail",
        "local_fee.query"
    ]
}
```

### 只读用户
```python
{
    "name": "只读用户",
    "description": "仅查看权限",
    "permissions": [
        "vessel_schedule.list",
        "vessel_schedule.detail",
        "vessel_info.list",
        "vessel_info.detail",
        "local_fee.list",
        "local_fee.detail"
    ]
}
```

## 🔧 权限实现

### 权限装饰器
```python
from authentication.permissions import HasPermission

class VesselScheduleViewSet(viewsets.ModelViewSet):
    """船舶航线视图集"""
    
    def get_permissions(self):
        """根据操作设置权限"""
        if self.action == 'list':
            return [HasPermission('vessel_schedule.list')]
        elif self.action == 'create':
            return [HasPermission('vessel_schedule.create')]
        elif self.action == 'update':
            return [HasPermission('vessel_schedule.update')]
        elif self.action == 'destroy':
            return [HasPermission('vessel_schedule.delete')]
        else:
            return [HasPermission('vessel_schedule.detail')]
```

### 函数级权限检查
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cabin_grouping_api(request):
    """共舱分组API"""
    # 检查权限
    if not request.user.has_permission('vessel_schedule_list'):
        return Response({
            'success': False,
            'message': '没有权限访问此功能'
        }, status=403)
    
    # 业务逻辑
    pass
```

### 权限映射机制
```python
# 权限映射表
PERMISSION_MAPPING = {
    # 船期管理权限映射
    'vessel_schedule_list': 'schedules.view_vesselschedule',
    'vessel_schedule_detail': 'schedules.view_vesselschedule',
    'vessel_schedule_create': 'schedules.add_vesselschedule',
    'vessel_schedule_update': 'schedules.change_vesselschedule',
    'vessel_schedule_delete': 'schedules.delete_vesselschedule',
    
    # 船舶信息权限映射
    'vessel_info_list': 'schedules.view_vesselinfofromcompany',
    'vessel_info_create': 'schedules.add_vesselinfofromcompany',
    'vessel_info_update': 'schedules.change_vesselinfofromcompany',
    'vessel_info_delete': 'schedules.delete_vesselinfofromcompany',
    
    # 本地费用权限映射
    'local_fee_list': 'local_fees.view_localfee',
    'local_fee_create': 'local_fees.add_localfee',
    'local_fee_update': 'local_fees.change_localfee',
    'local_fee_delete': 'local_fees.delete_localfee',
}

def get_permission_map():
    """获取权限映射表"""
    return PERMISSION_MAPPING
```

## 🛡️ 权限检查流程

### API请求权限验证
```
1. 请求到达 → 2. JWT Token验证 → 3. 用户身份确认 → 4. 权限检查 → 5. 业务逻辑执行
```

### 权限检查实现
```python
class HasPermission(permissions.BasePermission):
    """自定义权限检查类"""
    
    def __init__(self, permission_code):
        self.permission_code = permission_code
    
    def has_permission(self, request, view):
        """检查用户权限"""
        # 检查用户是否已认证
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 超级用户拥有所有权限
        if request.user.is_superuser:
            return True
        
        # 检查具体权限
        return request.user.has_permission(self.permission_code)
```

## 🔄 权限管理操作

### 创建角色和权限
```python
# 创建权限
permission = Permission.objects.create(
    code='vessel_schedule.list',
    name='船期列表查看',
    description='查看船舶航线列表',
    category='船期管理'
)

# 创建角色
role = Role.objects.create(
    name='船期查询员',
    description='负责船期查询工作'
)

# 分配权限给角色
role.permissions.add(permission)

# 分配角色给用户
user.roles.add(role)
```

### 权限检查示例
```python
# 检查用户是否有特定权限
if user.has_permission('vessel_schedule.list'):
    # 执行相应操作
    pass

# 获取用户所有权限
user_permissions = user.get_all_permissions()
print(user_permissions)
# 输出: {'vessel_schedule.list', 'vessel_info.list', ...}
```

## 🧪 权限测试

### 权限测试用例
```python
class PermissionTestCase(TestCase):
    """权限系统测试"""
    
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.permission = Permission.objects.create(
            code='vessel_schedule.list',
            name='船期列表查看',
            category='船期管理'
        )
        
        self.role = Role.objects.create(
            name='测试角色',
            description='测试用角色'
        )
        self.role.permissions.add(self.permission)
        self.user.roles.add(self.role)
    
    def test_user_has_permission(self):
        """测试用户权限检查"""
        self.assertTrue(self.user.has_permission('vessel_schedule.list'))
        self.assertFalse(self.user.has_permission('vessel_schedule.create'))
    
    def test_api_permission_check(self):
        """测试API权限检查"""
        self.client.force_authenticate(user=self.user)
        
        # 有权限的请求应该成功
        response = self.client.get('/api/schedules/')
        self.assertEqual(response.status_code, 200)
        
        # 无权限的请求应该被拒绝
        response = self.client.post('/api/schedules/', {})
        self.assertEqual(response.status_code, 403)
```

## 📊 权限监控

### 权限使用统计
```python
def get_permission_usage_stats():
    """获取权限使用统计"""
    stats = {}
    
    for permission in Permission.objects.all():
        # 统计拥有此权限的用户数
        user_count = User.objects.filter(
            roles__permissions=permission
        ).distinct().count()
        
        stats[permission.code] = {
            'name': permission.name,
            'user_count': user_count,
            'category': permission.category
        }
    
    return stats
```

### 权限审计日志
```python
import logging

permission_logger = logging.getLogger('permissions')

def log_permission_check(user, permission_code, result):
    """记录权限检查日志"""
    permission_logger.info(
        f"用户 {user.email} 检查权限 {permission_code}: {result}"
    )
```

## ⚠️ 注意事项

1. **权限粒度**: 权限设计要平衡安全性和易用性
2. **角色设计**: 角色应该反映实际业务需求
3. **权限继承**: 避免复杂的权限继承关系
4. **性能考虑**: 权限检查要考虑性能影响
5. **缓存策略**: 可以缓存用户权限信息提高性能
6. **审计要求**: 重要权限操作需要记录审计日志

## 🔗 相关链接

- **[认证API文档](../api/authentication.md)** - 认证相关API
- **[认证模块文档](../modules/authentication.md)** - 认证模块详细说明
- **[开发入门指南](getting_started.md)** - 开发环境搭建
- **[测试指南](testing.md)** - 测试框架使用
