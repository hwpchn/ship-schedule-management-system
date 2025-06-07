# GitHub仓库设置指南

## 📋 创建远程仓库步骤

### 1. 在GitHub创建仓库

1. **访问GitHub**: https://github.com
2. **登录账户**: 使用您的GitHub账户登录
3. **创建新仓库**: 点击右上角的 "+" 号，选择 "New repository"
4. **填写仓库信息**:
   - **Repository name**: `ship-schedule-management`
   - **Description**: `船舶航线管理系统 - 基于Django REST Framework的船期管理、本地费用管理和用户权限控制平台`
   - **Visibility**: Public (或根据需要选择Private)
   - **Initialize**: ❌ 不要勾选任何初始化选项
5. **创建仓库**: 点击 "Create repository"

### 2. 连接本地仓库到远程仓库

```bash
# 进入项目目录
cd /Users/huangcc/work_5.27/ship_schedule_projct

# 添加远程仓库 (请将 hwpchn 替换为您的实际GitHub用户名)
git remote add origin https://github.com/hwpchn/ship-schedule-management.git

# 推送到远程仓库
git push -u origin main
```

### 3. 验证推送

```bash
# 检查远程仓库连接
git remote -v

# 查看推送状态
git status

# 查看提交历史
git log --oneline
```

## 🎯 仓库信息

- **仓库名称**: ship-schedule-management
- **描述**: 船舶航线管理系统 - 基于Django REST Framework的船期管理、本地费用管理和用户权限控制平台
- **主要功能**:
  - 🚢 船舶航线管理
  - 💰 本地费用管理
  - 🔐 用户认证和权限控制
  - 📚 完整的API文档
  - 🛠️ 开发和部署工具

## 📚 项目特色

### 核心功能
- **船期管理**: 船舶航线CRUD、共舱分组查询、前台船期查询API
- **费用管理**: 多种计费方式、多货币支持、前台费用查询
- **权限系统**: JWT认证、RBAC权限控制、细粒度权限管理

### 技术栈
- **后端**: Django 4.2.7 + Django REST Framework 3.14.0
- **认证**: JWT Token (djangorestframework-simplejwt 5.3.0)
- **数据库**: MySQL 8.0+ / SQLite (开发环境)
- **缓存**: Redis 6.0+
- **文档**: 完整的API和开发文档

### 文档体系
- **API文档**: 认证、船期管理、本地费用API
- **模块文档**: 系统架构和模块说明
- **部署文档**: 安装指南和配置说明
- **开发文档**: 开发入门、测试指南、权限系统

## 🚀 快速开始

```bash
# 克隆项目
git clone https://github.com/hwpchn/ship-schedule-management.git
cd ship-schedule-management

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

## 📞 联系方式

- **开发者**: hwpchn
- **邮箱**: hwpchn@gmail.com
- **GitHub**: https://github.com/hwpchn

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
