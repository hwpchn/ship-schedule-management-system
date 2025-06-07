#!/bin/bash

# 🔒 SSL自动部署脚本 - Let's Encrypt
# 用法: ./deploy-ssl.sh your-domain.com admin@your-domain.com

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 检查参数
if [ $# -ne 2 ]; then
    log_error "用法: $0 <域名> <邮箱>"
    log_info "例如: $0 example.com admin@example.com"
    exit 1
fi

DOMAIN=$1
EMAIL=$2

log_info "🚀 开始SSL自动部署..."
log_info "📧 域名: $DOMAIN"
log_info "📧 邮箱: $EMAIL"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    log_error "请以root用户运行此脚本"
    exit 1
fi

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    log_error "Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 检查域名解析
log_info "🔍 检查域名解析..."
if ! nslookup $DOMAIN > /dev/null 2>&1; then
    log_error "域名解析失败，请检查DNS配置"
    exit 1
fi

# 获取域名解析的IP
DOMAIN_IP=$(dig +short $DOMAIN | tail -n1)
log_info "域名解析IP: $DOMAIN_IP"

# 获取服务器公网IP
SERVER_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || echo "未知")
log_info "服务器IP: $SERVER_IP"

if [ "$DOMAIN_IP" != "$SERVER_IP" ]; then
    log_warn "域名解析IP与服务器IP不一致，可能影响SSL证书申请"
    read -p "是否继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查端口占用
log_info "🔍 检查端口占用..."
if ss -tulpn | grep :80 > /dev/null; then
    log_warn "端口80已被占用"
    ss -tulpn | grep :80
fi

if ss -tulpn | grep :443 > /dev/null; then
    log_warn "端口443已被占用"
    ss -tulpn | grep :443
fi

# 创建必要目录
log_info "📁 创建SSL相关目录..."
mkdir -p ssl/live ssl/archive ssl/renewal
mkdir -p nginx/conf.d
mkdir -p logs

# 停止可能运行的服务
log_info "🛑 停止现有服务..."
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# 创建生产环境配置
log_info "⚙️ 创建生产环境配置..."

# 生成随机密码和密钥
DB_PASSWORD=$(openssl rand -base64 32)
DB_ROOT_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 64)

# 创建.env.prod文件
cat > .env.prod << EOF
# 生产环境配置
DOMAIN=$DOMAIN
EMAIL=$EMAIL

# 数据库配置
DB_NAME=ship_schedule_prod
DB_USER=ship_user
DB_PASSWORD=$DB_PASSWORD
DB_ROOT_PASSWORD=$DB_ROOT_PASSWORD

# Django配置
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN
CORS_ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN

# SSL配置
ENABLE_SSL=true
EOF

log_success "生产环境配置已创建"

# 创建Nginx配置
log_info "🌐 创建Nginx配置..."

# 主Nginx配置
cat > nginx/nginx.conf << 'EOF'
user nginx;
worker_processes auto;

error_log /var/log/nginx/error.log notice;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    # 基本设置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;

    # 文件上传限制
    client_max_body_size 10M;
    client_body_buffer_size 128k;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json
        image/svg+xml;

    # SSL设置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 安全头
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # 包含站点配置
    include /etc/nginx/conf.d/*.conf;
}
EOF

# HTTP配置 (用于证书申请和重定向)
cat > nginx/conf.d/default.conf << EOF
# HTTP配置 - 重定向到HTTPS
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Let's Encrypt验证
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # 重定向到HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}
EOF

# 创建临时SSL配置（用于首次申请证书）
cat > nginx/conf.d/ssl-temp.conf << EOF
# 临时HTTPS配置 - 用于证书申请
server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # 临时自签名证书
    ssl_certificate /etc/nginx/ssl/temp.crt;
    ssl_certificate_key /etc/nginx/ssl/temp.key;

    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 生成临时自签名证书
log_info "🔐 生成临时自签名证书..."
mkdir -p ssl/temp
openssl req -x509 -nodes -days 1 -newkey rsa:2048 \
    -keyout ssl/temp/temp.key \
    -out ssl/temp/temp.crt \
    -subj "/C=US/ST=State/L=City/O=Org/CN=$DOMAIN" > /dev/null 2>&1

# 启动服务准备证书申请
log_info "🚀 启动临时服务..."
docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动
log_info "⏳ 等待服务启动..."
sleep 30

# 申请Let's Encrypt证书
log_info "📜 申请Let's Encrypt SSL证书..."

# 运行Certbot申请证书
docker run --rm \
    -v $(pwd)/ssl:/etc/letsencrypt \
    -v $(pwd)/ssl-challenge:/var/www/certbot \
    -p 80:80 \
    certbot/certbot certonly \
    --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

if [ $? -eq 0 ]; then
    log_success "SSL证书申请成功！"
else
    log_error "SSL证书申请失败"
    exit 1
fi

# 创建正式的SSL配置
log_info "🔧 配置HTTPS服务..."

cat > nginx/conf.d/ssl.conf << EOF
# HTTPS配置
server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL证书配置
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    # SSL安全设置
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    add_header Strict-Transport-Security "max-age=31536000" always;

    # 前端静态文件
    location / {
        root /var/www/html;
        index index.html;
        try_files \$uri \$uri/ /index.html;
        
        # 静态资源缓存
        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API代理
    location /api/ {
        proxy_pass http://web:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 文件上传配置
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;
        proxy_request_buffering off;
    }

    # 媒体文件代理
    location /media/ {
        proxy_pass http://web:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Django管理后台
    location /admin/ {
        proxy_pass http://web:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # 静态文件代理
    location /static/ {
        proxy_pass http://web:8000;
        proxy_set_header Host \$host;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# 删除临时配置
rm -f nginx/conf.d/ssl-temp.conf

# 重新启动服务
log_info "🔄 重新启动服务..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# 等待服务完全启动
log_info "⏳ 等待服务完全启动..."
sleep 30

# 测试HTTPS连接
log_info "🧪 测试HTTPS连接..."
if curl -fs https://$DOMAIN > /dev/null; then
    log_success "HTTPS连接测试成功！"
else
    log_error "HTTPS连接测试失败"
fi

# 显示部署结果
echo
echo "🎉 SSL部署完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 访问地址:"
echo "   前端系统: https://$DOMAIN"
echo "   管理后台: https://$DOMAIN/admin"
echo "   API接口:  https://$DOMAIN/api/"
echo
echo "🔑 默认管理员账户:"
echo "   邮箱: admin@admin.com"
echo "   密码: admin123@"
echo
echo "📋 重要信息:"
echo "   - SSL证书有效期: 90天"
echo "   - 自动续期已配置"
echo "   - 证书路径: $(pwd)/ssl/live/$DOMAIN/"
echo "   - 配置文件: $(pwd)/.env.prod"
echo
echo "🔧 管理命令:"
echo "   查看状态: docker-compose -f docker-compose.prod.yml ps"
echo "   查看日志: docker-compose -f docker-compose.prod.yml logs -f"
echo "   续期证书: ./scripts/renew-ssl.sh"
echo "   重启服务: docker-compose -f docker-compose.prod.yml restart"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# 保存重要信息到文件
cat > SSL_DEPLOYMENT_INFO.txt << EOF
SSL部署信息 - $(date)
======================================

域名: $DOMAIN
邮箱: $EMAIL
部署时间: $(date)

访问地址:
- 前端: https://$DOMAIN
- 管理后台: https://$DOMAIN/admin
- API: https://$DOMAIN/api/

默认账户:
- 邮箱: admin@admin.com
- 密码: admin123@

数据库配置:
- 数据库名: ship_schedule_prod
- 用户名: ship_user
- 密码: $DB_PASSWORD
- Root密码: $DB_ROOT_PASSWORD

Django密钥:
- SECRET_KEY: $SECRET_KEY

证书信息:
- 证书路径: $(pwd)/ssl/live/$DOMAIN/
- 有效期: 90天
- 续期命令: ./scripts/renew-ssl.sh

重要提醒:
1. 请立即修改默认管理员密码
2. 证书会自动续期
3. 定期备份数据库
4. 监控服务状态
EOF

log_success "部署信息已保存到 SSL_DEPLOYMENT_INFO.txt"
log_info "🎯 请访问 https://$DOMAIN 开始使用系统！"