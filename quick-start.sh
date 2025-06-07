#!/bin/bash

# 快速启动脚本

echo "🚀 快速启动后端服务..."

cd ship_schedule_projct

# 激活虚拟环境
source venv/bin/activate

# 创建目录
mkdir -p logs media/user_avatars static

echo "🌐 启动Django开发服务器..."
echo "访问地址: http://localhost:8000"
echo "按 Ctrl+C 停止服务"
echo ""

# 启动服务器
python manage.py runserver 0.0.0.0:8000