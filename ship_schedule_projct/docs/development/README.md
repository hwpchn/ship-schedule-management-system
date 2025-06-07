# 开发文档总览

## 📋 概述

本文档为船舶航线管理系统的开发者提供完整的开发指南，包括开发环境搭建、编码规范、测试指南和权限系统说明。

## 🎯 开发环境

### 技术栈
- **后端**: Django 4.2.7 + Django REST Framework 3.14.0
- **数据库**: MySQL 8.0+ / SQLite (开发环境)
- **缓存**: Redis 6.0+
- **认证**: JWT Token (djangorestframework-simplejwt 5.3.0)
- **API文档**: Django REST Framework自动生成
- **测试**: Django TestCase + pytest

### 开发工具
- **IDE**: PyCharm / VS Code
- **版本控制**: Git
- **API测试**: Postman / curl
- **数据库管理**: MySQL Workbench / phpMyAdmin
- **代码质量**: flake8 / black / isort

## 📚 文档结构

### 开发指南
- **[开发入门](getting_started.md)** - 开发环境搭建和项目结构介绍
- **[测试指南](testing.md)** - 测试框架使用和测试用例编写
- **[权限系统](permissions.md)** - 权限系统设计和使用说明

### 编码规范
- **Python代码规范** - 遵循PEP 8标准
- **Django最佳实践** - Django框架使用规范
- **API设计规范** - RESTful API设计原则
- **数据库设计规范** - 数据模型设计原则

## 🏗️ 项目架构

### 目录结构
```
ship_schedule_projct/
├── 🔧 核心应用
│   ├── ship_schedule/      # Django项目设置
│   ├── authentication/    # 用户认证和权限管理
│   ├── schedules/         # 船期管理核心模块
│   ├── local_fees/        # 本地费用管理模块
│   └── manage.py          # Django管理脚本
├── 📚 文档系统
│   ├── docs/              # 详细文档目录
│   │   ├── api/           # API文档
│   │   ├── modules/       # 模块文档
│   │   ├── deployment/    # 部署文档
│   │   └── development/   # 开发文档
│   └── README.md          # 项目总览
├── 🛠️ 工具脚本
│   ├── scripts/testing/   # 测试脚本集合
│   ├── scripts/debugging/ # 调试分析工具
│   └── scripts/maintenance/ # 维护管理工具
├── 🧪 测试套件
│   └── tests/             # 正式测试用例
└── 📝 配置文件
    ├── requirements.txt   # Python依赖
    ├── .gitignore        # Git忽略文件
    └── .env.example      # 环境变量示例
```

### 模块依赖关系
```
ship_schedule (项目配置)
    ├── authentication (认证模块)
    ├── schedules (船期管理)
    │   └── 依赖 authentication
    └── local_fees (本地费用)
        └── 依赖 authentication
```

## 🔧 开发流程

### 标准开发流程
```
1. 需求分析 → 2. 设计方案 → 3. 编码实现 → 4. 单元测试 → 5. 集成测试 → 6. 代码审查 → 7. 部署上线
```

### Git工作流
```
1. 创建功能分支 → 2. 开发功能 → 3. 提交代码 → 4. 创建PR → 5. 代码审查 → 6. 合并主分支
```

#### 分支命名规范
- **feature/功能名称** - 新功能开发
- **bugfix/问题描述** - Bug修复
- **hotfix/紧急修复** - 紧急修复
- **refactor/重构内容** - 代码重构

#### 提交信息规范
```
类型(范围): 简短描述

详细描述（可选）

相关Issue: #123
```

类型说明：
- **feat**: 新功能
- **fix**: Bug修复
- **docs**: 文档更新
- **style**: 代码格式调整
- **refactor**: 代码重构
- **test**: 测试相关
- **chore**: 构建过程或辅助工具的变动

## 📝 编码规范

### Python代码规范
```python
# 导入顺序
import os
import sys
from datetime import datetime

from django.db import models
from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.response import Response

from .models import VesselSchedule
from .serializers import VesselScheduleSerializer

# 类定义
class VesselScheduleViewSet(viewsets.ModelViewSet):
    """
    船舶航线视图集
    
    提供船舶航线的CRUD操作
    """
    queryset = VesselSchedule.objects.all()
    serializer_class = VesselScheduleSerializer
    
    def list(self, request):
        """获取航线列表"""
        # 实现逻辑
        pass

# 函数定义
def calculate_duration(start_date, end_date):
    """
    计算航程时间
    
    Args:
        start_date (datetime): 开始日期
        end_date (datetime): 结束日期
        
    Returns:
        int: 航程天数
    """
    return (end_date - start_date).days
```

### Django最佳实践
```python
# 模型定义
class VesselSchedule(models.Model):
    """船舶航线模型"""
    
    # 字段定义
    vessel = models.CharField(
        max_length=100,
        verbose_name="船名",
        help_text="船舶名称"
    )
    
    class Meta:
        db_table = 'vessel_schedule'
        verbose_name = '船舶航线'
        verbose_name_plural = '船舶航线'
        ordering = ['-fetch_date']
        
    def __str__(self):
        return f"{self.vessel} {self.voyage}"
    
    def clean(self):
        """模型验证"""
        if self.polCd == self.podCd:
            raise ValidationError("起运港和目的港不能相同")

# 视图定义
class VesselScheduleListView(generics.ListAPIView):
    """船舶航线列表视图"""
    
    queryset = VesselSchedule.objects.filter(status=1)
    serializer_class = VesselScheduleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['polCd', 'podCd', 'carriercd']
    search_fields = ['vessel', 'voyage']
```

### API设计规范
```python
# URL设计
urlpatterns = [
    # 资源集合
    path('schedules/', VesselScheduleListCreateView.as_view()),
    
    # 单个资源
    path('schedules/<int:pk>/', VesselScheduleDetailView.as_view()),
    
    # 子资源
    path('schedules/<int:pk>/vessel-info/', VesselInfoView.as_view()),
    
    # 操作
    path('schedules/cabin-grouping/', cabin_grouping_view),
]

# 响应格式
def api_response(success=True, message="", data=None, status_code=200):
    """标准API响应格式"""
    return Response({
        'success': success,
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }, status=status_code)
```

## 🧪 测试策略

### 测试类型
- **单元测试** - 测试单个函数或方法
- **集成测试** - 测试模块间交互
- **API测试** - 测试API接口
- **功能测试** - 测试完整业务流程

### 测试覆盖率要求
- **总体覆盖率**: ≥90%
- **核心业务逻辑**: 100%
- **API接口**: 100%
- **权限控制**: 100%

### 测试命名规范
```python
class TestVesselScheduleModel(TestCase):
    """船舶航线模型测试"""
    
    def test_create_vessel_schedule_success(self):
        """测试成功创建船舶航线"""
        pass
    
    def test_create_vessel_schedule_with_invalid_data_should_fail(self):
        """测试使用无效数据创建船舶航线应该失败"""
        pass
    
    def test_vessel_schedule_str_representation(self):
        """测试船舶航线字符串表示"""
        pass
```

## 🔐 权限系统

### 权限设计原则
- **最小权限原则** - 用户只获得必要的权限
- **角色基础访问控制** - 基于角色分配权限
- **细粒度控制** - 支持操作级别的权限控制
- **动态权限检查** - 运行时权限验证

### 权限命名规范
```
模块.操作
例如：
- vessel_schedule.list
- vessel_schedule.create
- vessel_schedule.update
- vessel_schedule.delete
- vessel_info.list
- vessel_info.create
```

## 📊 性能优化

### 数据库优化
- 合理使用数据库索引
- 避免N+1查询问题
- 使用select_related和prefetch_related
- 分页查询大数据集

### 缓存策略
- 缓存频繁查询的数据
- 使用Redis缓存热点数据
- 设置合理的缓存过期时间
- 缓存失效策略

### API优化
- 响应数据压缩
- 合理的分页大小
- 批量操作支持
- 异步处理长时间任务

## 🔧 开发工具配置

### VS Code配置
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

### PyCharm配置
- 设置Python解释器为虚拟环境
- 配置代码格式化工具
- 启用代码检查
- 配置测试运行器

## 📋 开发检查清单

### 代码提交前检查
- [ ] 代码符合规范
- [ ] 单元测试通过
- [ ] 代码覆盖率达标
- [ ] 文档更新完成
- [ ] 无明显性能问题

### 功能开发检查
- [ ] 需求理解正确
- [ ] 设计方案合理
- [ ] 错误处理完善
- [ ] 权限控制正确
- [ ] 日志记录完整

### 发布前检查
- [ ] 所有测试通过
- [ ] 性能测试通过
- [ ] 安全检查通过
- [ ] 文档更新完成
- [ ] 部署脚本测试

## 🔗 相关链接

- **[开发入门指南](getting_started.md)** - 快速开始开发
- **[测试指南](testing.md)** - 测试框架和用例
- **[权限系统说明](permissions.md)** - 权限设计和使用
- **[API文档](../api/README.md)** - API接口文档
- **[模块文档](../modules/README.md)** - 模块架构说明

## 📞 开发支持

如果在开发过程中遇到问题，请：

1. 查看相关文档和代码注释
2. 运行测试用例验证功能
3. 查看日志文件获取错误信息
4. 联系开发团队或提交Issue

**开发团队邮箱**: dev@example.com  
**技术讨论群**: 开发者微信群
