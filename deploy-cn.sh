#!/bin/bash

# 船舶调度管理系统 - Docker部署脚本（国内网络优化版）

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

echo "🚢 开始部署船舶调度管理系统（国内网络优化版）..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    log_error "Docker未安装，请先安装Docker"
    exit 1
fi

# 检查Docker Compose是否可用（支持新版本的docker compose命令）
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    log_error "Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

log_info "使用 $COMPOSE_CMD 命令"

# 检查.env文件是否存在
if [ ! -f "ship_schedule_projct/.env" ]; then
    echo "❌ 未找到ship_schedule_projct/.env文件"
    exit 1
fi

echo "✅ 使用现有的.env配置文件"

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p ship_schedule_projct/logs
mkdir -p ship_schedule_projct/media/user_avatars
mkdir -p ship_schedule_projct/static

# 停止并删除现有容器
log_info "停止现有服务..."
$COMPOSE_CMD -f docker-compose.cn.yml down

# 预拉取镜像（使用多个镜像源备选）
log_info "预拉取Docker镜像..."

# 尝试多个镜像源拉取MySQL
pull_mysql() {
    log_info "正在拉取MySQL镜像..."
    if docker pull mysql:8.0; then
        log_success "MySQL镜像拉取成功"
        return 0
    fi
    
    log_warn "官方源失败，尝试阿里云镜像源..."
    if docker pull registry.cn-hangzhou.aliyuncs.com/library/mysql:8.0; then
        docker tag registry.cn-hangzhou.aliyuncs.com/library/mysql:8.0 mysql:8.0
        log_success "MySQL镜像拉取成功（阿里云源）"
        return 0
    fi
    
    log_warn "阿里云源失败，尝试网易镜像源..."
    if docker pull hub-mirror.c.163.com/library/mysql:8.0; then
        docker tag hub-mirror.c.163.com/library/mysql:8.0 mysql:8.0
        log_success "MySQL镜像拉取成功（网易源）"
        return 0
    fi
    
    log_error "所有MySQL镜像源均失败，但继续尝试启动"
    return 1
}

# 尝试多个镜像源拉取Redis
pull_redis() {
    log_info "正在拉取Redis镜像..."
    if docker pull redis:7-alpine; then
        log_success "Redis镜像拉取成功"
        return 0
    fi
    
    log_warn "官方源失败，尝试阿里云镜像源..."
    if docker pull registry.cn-hangzhou.aliyuncs.com/library/redis:7-alpine; then
        docker tag registry.cn-hangzhou.aliyuncs.com/library/redis:7-alpine redis:7-alpine
        log_success "Redis镜像拉取成功（阿里云源）"
        return 0
    fi
    
    log_warn "阿里云源失败，尝试网易镜像源..."
    if docker pull hub-mirror.c.163.com/library/redis:7-alpine; then
        docker tag hub-mirror.c.163.com/library/redis:7-alpine redis:7-alpine
        log_success "Redis镜像拉取成功（网易源）"
        return 0
    fi
    
    log_error "所有Redis镜像源均失败，但继续尝试启动"
    return 1
}

# 执行镜像拉取
pull_mysql
pull_redis

# 构建并启动服务
log_info "构建并启动服务..."
$COMPOSE_CMD -f docker-compose.cn.yml up --build -d

# 等待服务启动
log_info "等待服务启动..."
sleep 30

# 检查服务状态
log_info "检查服务状态..."
$COMPOSE_CMD -f docker-compose.cn.yml ps

# 等待数据库准备就绪
log_info "等待数据库准备就绪..."
for i in {1..30}; do
    if $COMPOSE_CMD -f docker-compose.cn.yml exec -T db mysqladmin ping -h"localhost" -u root -p099118 --silent 2>/dev/null; then
        log_success "数据库已准备就绪"
        break
    fi
    log_info "等待数据库启动...$i/30"
    sleep 2
done

echo "✅ 部署完成！"
echo ""
echo "📋 服务信息："
echo "   前端地址: http://localhost"
echo "   后端API: http://localhost:8000"
echo "   管理后台: http://localhost:8000/admin"
echo "   数据库端口: 3307 (避免与本地MySQL冲突)"
echo "   Redis端口: 6380 (避免与本地Redis冲突)"
echo ""
echo "🔧 测试命令："
echo "   查看后端日志: docker-compose -f docker-compose.cn.yml logs -f web"
echo "   查看数据库日志: docker-compose -f docker-compose.cn.yml logs -f db"
echo "   进入后端容器: docker-compose -f docker-compose.cn.yml exec web bash"
echo "   测试API: curl http://localhost:8000/api/schedules/"
echo ""
echo "🔧 管理命令："
echo "   停止服务: docker-compose -f docker-compose.cn.yml down"
echo "   重启服务: docker-compose -f docker-compose.cn.yml restart"
echo "   查看所有日志: docker-compose -f docker-compose.cn.yml logs -f"