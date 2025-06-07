# 开发入门指南

## 📋 概述

本指南帮助新开发者快速搭建开发环境，了解项目结构，并开始参与船舶航线管理系统的开发工作。

## 🚀 快速开始

### 1. 环境准备

#### 系统要求
- **Python**: 3.8+
- **Git**: 2.30+
- **IDE**: PyCharm / VS Code (推荐)
- **数据库**: MySQL 8.0+ (可选，开发环境可用SQLite)

#### 安装Python和Git
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# macOS (使用Homebrew)
brew install python3 git

# Windows
# 从官网下载安装包：
# Python: https://www.python.org/downloads/
# Git: https://git-scm.com/download/win
```

### 2. 克隆项目

```bash
# 克隆项目代码
git clone <repository-url>
cd ship_schedule_projct

# 查看项目结构
tree -L 2
```

### 3. 创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# 验证虚拟环境
which python
python --version
```

### 4. 安装依赖

```bash
# 升级pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 验证安装
pip list | grep Django
```

### 5. 配置数据库

#### 使用SQLite（推荐开发环境）
```bash
# 执行数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
# 输入邮箱: admin@example.com
# 输入密码: admin123456
```

#### 使用MySQL（可选）
```bash
# 安装MySQL客户端库
pip install mysqlclient

# 创建数据库
mysql -u root -p
CREATE DATABASE ship_schedule_dev CHARACTER SET utf8mb4;
CREATE USER 'dev_user'@'localhost' IDENTIFIED BY 'dev_password';
GRANT ALL PRIVILEGES ON ship_schedule_dev.* TO 'dev_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# 修改settings.py中的数据库配置
# 然后执行迁移
python manage.py migrate
python manage.py createsuperuser
```

### 6. 启动开发服务器

```bash
# 启动Django开发服务器
python manage.py runserver

# 访问应用
# API健康检查: http://127.0.0.1:8000/api/
# 管理后台: http://127.0.0.1:8000/admin/
```

## 🏗️ 项目结构详解

### 核心目录结构
```
ship_schedule_projct/
├── ship_schedule/          # Django项目配置
│   ├── __init__.py
│   ├── settings.py        # 项目设置
│   ├── urls.py           # 主URL配置
│   ├── wsgi.py           # WSGI配置
│   └── asgi.py           # ASGI配置
├── authentication/        # 认证模块
│   ├── models.py         # 用户、角色、权限模型
│   ├── views.py          # 认证相关视图
│   ├── serializers.py    # 数据序列化器
│   ├── permissions.py    # 权限控制逻辑
│   └── urls.py          # 认证URL配置
├── schedules/            # 船期管理模块
│   ├── models.py         # 船期、船舶信息模型
│   ├── views.py          # 船期管理视图
│   ├── serializers.py    # 序列化器
│   └── urls.py          # 船期URL配置
├── local_fees/           # 本地费用模块
│   ├── models.py         # 本地费用模型
│   ├── views.py          # 费用管理视图
│   ├── serializers.py    # 序列化器
│   └── urls.py          # 费用URL配置
├── docs/                 # 项目文档
├── scripts/              # 工具脚本
├── tests/               # 测试用例
├── manage.py            # Django管理脚本
└── requirements.txt     # Python依赖
```

### 关键文件说明

#### settings.py
```python
# 项目核心配置文件
# 包含数据库、缓存、安全、国际化等配置
```

#### models.py
```python
# 数据模型定义
# 定义数据库表结构和业务逻辑
```

#### views.py
```python
# 视图函数/类
# 处理HTTP请求和响应
```

#### serializers.py
```python
# 数据序列化器
# 处理数据验证和格式转换
```

#### urls.py
```python
# URL路由配置
# 定义URL模式和视图映射
```

## 🔧 开发工具配置

### VS Code配置

#### 安装扩展
```bash
# 推荐扩展
- Python
- Django
- GitLens
- REST Client
- SQLite Viewer
```

#### 配置文件 (.vscode/settings.json)
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".venv": true
    },
    "emmet.includeLanguages": {
        "django-html": "html"
    }
}
```

### PyCharm配置

#### 项目设置
1. 打开项目目录
2. 设置Python解释器为虚拟环境
3. 配置Django设置
4. 启用代码检查和格式化

#### Django配置
```
File → Settings → Languages & Frameworks → Django
- Enable Django Support: ✓
- Django project root: /path/to/ship_schedule_projct
- Settings: ship_schedule/settings.py
- Manage script: manage.py
```

## 🧪 开发测试

### 运行测试
```bash
# 运行所有测试
python manage.py test

# 运行特定应用测试
python manage.py test authentication
python manage.py test schedules
python manage.py test local_fees

# 运行特定测试类
python manage.py test authentication.tests.UserModelTest

# 运行特定测试方法
python manage.py test authentication.tests.UserModelTest.test_create_user
```

### 测试覆盖率
```bash
# 安装coverage
pip install coverage

# 运行测试并生成覆盖率报告
coverage run --source='.' manage.py test
coverage report
coverage html  # 生成HTML报告
```

### API测试
```bash
# 使用curl测试API
# 健康检查
curl http://127.0.0.1:8000/api/

# 用户登录
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123456"}'

# 使用Token访问API
curl -X GET http://127.0.0.1:8000/api/schedules/ \
  -H "Authorization: Bearer <your_token>"
```

## 📝 开发规范

### 代码风格
```python
# 遵循PEP 8规范
# 使用black进行代码格式化
black .

# 使用isort整理导入
isort .

# 使用flake8检查代码质量
flake8 .
```

### Git提交规范
```bash
# 提交信息格式
git commit -m "feat(schedules): 添加船期查询API"
git commit -m "fix(auth): 修复登录权限检查问题"
git commit -m "docs: 更新API文档"

# 提交前检查
git status
git diff
python manage.py test
```

### 分支管理
```bash
# 创建功能分支
git checkout -b feature/vessel-search

# 开发完成后
git add .
git commit -m "feat: 实现船舶搜索功能"
git push origin feature/vessel-search

# 创建Pull Request
```

## 🔍 调试技巧

### Django调试
```python
# 在代码中添加断点
import pdb; pdb.set_trace()

# 使用Django shell
python manage.py shell

# 查看SQL查询
from django.db import connection
print(connection.queries)

# 使用Django调试工具栏
pip install django-debug-toolbar
```

### 日志调试
```python
import logging

logger = logging.getLogger(__name__)

def my_view(request):
    logger.info("处理请求开始")
    logger.debug(f"请求参数: {request.GET}")
    # 业务逻辑
    logger.info("处理请求完成")
```

### 数据库调试
```bash
# 查看数据库结构
python manage.py dbshell

# 查看迁移状态
python manage.py showmigrations

# 生成SQL语句
python manage.py sqlmigrate authentication 0001
```

## 📚 学习资源

### Django官方文档
- [Django文档](https://docs.djangoproject.com/)
- [Django REST Framework文档](https://www.django-rest-framework.org/)

### 项目相关文档
- [API文档](../api/README.md)
- [模块文档](../modules/README.md)
- [权限系统](permissions.md)
- [测试指南](testing.md)

### 推荐教程
- Django官方教程
- DRF官方教程
- Python最佳实践指南

## 🤝 开发协作

### 代码审查
- 创建Pull Request前确保测试通过
- 代码审查关注功能、性能、安全性
- 及时响应审查意见

### 问题反馈
- 使用GitHub Issues报告问题
- 提供详细的问题描述和复现步骤
- 包含相关的错误日志和环境信息

### 文档维护
- 新功能开发时同步更新文档
- 修复问题时更新相关说明
- 定期检查文档的准确性

## ⚠️ 常见问题

### 1. 虚拟环境问题
```bash
# 虚拟环境未激活
source .venv/bin/activate

# 依赖安装失败
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. 数据库连接问题
```bash
# 检查数据库服务状态
sudo systemctl status mysql

# 检查数据库配置
python manage.py check --database default
```

### 3. 端口占用问题
```bash
# 查看端口占用
lsof -i :8000

# 使用其他端口
python manage.py runserver 8001
```

### 4. 权限问题
```bash
# 检查文件权限
ls -la

# 修复权限
chmod +x manage.py
```

## 🔗 相关链接

- **[开发文档总览](README.md)** - 开发指南概述
- **[测试指南](testing.md)** - 测试框架使用
- **[权限系统](permissions.md)** - 权限设计说明
- **[API文档](../api/README.md)** - API接口文档
- **[部署指南](../deployment/README.md)** - 部署相关文档
