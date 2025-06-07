# 船舶航线管理系统 - 文档中心

## 📖 文档概览

欢迎来到船舶航线管理系统的文档中心。本系统是基于Django REST Framework开发的船舶航线管理平台，提供完整的船期管理、本地费用管理和用户权限控制功能。

## 🗂️ 文档结构

### 📋 API文档
- **[API总览](api/README.md)** - API接口总体介绍和使用说明
- **[认证API](api/authentication.md)** - 用户认证、登录、权限管理相关API
- **[船期管理API](api/schedules.md)** - 船舶航线、船舶信息、共舱分组相关API
- **[本地费用API](api/local_fees.md)** - 本地费用管理相关API

### 🔧 模块文档
- **[模块总览](modules/README.md)** - 系统模块架构和功能介绍
- **[认证模块](modules/authentication.md)** - 用户认证和权限系统详细说明
- **[船期管理模块](modules/schedules.md)** - 船期管理核心功能说明
- **[本地费用模块](modules/local_fees.md)** - 本地费用管理功能说明

### 🚀 部署文档
- **[部署总览](deployment/README.md)** - 系统部署概述
- **[安装指南](deployment/installation.md)** - 详细安装步骤
- **[配置说明](deployment/configuration.md)** - 系统配置参数说明

### 💻 开发文档
- **[开发总览](development/README.md)** - 开发环境和规范
- **[开发入门](development/getting_started.md)** - 开发环境搭建和入门指南
- **[测试指南](development/testing.md)** - 测试框架和测试用例说明
- **[权限系统](development/permissions.md)** - 权限系统设计和使用说明

## 🎯 快速导航

### 新用户入门
1. 📖 阅读 [API总览](api/README.md) 了解系统功能
2. 🔧 查看 [安装指南](deployment/installation.md) 搭建环境
3. 🚀 参考 [认证API](api/authentication.md) 开始使用

### 开发者指南
1. 💻 查看 [开发入门](development/getting_started.md) 搭建开发环境
2. 🧪 阅读 [测试指南](development/testing.md) 了解测试规范
3. 🔐 学习 [权限系统](development/permissions.md) 理解权限控制

### API使用者
1. 🔑 从 [认证API](api/authentication.md) 开始获取访问令牌
2. 🚢 使用 [船期管理API](api/schedules.md) 查询和管理船期信息
3. 💰 通过 [本地费用API](api/local_fees.md) 管理费用信息

## 📊 系统特性

### 核心功能
- **🚢 船舶航线管理** - 完整的船期信息管理和查询
- **📊 船舶额外信息** - 价格、舱位、截关时间等补充信息管理
- **🔄 数据同步** - 自动同步船期和额外信息
- **👥 权限管理** - 基于角色的细粒度权限控制
- **🔍 前台查询** - 专用的前台船期查询API
- **💰 本地费用** - 完整的本地费用管理功能

### 技术特性
- **🔐 JWT认证** - 安全的Token认证机制
- **📱 RESTful API** - 标准的REST API设计
- **🎯 权限控制** - 细粒度的权限管理系统
- **📊 数据版本** - 支持数据版本控制
- **🔄 批量操作** - 支持批量创建、更新、删除
- **🌐 中文支持** - 全面的中文错误提示和文档

## 🔗 相关链接

- **项目主页**: [README.md](../README.md)
- **API基础URL**: `http://127.0.0.1:8000/api/`
- **管理后台**: `http://127.0.0.1:8000/admin/`

## 📝 文档维护

本文档与代码同步更新，确保信息的准确性和时效性。如发现文档问题或需要补充内容，请联系开发团队。

**最后更新**: 2025-05-27
**文档版本**: v1.0.0
