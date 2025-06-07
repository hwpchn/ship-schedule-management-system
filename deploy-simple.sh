#!/bin/bash

# 船舶调度管理系统 - 简化Docker部署脚本（使用本地数据库）

set -e

echo "🚢 开始简化部署船舶调度管理系统（使用本地数据库）..."

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

# 检查本地MySQL是否运行
echo "🔍 检查本地MySQL连接..."
if mysql -u root -p099118 -e "SELECT 1;" 2>/dev/null; then
    echo "✅ 本地MySQL连接成功"
else
    echo "❌ 无法连接本地MySQL，请确保MySQL服务正在运行且密码正确"
    echo "提示：请先启动本地MySQL服务"
    exit 1
fi

# 检查数据库是否存在
echo "🗄️ 检查数据库..."
if mysql -u root -p099118 -e "USE huan_hai;" 2>/dev/null; then
    echo "✅ 数据库 huan_hai 已存在"
else
    echo "🔧 创建数据库 huan_hai..."
    mysql -u root -p099118 -e "CREATE DATABASE IF NOT EXISTS huan_hai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    echo "✅ 数据库创建成功"
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p ship_schedule_projct/logs
mkdir -p ship_schedule_projct/media/user_avatars
mkdir -p ship_schedule_projct/static

# 停止并删除现有容器
echo "🛑 停止现有服务..."
docker-compose -f docker-compose.simple.yml down 2>/dev/null || true

# 构建并启动服务
echo "🔨 构建并启动服务..."
docker-compose -f docker-compose.simple.yml up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 20

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose -f docker-compose.simple.yml ps

# 检查后端健康状态
echo "🌐 测试后端API..."
for i in {1..10}; do
    if curl -f http://localhost:8000/ 2>/dev/null; then
        echo "✅ 后端服务正常运行"
        break
    fi
    echo "等待后端启动...$i/10"
    sleep 3
done

echo "✅ 部署完成！"
echo ""
echo "📋 服务信息："
echo "   前端地址: http://localhost"
echo "   后端API: http://localhost:8000"
echo "   管理后台: http://localhost:8000/admin"
echo "   使用本地MySQL数据库 (huan_hai)"
echo ""
echo "🔧 测试命令："
echo "   查看后端日志: docker-compose -f docker-compose.simple.yml logs -f web"
echo "   进入后端容器: docker-compose -f docker-compose.simple.yml exec web bash"
echo "   测试API: curl http://localhost:8000/api/schedules/"
echo ""
echo "🔧 管理命令："
echo "   停止服务: docker-compose -f docker-compose.simple.yml down"
echo "   重启服务: docker-compose -f docker-compose.simple.yml restart"
echo "   查看所有日志: docker-compose -f docker-compose.simple.yml logs -f"