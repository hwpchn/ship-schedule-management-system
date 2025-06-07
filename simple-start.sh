#!/bin/bash

# 简化启动脚本 - 跳过迁移问题

echo "🚀 简化启动Django服务..."

cd ship_schedule_projct

# 激活虚拟环境
source venv/bin/activate

# 创建必要目录
mkdir -p logs media/user_avatars static

echo "🌐 启动Django开发服务器 (跳过迁移)..."
echo "访问地址: http://localhost:8000"
echo "前端代理已配置，可直接从前端访问API"
echo "按 Ctrl+C 停止服务"
echo ""

# 直接启动服务器，跳过复杂的迁移
python manage.py runserver 0.0.0.0:8000 --insecure