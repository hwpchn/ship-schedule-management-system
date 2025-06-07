#!/bin/bash

# 船舶调度管理系统 - Docker测试部署脚本

set -e

echo "🚢 开始测试部署船舶调度管理系统..."

# 检查Docker和Docker Compose是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 检查.env文件是否存在
if [ ! -f "ship_schedule_projct/.env" ]; then
    echo "❌ 未找到ship_schedule_projct/.env文件"
    exit 1
fi

echo "✅ 使用现有的.env配置文件"

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p ship_schedule_projct/logs
mkdir -p ship_schedule_projct/media/user_avatars
mkdir -p ship_schedule_projct/static

# 停止并删除现有容器
echo "🛑 停止现有服务..."
docker-compose down

# 构建并启动服务
echo "🔨 构建并启动服务..."
docker-compose up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 等待数据库准备就绪
echo "📊 等待数据库准备就绪..."
until docker-compose exec -T db mysqladmin ping -h"localhost" -u root -p099118 --silent; do
    echo "等待数据库启动..."
    sleep 2
done

echo "✅ 部署完成！"
echo ""
echo "🌐 访问地址："
echo "   ┌─────────────────────────────────────────┐"
echo "   │  🖥️  前端系统: http://localhost          │"
echo "   │  🔧  后端API:  http://localhost:8000     │"
echo "   │  ⚙️   管理后台: http://localhost:8000/admin │"
echo "   └─────────────────────────────────────────┘"
echo ""
echo "🔑 默认管理员账户："
echo "   ┌─────────────────────────────────────────┐"
echo "   │  📧  邮箱: admin@admin.com              │"
echo "   │  🔐  密码: admin123@                    │"
echo "   └─────────────────────────────────────────┘"
echo ""
echo "⚠️  重要提醒："
echo "   • 请在首次登录后立即修改默认密码"
echo "   • 建议创建新的管理员账户后删除默认账户"
echo "   • 生产环境请使用强密码策略"
echo ""
echo "📊 服务端口信息："
echo "   • MySQL数据库: 3307 (避免与本地MySQL冲突)"
echo "   • Redis缓存: 6380 (避免与本地Redis冲突)"
echo ""
echo "🔧 常用管理命令："
echo "   • 查看后端日志: docker-compose logs -f web"
echo "   • 查看所有日志: docker-compose logs -f"
echo "   • 重启服务: docker-compose restart"
echo "   • 停止服务: docker-compose down"
echo "   • 进入后端容器: docker-compose exec web bash"
echo ""
echo "🧪 API测试："
echo "   • curl http://localhost:8000/api/auth/login/"
echo "   • curl http://localhost:8000/api/schedules/"