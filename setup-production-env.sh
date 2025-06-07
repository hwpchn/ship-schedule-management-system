#!/bin/bash

# 🚢 生产环境配置设置脚本
# 用于在生产服务器上快速配置环境变量

set -e

echo "🔧 开始配置生产环境..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    log_error "请使用root用户运行此脚本"
    exit 1
fi

# 检查项目目录
if [ ! -d "ship_schedule_projct" ]; then
    log_error "未找到 ship_schedule_projct 目录，请确保在项目根目录执行"
    exit 1
fi

# 备份现有的.env文件（如果存在）
if [ -f "ship_schedule_projct/.env" ]; then
    log_warn "发现现有 .env 文件，备份为 .env.backup"
    cp ship_schedule_projct/.env ship_schedule_projct/.env.backup
fi

# 创建生产环境配置
log_info "创建生产环境 .env 文件..."

# 生成随机SECRET_KEY
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")

# 获取服务器IP
SERVER_IP=$(curl -s ifconfig.me || echo "your-server-ip")

cat > ship_schedule_projct/.env << EOF
# 🔐 生产环境配置文件
# 自动生成于: $(date)

# Django 核心配置
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,web,${SERVER_IP}

# 数据库配置
DB_ENGINE=django.db.backends.mysql
DB_NAME=huan_hai
DB_USER=root
DB_PASSWORD=099118
DB_HOST=db
DB_PORT=3306

# JWT 配置 (生产环境)
JWT_ACCESS_TOKEN_LIFETIME=30
JWT_REFRESH_TOKEN_LIFETIME=1

# 文件上传配置
MAX_UPLOAD_SIZE=10485760

# 日志级别
LOG_LEVEL=WARNING

# 安全配置 (生产环境)
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY

# CORS 配置
CORS_ALLOW_ALL_ORIGINS=False

# 静态文件配置
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media

# 数据库连接池配置
DB_CONN_MAX_AGE=60
DB_CONN_HEALTH_CHECKS=True
EOF

log_success "生产环境 .env 文件创建完成"

# 设置文件权限
chmod 600 ship_schedule_projct/.env
log_info "已设置 .env 文件权限为 600 (仅owner可读写)"

# 显示配置信息
log_info "配置摘要:"
echo "  🔑 SECRET_KEY: 已生成随机密钥"
echo "  🌐 ALLOWED_HOSTS: localhost,127.0.0.1,0.0.0.0,web,${SERVER_IP}"
echo "  🛡️  DEBUG: False (生产模式)"
echo "  🗄️  数据库: MySQL (huan_hai)"
echo "  📊 日志级别: WARNING"

# 询问是否需要配置域名
echo ""
read -p "是否需要添加自定义域名到ALLOWED_HOSTS? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "请输入您的域名 (例如: yourdomain.com): " DOMAIN
    if [ ! -z "$DOMAIN" ]; then
        sed -i "s/ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,web,${SERVER_IP}/ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,web,${SERVER_IP},${DOMAIN}/" ship_schedule_projct/.env
        log_success "域名 $DOMAIN 已添加到 ALLOWED_HOSTS"
    fi
fi

# 询问是否需要启用SSL
echo ""
read -p "是否启用SSL安全配置? (仅在配置了HTTPS时选择y) (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sed -i 's/SECURE_SSL_REDIRECT=False/SECURE_SSL_REDIRECT=True/' ship_schedule_projct/.env
    sed -i 's/SECURE_HSTS_SECONDS=0/SECURE_HSTS_SECONDS=31536000/' ship_schedule_projct/.env
    sed -i 's/SECURE_HSTS_INCLUDE_SUBDOMAINS=False/SECURE_HSTS_INCLUDE_SUBDOMAINS=True/' ship_schedule_projct/.env
    sed -i 's/SECURE_HSTS_PRELOAD=False/SECURE_HSTS_PRELOAD=True/' ship_schedule_projct/.env
    log_success "SSL安全配置已启用"
fi

log_success "✅ 生产环境配置完成！"
echo ""
log_info "下一步可以运行: ./deploy.sh"
echo ""
log_warn "注意: 请根据实际情况修改数据库密码和其他敏感配置"