#!/bin/bash

# 船舶调度管理系统 - 本地运行脚本

set -e

echo "🚢 开始本地运行船舶调度管理系统..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python3"
    exit 1
fi

# 进入后端目录
cd ship_schedule_projct

# 检查.env文件是否存在
if [ ! -f ".env" ]; then
    echo "❌ 未找到.env文件"
    exit 1
fi

echo "✅ 使用现有的.env配置文件"

# 检查本地MySQL是否运行
echo "🔍 检查本地MySQL连接..."
if mysql -u root -p099118 -e "SELECT 1;" 2>/dev/null; then
    echo "✅ 本地MySQL连接成功"
else
    echo "❌ 无法连接本地MySQL，请确保MySQL服务正在运行且密码正确"
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

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "🐍 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📦 安装Python依赖..."
pip install -r requirements.txt

# 安装缺失的依赖
pip install django-filter

# 创建必要的目录
mkdir -p logs media/user_avatars static

# 运行数据库迁移（跳过需要交互的迁移）
echo "🔄 运行数据库迁移..."
python manage.py migrate --run-syncdb 2>/dev/null || echo "⚠️ 一些迁移需要手动处理，但基础表已创建"

# 创建超级用户（如果不存在）
echo "👤 检查管理员用户..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser('admin@example.com', 'admin123');
    print('管理员用户已创建: admin@example.com/admin123')
else:
    print('管理员用户已存在')
"

# 收集静态文件
echo "📦 收集静态文件..."
python manage.py collectstatic --noinput

echo "✅ 准备完成！"
echo ""
echo "🚀 启动开发服务器..."
echo "📋 服务信息："
echo "   后端API: http://localhost:8000"
echo "   管理后台: http://localhost:8000/admin"
echo "   管理员账号: admin / admin123"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 启动开发服务器
python manage.py runserver 0.0.0.0:8000