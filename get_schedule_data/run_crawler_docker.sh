#!/bin/bash

# 🐳 Docker环境下的爬虫启动脚本
# 用法: ./run_crawler_docker.sh [选项]

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

# 检查Docker容器状态
check_docker_status() {
    log_info "检查Docker容器状态..."
    
    # 检查数据库容器
    if ! docker ps | grep -q "ship_schedule_db"; then
        log_error "数据库容器未运行，请先启动Docker服务"
        log_info "运行: docker-compose up -d"
        exit 1
    fi
    
    # 检查Web容器
    if ! docker ps | grep -q "ship_schedule_web"; then
        log_warn "Web容器未运行，但数据库可用"
    fi
    
    log_success "Docker容器状态正常"
}

# 测试数据库连接
test_db_connection() {
    log_info "测试数据库连接..."
    
    if python3 -c "
import pymysql
try:
    conn = pymysql.connect(host='localhost', port=3307, user='root', password='099118', database='huan_hai')
    conn.close()
    print('✅ 数据库连接成功')
except Exception as e:
    print(f'❌ 数据库连接失败: {e}')
    exit(1)
"; then
        log_success "数据库连接测试通过"
    else
        log_error "数据库连接测试失败"
        exit 1
    fi
}

# 显示使用帮助
show_help() {
    echo "🐳 Docker环境下的爬虫启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --test           使用测试数据运行"
    echo "  --api            使用API获取所有港口组合数据"
    echo "  --pol CODE       指定起运港代码"
    echo "  --pod CODE       指定目的港代码"
    echo "  --check          仅检查环境，不运行爬虫"
    echo "  --help           显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                     # 使用默认配置运行"
    echo "  $0 --test             # 使用测试数据"
    echo "  $0 --api              # 获取所有港口数据"
    echo "  $0 --pol CNSHK --pod THBKK  # 指定港口"
    echo ""
}

# 主函数
main() {
    log_info "🚀 启动Docker环境爬虫服务..."
    
    # 解析命令行参数
    USE_TEST=false
    USE_API=false
    POL_CODE=""
    POD_CODE=""
    CHECK_ONLY=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --test)
                USE_TEST=true
                shift
                ;;
            --api)
                USE_API=true
                shift
                ;;
            --pol)
                POL_CODE="$2"
                shift 2
                ;;
            --pod)
                POD_CODE="$2"
                shift 2
                ;;
            --check)
                CHECK_ONLY=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 环境检查
    check_docker_status
    test_db_connection
    
    if [ "$CHECK_ONLY" = true ]; then
        log_success "环境检查完成，一切正常！"
        exit 0
    fi
    
    # 构建爬虫命令
    CRAWLER_CMD="python3 process_routes.py --env docker"
    
    if [ "$USE_TEST" = true ]; then
        CRAWLER_CMD="$CRAWLER_CMD --use_test_data"
        log_info "使用测试数据模式"
    fi
    
    if [ "$USE_API" = true ]; then
        CRAWLER_CMD="$CRAWLER_CMD --use_port_api"
        log_info "使用API获取所有港口组合数据"
    fi
    
    if [ -n "$POL_CODE" ]; then
        CRAWLER_CMD="$CRAWLER_CMD --pol_cd $POL_CODE"
        log_info "指定起运港: $POL_CODE"
    fi
    
    if [ -n "$POD_CODE" ]; then
        CRAWLER_CMD="$CRAWLER_CMD --pod_cd $POD_CODE"
        log_info "指定目的港: $POD_CODE"
    fi
    
    # 运行爬虫
    log_info "执行命令: $CRAWLER_CMD"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if eval $CRAWLER_CMD; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        log_success "🎉 爬虫运行完成！"
        
        # 显示数据统计
        log_info "📊 数据统计:"
        python3 -c "
import pymysql
conn = pymysql.connect(host='localhost', port=3307, user='root', password='099118', database='huan_hai')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM vessel_schedule')
total = cursor.fetchone()[0]
cursor.execute('SELECT MAX(data_version) FROM vessel_schedule')
version = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(DISTINCT vessel) FROM vessel_schedule WHERE data_version = %s', (version,))
vessels = cursor.fetchone()[0]
print(f'   总记录数: {total}')
print(f'   当前版本: {version}') 
print(f'   船舶数量: {vessels}')
conn.close()
"
    else
        log_error "❌ 爬虫运行失败"
        exit 1
    fi
}

# 检查Python依赖
if ! command -v python3 &> /dev/null; then
    log_error "Python3 未安装"
    exit 1
fi

if ! python3 -c "import pymysql, requests" &> /dev/null; then
    log_error "缺少Python依赖，请安装: pip install pymysql requests"
    exit 1
fi

# 运行主函数
main "$@"