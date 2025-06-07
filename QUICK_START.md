# 🚢 船期管理系统 - 快速开始指南

## 🚀 一键部署

```bash
# 克隆项目后，直接运行部署脚本
./deploy.sh
```

部署完成后，系统会自动创建默认管理员账户供您立即使用。

## 🔑 默认管理员账户

### 登录信息
- **前端地址**: http://localhost
- **邮箱**: `admin@admin.com`
- **密码**: `admin123@`

### 功能权限
默认管理员拥有系统所有权限，包括：
- ✅ 用户管理
- ✅ 角色权限管理
- ✅ 船舶航线查询与管理
- ✅ 本地费用管理
- ✅ 系统配置

## 📋 首次登录步骤

### 1. 访问系统
打开浏览器访问 http://localhost

### 2. 登录系统
- 在登录页面输入默认管理员邮箱: `admin@admin.com`
- 输入密码: `admin123@`
- 点击登录

### 3. 修改默认密码 (重要!)
登录后请立即修改默认密码：
1. 点击右上角用户头像
2. 选择"个人资料"
3. 修改密码为强密码
4. 保存更改

### 4. 创建新管理员 (推荐)
1. 进入"用户管理"
2. 创建新的管理员账户
3. 分配"超级管理员"角色
4. 使用新账户登录
5. 删除默认账户

## 🔧 系统管理

### 用户管理
- **路径**: 管理后台 → 用户管理
- **功能**: 创建、编辑、删除用户账户
- **权限**: 分配角色和权限

### 角色管理
- **路径**: 管理后台 → 角色管理
- **功能**: 创建和管理用户角色
- **默认角色**:
  - `超级管理员`: 拥有所有权限
  - `普通用户`: 基本查询权限

### 数据管理
- **船舶航线**: 查看和管理船期数据
- **本地费用**: 管理港口费用信息
- **数据导入**: 支持批量数据导入

## 🛠️ 开发和调试

### 查看日志
```bash
# 查看后端应用日志
docker-compose logs -f web

# 查看数据库日志
docker-compose logs -f db

# 查看所有服务日志
docker-compose logs -f
```

### 进入容器
```bash
# 进入后端容器
docker-compose exec web bash

# 进入数据库容器
docker-compose exec db bash
```

### API测试
```bash
# 测试登录API
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@admin.com","password":"admin123@"}'

# 测试船期API (需要token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/schedules/
```

## 🔐 安全建议

### 生产环境部署
1. **修改默认密码**: 立即更改默认管理员密码
2. **删除默认账户**: 创建新管理员后删除默认账户
3. **使用强密码**: 密码应包含大小写字母、数字和特殊字符
4. **启用HTTPS**: 生产环境配置SSL证书
5. **定期备份**: 设置数据库定期备份

### 网络安全
- 生产环境不要暴露数据库端口(3307)
- 配置防火墙规则
- 使用反向代理(Nginx)
- 定期更新系统和依赖

## 📞 技术支持

### 常见问题
1. **无法访问系统**: 检查Docker服务是否正常运行
2. **登录失败**: 确认使用正确的邮箱和密码
3. **数据库连接错误**: 等待数据库完全启动(约30秒)

### 服务管理
```bash
# 重启所有服务
docker-compose restart

# 停止服务
docker-compose down

# 重新构建并启动
docker-compose up --build -d

# 查看服务状态
docker-compose ps
```

### 数据持久化
系统数据存储在Docker volume中，即使重启容器数据也不会丢失：
- `mysql_data`: 数据库数据
- `redis_data`: 缓存数据
- `./ship_schedule_projct/media`: 用户上传文件
- `./ship_schedule_projct/logs`: 系统日志

## 🌟 开始使用

现在您可以使用默认管理员账户 `admin@admin.com` 登录系统开始管理船期数据了！

记住：**安全第一，请及时修改默认密码！** 🔒