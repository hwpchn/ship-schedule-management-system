#!/bin/bash

# Docker部署测试脚本

echo "🔍 开始测试Docker部署..."

# 检查容器状态
echo ""
echo "📋 检查容器状态:"
docker-compose ps

# 检查后端健康状态
echo ""
echo "🌐 测试后端API连接..."
echo "等待后端服务启动..."
sleep 10

# 测试后端API
if curl -f http://localhost:8000/api/schedules/ &>/dev/null; then
    echo "✅ 后端API连接成功"
else
    echo "❌ 后端API连接失败，检查后端日志:"
    docker-compose logs --tail=20 web
fi

# 测试前端
echo ""
echo "🎨 测试前端连接..."
if curl -f http://localhost/ &>/dev/null; then
    echo "✅ 前端连接成功"
else
    echo "❌ 前端连接失败，检查前端日志:"
    docker-compose logs --tail=20 frontend
fi

# 测试数据库连接
echo ""
echo "🗄️ 测试数据库连接..."
if docker-compose exec -T db mysqladmin ping -h"localhost" -u root -p099118 --silent; then
    echo "✅ 数据库连接成功"
else
    echo "❌ 数据库连接失败"
fi

# 检查日志中的错误
echo ""
echo "📝 检查最近的错误日志:"
echo "后端错误:"
docker-compose logs web | grep -i error | tail -5 || echo "无错误日志"

echo ""
echo "数据库错误:"
docker-compose logs db | grep -i error | tail -5 || echo "无错误日志"

echo ""
echo "🔗 服务访问地址:"
echo "   前端: http://localhost"
echo "   后端API: http://localhost:8000"
echo "   管理后台: http://localhost:8000/admin"
echo ""
echo "测试完成！"