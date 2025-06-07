#!/bin/bash

# 船舶调度管理系统 - Docker部署脚本（使用国内镜像源）

set -e

echo "🚢 开始部署船舶调度管理系统（使用国内镜像源）..."

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
docker-compose -f docker-compose.cn.yml down

# 先尝试拉取镜像
echo "📥 拉取Docker镜像..."
docker pull registry.cn-hangzhou.aliyuncs.com/library/mysql:8.0 || echo "MySQL镜像拉取失败，尝试继续..."
docker pull registry.cn-hangzhou.aliyuncs.com/library/redis:7-alpine || echo "Redis镜像拉取失败，尝试继续..."

# 构建并启动服务
echo "🔨 构建并启动服务..."
docker-compose -f docker-compose.cn.yml up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose -f docker-compose.cn.yml ps

# 等待数据库准备就绪
echo "📊 等待数据库准备就绪..."
for i in {1..30}; do
    if docker-compose -f docker-compose.cn.yml exec -T db mysqladmin ping -h"localhost" -u root -p099118 --silent 2>/dev/null; then
        echo "✅ 数据库已准备就绪"
        break
    fi
    echo "等待数据库启动...$i/30"
    sleep 2
done

echo "✅ 部署完成！"
echo ""
echo "📋 服务信息："
echo "   前端地址: http://localhost"
echo "   后端API: http://localhost:8000"
echo "   管理后台: http://localhost:8000/admin"
echo "   数据库端口: 3307 (避免与本地MySQL冲突)"
echo "   Redis端口: 6380 (避免与本地Redis冲突)"
echo ""
echo "🔧 测试命令："
echo "   查看后端日志: docker-compose -f docker-compose.cn.yml logs -f web"
echo "   查看数据库日志: docker-compose -f docker-compose.cn.yml logs -f db"
echo "   进入后端容器: docker-compose -f docker-compose.cn.yml exec web bash"
echo "   测试API: curl http://localhost:8000/api/schedules/"
echo ""
echo "🔧 管理命令："
echo "   停止服务: docker-compose -f docker-compose.cn.yml down"
echo "   重启服务: docker-compose -f docker-compose.cn.yml restart"
echo "   查看所有日志: docker-compose -f docker-compose.cn.yml logs -f"