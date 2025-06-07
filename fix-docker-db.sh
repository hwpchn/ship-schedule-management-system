#!/bin/bash

echo "🔧 修复Docker数据库问题..."

# 停止后端服务
docker-compose stop web

# 等待数据库启动
echo "⏳ 等待数据库服务启动..."
sleep 10

# 手动运行迁移
echo "🔄 手动运行数据库迁移..."
docker-compose exec db mysql -u root -p099118 -e "DROP DATABASE IF EXISTS huan_hai; CREATE DATABASE huan_hai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 重新构建并启动web服务
echo "🚀 重新启动web服务..."
docker-compose up -d web

echo "✅ 修复完成！"