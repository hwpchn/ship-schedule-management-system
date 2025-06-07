#!/bin/bash

# 🔐 自签名SSL证书生成脚本
# 用法: ./generate-self-signed.sh your-domain.com

set -e

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

# 检查参数
if [ $# -ne 1 ]; then
    log_error "用法: $0 <域名或IP>"
    log_info "例如: $0 example.com 或 $0 192.168.1.100"
    exit 1
fi

DOMAIN=$1

log_info "🔐 开始生成自签名SSL证书..."
log_info "📧 域名/IP: $DOMAIN"

# 创建SSL目录
mkdir -p ssl/self-signed
cd ssl/self-signed

# 生成私钥
log_info "🔑 生成私钥..."
openssl genrsa -out private.key 2048

# 创建证书签名请求配置
log_info "📝 创建证书配置..."
cat > cert.conf << EOF
[req]
default_bits = 2048
prompt = no
distinguished_name = req_distinguished_name
req_extensions = v3_req

[req_distinguished_name]
C = CN
ST = Beijing
L = Beijing
O = Ship Schedule Management
OU = IT Department
CN = $DOMAIN

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN
DNS.2 = www.$DOMAIN
DNS.3 = localhost
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

# 如果输入的是IP地址，添加到SAN中
if [[ $DOMAIN =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "IP.3 = $DOMAIN" >> cert.conf
fi

# 生成证书签名请求
log_info "📋 生成证书签名请求..."
openssl req -new -key private.key -out cert.csr -config cert.conf

# 生成自签名证书 (有效期10年)
log_info "📜 生成自签名证书..."
openssl x509 -req -in cert.csr -signkey private.key -out certificate.crt -days 3650 -extensions v3_req -extfile cert.conf

# 创建PEM格式的完整证书链
log_info "🔗 创建证书链..."
cat certificate.crt > fullchain.pem
cat private.key > privkey.pem

# 生成DH参数 (用于增强安全性)
log_info "🛡️ 生成DH参数..."
openssl dhparam -out dhparam.pem 2048

# 设置正确的权限
chmod 644 certificate.crt fullchain.pem
chmod 600 private.key privkey.pem dhparam.pem

# 返回项目根目录
cd ../..

# 创建Nginx SSL配置
log_info "🌐 创建Nginx SSL配置..."
mkdir -p nginx/conf.d

cat > nginx/conf.d/ssl-self-signed.conf << EOF
# 自签名SSL配置
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN localhost;
    
    # 重定向到HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN localhost;

    # 自签名SSL证书配置
    ssl_certificate /etc/nginx/ssl/self-signed/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/self-signed/privkey.pem;
    ssl_dhparam /etc/nginx/ssl/self-signed/dhparam.pem;

    # SSL安全设置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 安全头
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

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

# 更新docker-compose.prod.yml中的卷映射
log_info "📦 更新Docker配置..."
if [ -f "docker-compose.prod.yml" ]; then
    # 确保SSL证书目录映射正确
    if ! grep -q "ssl/self-signed:/etc/nginx/ssl/self-signed" docker-compose.prod.yml; then
        log_info "添加自签名证书卷映射到docker-compose.prod.yml"
    fi
fi

# 验证证书
log_info "✅ 验证生成的证书..."
openssl x509 -in ssl/self-signed/certificate.crt -text -noout | grep -E "(Subject:|Not After:|DNS:|IP Address:)"

# 显示证书信息
EXPIRE_DATE=$(openssl x509 -in ssl/self-signed/certificate.crt -noout -enddate | cut -d= -f2)
SUBJECT=$(openssl x509 -in ssl/self-signed/certificate.crt -noout -subject | cut -d= -f2-)

echo
log_success "🎉 自签名SSL证书生成完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📜 证书信息:"
echo "   域名: $DOMAIN"
echo "   主题: $SUBJECT"
echo "   有效期: 10年"
echo "   到期时间: $EXPIRE_DATE"
echo
echo "📁 证书文件位置:"
echo "   私钥: ssl/self-signed/private.key"
echo "   证书: ssl/self-signed/certificate.crt"
echo "   完整链: ssl/self-signed/fullchain.pem"
echo "   DH参数: ssl/self-signed/dhparam.pem"
echo
echo "🚀 启动命令:"
echo "   docker-compose -f docker-compose.prod.yml up -d"
echo
echo "🌐 访问地址:"
echo "   HTTPS: https://$DOMAIN"
echo "   管理后台: https://$DOMAIN/admin"
echo
echo "⚠️  重要提醒:"
echo "   - 这是自签名证书，浏览器会显示安全警告"
echo "   - 点击'高级'然后'继续访问'即可"
echo "   - 生产环境建议使用Let's Encrypt证书"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 保存证书信息
cat > SSL_SELF_SIGNED_INFO.txt << EOF
自签名SSL证书信息 - $(date)
=======================================

域名: $DOMAIN
生成时间: $(date)
有效期: 10年
到期时间: $EXPIRE_DATE

证书文件:
- 私钥: ssl/self-signed/private.key
- 证书: ssl/self-signed/certificate.crt
- 完整链: ssl/self-signed/fullchain.pem
- DH参数: ssl/self-signed/dhparam.pem

访问地址:
- HTTPS: https://$DOMAIN
- 管理后台: https://$DOMAIN/admin

默认账户:
- 邮箱: admin@admin.com
- 密码: admin123@

启动命令:
docker-compose -f docker-compose.prod.yml up -d

重要提醒:
1. 自签名证书会显示安全警告，这是正常的
2. 生产环境建议使用 ./scripts/deploy-ssl.sh 申请正式证书
3. 请立即修改默认管理员密码
EOF

log_success "证书信息已保存到 SSL_SELF_SIGNED_INFO.txt"
log_info "🎯 现在可以运行 docker-compose -f docker-compose.prod.yml up -d 启动HTTPS服务！"