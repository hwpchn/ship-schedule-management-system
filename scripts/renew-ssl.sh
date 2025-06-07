#!/bin/bash

# 🔄 SSL证书自动续期脚本
# 用法: ./renew-ssl.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_warn() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

log_info "🔄 开始SSL证书续期检查..."

# 检查是否存在SSL证书目录
if [ ! -d "ssl/live" ]; then
    log_error "SSL证书目录不存在，请先运行 deploy-ssl.sh"
    exit 1
fi

# 获取域名（从第一个证书目录）
DOMAIN=$(ls ssl/live/ | head -n 1)
if [ -z "$DOMAIN" ]; then
    log_error "未找到SSL证书域名"
    exit 1
fi

log_info "检查域名: $DOMAIN"

# 检查证书有效期
CERT_FILE="ssl/live/$DOMAIN/cert.pem"
if [ -f "$CERT_FILE" ]; then
    # 获取证书到期时间
    EXPIRE_DATE=$(openssl x509 -in "$CERT_FILE" -noout -enddate | cut -d= -f2)
    EXPIRE_TIMESTAMP=$(date -d "$EXPIRE_DATE" +%s)
    CURRENT_TIMESTAMP=$(date +%s)
    DAYS_LEFT=$(( (EXPIRE_TIMESTAMP - CURRENT_TIMESTAMP) / 86400 ))
    
    log_info "证书到期时间: $EXPIRE_DATE"
    log_info "剩余天数: $DAYS_LEFT 天"
    
    # 如果证书还有30天以上有效期，跳过续期
    if [ $DAYS_LEFT -gt 30 ]; then
        log_info "证书还有 $DAYS_LEFT 天有效期，无需续期"
        exit 0
    fi
    
    log_warn "证书将在 $DAYS_LEFT 天后过期，开始续期..."
else
    log_error "证书文件不存在: $CERT_FILE"
    exit 1
fi

# 备份当前证书
log_info "📦 备份当前证书..."
BACKUP_DIR="ssl/backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r ssl/live/$DOMAIN "$BACKUP_DIR/"
log_success "证书已备份到: $BACKUP_DIR"

# 停止Nginx以释放80和443端口
log_info "🛑 临时停止Nginx服务..."
docker-compose -f docker-compose.prod.yml stop nginx

# 续期证书
log_info "🔄 续期SSL证书..."
docker run --rm \
    -v $(pwd)/ssl:/etc/letsencrypt \
    -v $(pwd)/ssl-challenge:/var/www/certbot \
    -p 80:80 \
    -p 443:443 \
    certbot/certbot renew \
    --standalone \
    --quiet

RENEW_RESULT=$?

# 重新启动Nginx
log_info "🚀 重新启动Nginx服务..."
docker-compose -f docker-compose.prod.yml start nginx

# 检查续期结果
if [ $RENEW_RESULT -eq 0 ]; then
    log_success "SSL证书续期成功！"
    
    # 重新加载Nginx配置
    log_info "🔄 重新加载Nginx配置..."
    docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
    
    # 检查新证书有效期
    NEW_EXPIRE_DATE=$(openssl x509 -in "$CERT_FILE" -noout -enddate | cut -d= -f2)
    NEW_EXPIRE_TIMESTAMP=$(date -d "$NEW_EXPIRE_DATE" +%s)
    NEW_DAYS_LEFT=$(( (NEW_EXPIRE_TIMESTAMP - CURRENT_TIMESTAMP) / 86400 ))
    
    log_success "新证书到期时间: $NEW_EXPIRE_DATE"
    log_success "新证书有效期: $NEW_DAYS_LEFT 天"
    
    # 测试HTTPS连接
    log_info "🧪 测试HTTPS连接..."
    if curl -fs https://$DOMAIN > /dev/null; then
        log_success "HTTPS连接测试成功！"
    else
        log_error "HTTPS连接测试失败，请检查配置"
    fi
    
    # 记录续期日志
    echo "$(date '+%Y-%m-%d %H:%M:%S') - SSL证书续期成功，新有效期：$NEW_DAYS_LEFT 天" >> ssl/renewal.log
    
else
    log_error "SSL证书续期失败"
    
    # 恢复备份证书
    log_warn "🔙 恢复备份证书..."
    cp -r "$BACKUP_DIR/$DOMAIN"/* ssl/live/$DOMAIN/
    
    # 重新加载Nginx配置
    docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
    
    # 记录失败日志
    echo "$(date '+%Y-%m-%d %H:%M:%S') - SSL证书续期失败" >> ssl/renewal.log
    
    exit 1
fi

# 清理旧的备份（保留最近10个）
log_info "🧹 清理旧备份..."
find ssl/backup -type d -name "20*" | sort -r | tail -n +11 | xargs rm -rf

log_success "SSL证书续期完成！"

# 发送通知（如果配置了邮件）
if command -v mail &> /dev/null && [ -n "$ADMIN_EMAIL" ]; then
    echo "SSL证书续期成功 - $DOMAIN
    
续期时间: $(date)
新证书有效期: $NEW_DAYS_LEFT 天
到期时间: $NEW_EXPIRE_DATE

系统运行正常。
" | mail -s "SSL证书续期成功 - $DOMAIN" "$ADMIN_EMAIL"
fi