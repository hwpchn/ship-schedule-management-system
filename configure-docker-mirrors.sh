#!/bin/bash

# Docker镜像源配置脚本 - 适用于中国大陆服务器

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

echo "🔧 配置Docker镜像源（中国大陆优化）..."

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    log_error "请使用root用户运行此脚本: sudo ./configure-docker-mirrors.sh"
    exit 1
fi

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    log_error "Docker未安装，请先安装Docker"
    exit 1
fi

# 创建Docker配置目录
log_info "创建Docker配置目录..."
mkdir -p /etc/docker

# 备份现有配置
if [ -f /etc/docker/daemon.json ]; then
    log_warn "发现现有配置，备份为 daemon.json.backup"
    cp /etc/docker/daemon.json /etc/docker/daemon.json.backup
fi

# 创建daemon.json配置文件
log_info "配置Docker镜像源..."
cat > /etc/docker/daemon.json << EOF
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com",
    "https://registry.docker-cn.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "exec-opts": ["native.cgroupdriver=systemd"],
  "live-restore": true,
  "ipv6": false,
  "iptables": true,
  "bridge": "none"
}
EOF

# 重启Docker服务
log_info "重启Docker服务..."
systemctl daemon-reload
systemctl restart docker

# 等待Docker启动
log_info "等待Docker服务启动..."
sleep 5

# 验证配置
log_info "验证Docker配置..."
if docker info | grep -q "Registry Mirrors" 2>/dev/null; then
    log_success "Docker镜像源配置成功！"
    echo ""
    log_info "当前配置的镜像源："
    docker info | grep -A 10 "Registry Mirrors" 2>/dev/null || echo "  配置已生效，但输出格式可能不同"
else
    log_warn "Docker配置可能未完全生效，请检查配置文件"
fi

# 测试镜像拉取
log_info "测试镜像拉取速度..."
echo "正在拉取hello-world镜像进行测试..."

start_time=$(date +%s)
if docker pull hello-world:latest >/dev/null 2>&1; then
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    log_success "测试镜像拉取成功，耗时 ${duration} 秒"
    docker rmi hello-world:latest >/dev/null 2>&1
else
    log_error "测试镜像拉取失败，请检查网络连接"
fi

echo ""
log_success "✅ Docker镜像源配置完成！"
echo ""
log_info "配置说明："
echo "  • 已配置4个国内镜像源"
echo "  • 日志大小限制为100MB，保留3个文件"
echo "  • 使用overlay2存储驱动"
echo "  • 启用systemd cgroup驱动"
echo ""
log_info "现在可以运行以下命令进行部署："
echo "  ./deploy-cn.sh    # 使用国内优化的部署脚本"
echo "  ./deploy.sh       # 使用标准部署脚本"