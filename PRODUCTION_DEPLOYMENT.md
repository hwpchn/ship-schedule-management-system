# 🚀 生产环境部署指南

## 📋 快速部署清单

### 📦 交付给客户的文件
```
ship-schedule-system/
├── 📄 README.md                    # 系统说明
├── 📄 SSL_DEPLOYMENT_GUIDE.md      # SSL配置详细指南
├── 📄 PRODUCTION_DEPLOYMENT.md     # 生产环境部署指南 (本文件)
├── 📄 QUICK_START.md               # 快速开始指南
├── 🐳 docker-compose.yml           # 开发环境配置
├── 🐳 docker-compose.prod.yml      # 生产环境配置
├── 📁 ship_schedule_projct/         # Django后端项目
├── 📁 ship-schedule-management-ui/  # Vue前端项目
├── 📁 scripts/                     # 部署脚本
│   ├── 🔒 deploy-ssl.sh            # SSL自动部署脚本
│   ├── 🔄 renew-ssl.sh             # SSL续期脚本
│   └── 🔐 generate-self-signed.sh   # 自签名证书生成
└── 📁 nginx/                       # Nginx配置目录
```

## 🎯 三种部署方案

### 方案一：有域名 + Let's Encrypt (推荐)
```bash
# 1. 上传项目到服务器
scp -r ship-schedule-system/ user@server:/opt/

# 2. 登录服务器
ssh user@server
cd /opt/ship-schedule-system

# 3. 一键SSL部署
sudo ./scripts/deploy-ssl.sh your-domain.com admin@your-domain.com

# 4. 访问系统
# https://your-domain.com
```

### 方案二：无域名 + 自签名证书
```bash
# 1. 上传项目到服务器
scp -r ship-schedule-system/ user@server:/opt/

# 2. 登录服务器
ssh user@server
cd /opt/ship-schedule-system

# 3. 生成自签名证书
./scripts/generate-self-signed.sh 192.168.1.100  # 使用服务器IP

# 4. 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 5. 访问系统 (会有安全警告，点击继续访问即可)
# https://192.168.1.100
```

### 方案三：HTTP部署 (不推荐)
```bash
# 1. 上传项目到服务器
scp -r ship-schedule-system/ user@server:/opt/

# 2. 登录服务器
ssh user@server
cd /opt/ship-schedule-system

# 3. 启动开发环境 (HTTP)
docker-compose up -d

# 4. 访问系统
# http://server-ip
```

## 🛠️ 服务器环境要求

### 最低配置
- **CPU**: 2核
- **内存**: 4GB RAM
- **存储**: 20GB 可用空间
- **操作系统**: Ubuntu 20.04+, CentOS 8+, Debian 10+
- **网络**: 公网IP (如需域名访问)

### 推荐配置
- **CPU**: 4核
- **内存**: 8GB RAM
- **存储**: 50GB SSD
- **带宽**: 10Mbps+

### 端口要求
- **80**: HTTP (Let's Encrypt验证)
- **443**: HTTPS
- **22**: SSH管理

## 🔧 预安装软件

### Docker安装 (Ubuntu/Debian)
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 添加用户到docker组
sudo usermod -aG docker $USER
newgrp docker
```

### Docker安装 (CentOS/RHEL)
```bash
# 更新系统
sudo yum update -y

# 安装Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 添加用户到docker组
sudo usermod -aG docker $USER
newgrp docker
```

## 🌐 域名配置 (方案一必需)

### DNS设置
```bash
# A记录配置
域名                  类型    值
your-domain.com      A      服务器公网IP
www.your-domain.com  A      服务器公网IP

# 验证DNS解析
nslookup your-domain.com
dig your-domain.com
```

### 防火墙配置
```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 📊 部署验证

### 服务状态检查
```bash
# 检查Docker服务
docker --version
docker-compose --version

# 检查容器状态
docker-compose -f docker-compose.prod.yml ps

# 检查端口监听
netstat -tulpn | grep :443
netstat -tulpn | grep :80
```

### 系统访问测试
```bash
# 测试HTTPS连接
curl -I https://your-domain.com

# 测试API接口
curl https://your-domain.com/api/auth/login/

# 检查SSL证书
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

## 🔐 安全配置

### SSL证书管理
```bash
# 查看证书有效期
./scripts/renew-ssl.sh

# 设置自动续期
crontab -e
# 添加: 0 2 * * * /opt/ship-schedule-system/scripts/renew-ssl.sh
```

### 系统安全加固
```bash
# 禁用root登录
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# 创建管理用户
sudo adduser shipmanager
sudo usermod -aG sudo shipmanager
sudo usermod -aG docker shipmanager

# 配置SSH密钥认证
ssh-copy-id shipmanager@server-ip
```

## 📱 客户培训清单

### 管理员培训内容
1. **系统访问**
   - HTTPS地址: https://your-domain.com
   - 管理后台: https://your-domain.com/admin
   - 默认账户: admin@admin.com / admin123@

2. **安全操作**
   - 修改默认密码
   - 创建新管理员
   - 删除默认账户

3. **日常管理**
   - 用户管理
   - 权限分配
   - 数据备份
   - 系统监控

4. **故障处理**
   - 重启服务: `docker-compose -f docker-compose.prod.yml restart`
   - 查看日志: `docker-compose -f docker-compose.prod.yml logs -f`
   - 证书续期: `./scripts/renew-ssl.sh`

### 用户培训内容
1. **系统登录**
   - 访问地址
   - 账户申请流程
   - 密码重置

2. **功能使用**
   - 船期查询
   - 数据导出
   - 个人资料管理

## 🛠️ 运维管理

### 数据备份
```bash
# 数据库备份脚本
#!/bin/bash
BACKUP_DIR="/opt/backup/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose -f docker-compose.prod.yml exec -T db mysqldump -u root -p$DB_ROOT_PASSWORD ship_schedule_prod > $BACKUP_DIR/database.sql

# 备份用户上传文件
tar -czf $BACKUP_DIR/media.tar.gz ship_schedule_projct/media/

# 清理30天前的备份
find /opt/backup -type d -mtime +30 -exec rm -rf {} \;
```

### 监控脚本
```bash
# 系统监控脚本
#!/bin/bash
LOG_FILE="/var/log/ship-schedule-monitor.log"

# 检查服务状态
if ! docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "$(date): 服务异常" >> $LOG_FILE
    # 发送告警邮件或短信
fi

# 检查SSL证书
DAYS_LEFT=$(./scripts/renew-ssl.sh 2>&1 | grep "剩余天数" | awk '{print $2}')
if [ "$DAYS_LEFT" -lt 7 ]; then
    echo "$(date): SSL证书即将过期，剩余${DAYS_LEFT}天" >> $LOG_FILE
fi

# 检查磁盘空间
DISK_USAGE=$(df / | awk 'NR==2{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "$(date): 磁盘使用率${DISK_USAGE}%，请清理" >> $LOG_FILE
fi
```

## 📞 技术支持

### 常见问题解决
1. **无法访问系统**
   - 检查防火墙配置
   - 验证Docker服务状态
   - 查看容器日志

2. **SSL证书问题**
   - 验证域名解析
   - 检查证书有效期
   - 手动续期证书

3. **性能问题**
   - 检查服务器资源使用
   - 优化数据库配置
   - 清理日志文件

### 联系方式
- **技术支持**: 通过项目文档获取
- **紧急故障**: 查看故障排除指南
- **功能需求**: 提交功能请求

## ✅ 部署检查清单

### 部署前检查
- [ ] 服务器配置满足要求
- [ ] Docker和Docker Compose已安装
- [ ] 域名DNS解析正确 (如使用域名)
- [ ] 防火墙端口已开放
- [ ] 项目文件已上传

### 部署过程检查
- [ ] SSL证书申请成功
- [ ] 所有容器启动正常
- [ ] HTTPS访问正常
- [ ] API接口响应正常
- [ ] 默认管理员登录成功

### 部署后检查
- [ ] 修改默认管理员密码
- [ ] 创建新管理员账户
- [ ] 删除默认账户
- [ ] 配置自动备份
- [ ] 设置监控告警
- [ ] 培训系统管理员

---

## 🎯 一键部署命令总结

```bash
# 方案一：域名 + Let's Encrypt
sudo ./scripts/deploy-ssl.sh your-domain.com admin@your-domain.com

# 方案二：IP + 自签名证书
./scripts/generate-self-signed.sh 192.168.1.100
docker-compose -f docker-compose.prod.yml up -d

# 方案三：HTTP部署
docker-compose up -d
```

**部署完成后访问**: https://your-domain.com 或 https://server-ip
**默认账户**: admin@admin.com / admin123@

**记住**: 🔒 安全第一，立即修改默认密码！