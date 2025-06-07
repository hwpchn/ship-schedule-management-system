# 🔒 生产环境SSL部署指南

## 📋 概述

本指南提供在Linux生产环境中为船期管理系统配置SSL证书的完整解决方案，包括Let's Encrypt免费证书和自签名证书两种方案。

## 🎯 部署选项

### 方案一：Let's Encrypt 免费SSL证书（推荐）
- ✅ 免费且自动续期
- ✅ 被所有浏览器信任
- ✅ 适合有域名的生产环境

### 方案二：自签名证书
- ✅ 无需域名
- ✅ 适合内网环境
- ⚠️ 浏览器会显示安全警告

## 🚀 快速部署（Let's Encrypt）

### 1. 前置条件
```bash
# 确保有域名指向服务器
# 例如：example.com -> 服务器IP

# 检查域名解析
nslookup your-domain.com

# 确保80和443端口开放
sudo ufw allow 80
sudo ufw allow 443
```

### 2. 一键部署命令
```bash
# 下载SSL部署脚本
wget https://your-domain.com/deploy-ssl.sh
chmod +x deploy-ssl.sh

# 运行SSL部署（替换为您的域名和邮箱）
./deploy-ssl.sh your-domain.com admin@your-domain.com
```

## 📁 生产环境文件结构

```
project/
├── docker-compose.prod.yml      # 生产环境Docker配置
├── nginx/
│   ├── nginx.conf              # 主Nginx配置
│   └── conf.d/
│       ├── default.conf        # HTTP重定向配置
│       └── ssl.conf           # HTTPS配置
├── ssl/                       # SSL证书目录
│   ├── live/
│   ├── archive/
│   └── renewal/
├── scripts/
│   ├── deploy-ssl.sh          # SSL自动部署脚本
│   ├── renew-ssl.sh           # 证书续期脚本
│   └── generate-self-signed.sh # 自签名证书生成
├── .env.prod                  # 生产环境变量
└── QUICK_START_PROD.md       # 生产环境快速开始
```

## 🌐 域名配置

### DNS设置
```bash
# A记录配置
your-domain.com     A    YOUR_SERVER_IP
www.your-domain.com A    YOUR_SERVER_IP

# 验证DNS解析
dig your-domain.com
```

### 环境变量配置
```bash
# .env.prod 文件内容
DOMAIN=your-domain.com
EMAIL=admin@your-domain.com
DB_NAME=ship_schedule_prod
DB_USER=ship_user
DB_PASSWORD=YOUR_SECURE_PASSWORD
DB_ROOT_PASSWORD=YOUR_ROOT_PASSWORD
SECRET_KEY=YOUR_SECRET_KEY_HERE
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

## 🛡️ SSL证书管理

### 自动续期设置
```bash
# 添加到crontab
crontab -e

# 每天凌晨2点检查证书续期
0 2 * * * /path/to/project/scripts/renew-ssl.sh >> /var/log/ssl-renew.log 2>&1
```

### 手动续期
```bash
./scripts/renew-ssl.sh
```

## 🔧 故障排除

### 常见问题

1. **证书申请失败**
   ```bash
   # 检查域名解析
   nslookup your-domain.com
   
   # 检查端口开放
   netstat -tulpn | grep :80
   netstat -tulpn | grep :443
   ```

2. **Nginx配置错误**
   ```bash
   # 测试配置
   docker-compose exec nginx nginx -t
   
   # 重新加载配置
   docker-compose exec nginx nginx -s reload
   ```

3. **证书路径问题**
   ```bash
   # 检查证书文件
   ls -la ssl/live/your-domain.com/
   
   # 检查权限
   chmod 644 ssl/live/your-domain.com/*.pem
   ```

## 📊 监控和维护

### 证书状态检查
```bash
# 检查证书有效期
openssl x509 -in ssl/live/your-domain.com/cert.pem -text -noout | grep "Not After"

# 在线检查
curl -I https://your-domain.com
```

### 性能监控
```bash
# 查看SSL握手时间
curl -w "@curl-format.txt" -o /dev/null -s https://your-domain.com

# Nginx访问日志
docker-compose logs nginx | grep "ssl"
```

## 🚀 部署流程

### 第一次部署
1. 准备服务器和域名
2. 上传项目文件
3. 配置环境变量
4. 运行SSL部署脚本
5. 验证HTTPS访问

### 更新部署
1. 停止服务：`docker-compose -f docker-compose.prod.yml down`
2. 更新代码
3. 启动服务：`docker-compose -f docker-compose.prod.yml up -d`
4. 检查SSL状态

## 📱 客户使用指南

### 访问地址
- **HTTPS**: https://your-domain.com
- **管理后台**: https://your-domain.com:8000/admin
- **API文档**: https://your-domain.com:8000/api/

### 默认账户
- **邮箱**: admin@admin.com
- **密码**: admin123@

### 安全建议
1. 立即修改默认密码
2. 创建新管理员账户
3. 删除默认账户
4. 定期备份数据库
5. 监控证书有效期

## 🔐 安全最佳实践

### 服务器安全
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 配置防火墙
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# 禁用root登录
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```

### 数据库安全
```bash
# 使用强密码
# 限制数据库访问
# 定期备份
# 启用审计日志
```

### 应用安全
```bash
# 使用强SECRET_KEY
# 启用HTTPS重定向
# 配置安全头
# 限制文件上传大小
```

## 📞 技术支持

### 日志查看
```bash
# 应用日志
docker-compose -f docker-compose.prod.yml logs -f web

# Nginx日志
docker-compose -f docker-compose.prod.yml logs -f nginx

# 系统日志
tail -f /var/log/syslog
```

### 备份策略
```bash
# 数据库备份
docker-compose -f docker-compose.prod.yml exec db mysqldump -u root -p ship_schedule_prod > backup_$(date +%Y%m%d).sql

# 完整备份
tar -czf backup_$(date +%Y%m%d).tar.gz . --exclude=node_modules --exclude=.git
```

---

## 🎯 快速命令参考

```bash
# 部署SSL
./scripts/deploy-ssl.sh your-domain.com admin@your-domain.com

# 启动生产环境
docker-compose -f docker-compose.prod.yml up -d

# 检查服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 续期证书
./scripts/renew-ssl.sh

# 备份数据
./scripts/backup.sh
```

记住：**安全第一，定期更新，监控告警！** 🛡️