# 🚢 船舶调度管理系统 - 本地运行指南

由于Docker Hub网络问题，推荐使用本地运行方式测试系统。

## 🚀 快速启动

### 1. 启动后端服务

```bash
cd /Users/huangcc/work_5.27
./run-local.sh
```

这会：
- ✅ 检查MySQL连接
- ✅ 创建虚拟环境
- ✅ 安装Python依赖
- ✅ 运行数据库迁移
- ✅ 创建管理员用户 (admin/admin123)
- ✅ 启动后端API服务 (http://localhost:8000)

### 2. 启动前端服务（新终端）

```bash
cd /Users/huangcc/work_5.27
./run-frontend.sh
```

这会：
- ✅ 安装前端依赖
- ✅ 启动Vue开发服务器 (http://localhost:3000)
- ✅ 自动代理API请求到后端

## 📋 服务访问

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:8000/api/
- **管理后台**: http://localhost:8000/admin/
- **管理员账号**: admin / admin123

## 🔧 API测试

```bash
# 测试API连接
curl http://localhost:8000/api/schedules/

# 测试用户认证
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## 📝 注意事项

1. **确保MySQL运行**: 本地MySQL服务必须在3306端口运行
2. **数据库配置**: 使用现有的.env配置 (root/099118)
3. **端口使用**: 
   - 后端: 8000
   - 前端: 3000
   - MySQL: 3306

## 🛠 故障排除

### 后端启动失败
```bash
# 检查MySQL连接
mysql -u root -p099118 -e "SELECT 1;"

# 查看详细错误
cd ship_schedule_projct
source venv/bin/activate
python manage.py check
```

### 前端启动失败
```bash
# 重新安装依赖
cd ship-schedule-management-ui
rm -rf node_modules
pnpm install
```

### 数据库连接问题
```bash
# 检查MySQL状态
brew services list | grep mysql

# 启动MySQL (如果使用brew)
brew services start mysql
```

## 🔄 Docker方案（网络恢复后）

当Docker Hub网络恢复正常后，可以使用：

```bash
# 简化Docker部署
./deploy-simple.sh

# 或完整Docker部署
./deploy.sh
```

---

现在可以运行 `./run-local.sh` 开始测试后端服务！