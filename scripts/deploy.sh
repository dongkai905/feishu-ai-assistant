#!/bin/bash

# 飞书AI助手生产部署脚本
# 使用方法: ./scripts/deploy.sh [环境]
# 环境: dev, staging, production (默认: production)

set -e  # 遇到错误立即退出

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

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "命令 $1 未找到，请先安装"
        exit 1
    fi
}

# 显示帮助
show_help() {
    echo "飞书AI助手部署脚本"
    echo ""
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -e, --env ENV       部署环境 (dev, staging, production)"
    echo "  -b, --build         重新构建Docker镜像"
    echo "  -u, --up            启动所有服务"
    echo "  -d, --down          停止所有服务"
    echo "  -r, --restart       重启所有服务"
    echo "  -l, --logs          查看服务日志"
    echo "  -s, --status        查看服务状态"
    echo "  -c, --clean         清理未使用的Docker资源"
    echo "  -h, --help          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --env production --build --up  # 构建并启动生产环境"
    echo "  $0 --restart                       # 重启当前环境服务"
    echo "  $0 --logs                          # 查看服务日志"
}

# 解析命令行参数
ENVIRONMENT="production"
ACTION="up"
BUILD=false
CLEAN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -b|--build)
            BUILD=true
            shift
            ;;
        -u|--up)
            ACTION="up"
            shift
            ;;
        -d|--down)
            ACTION="down"
            shift
            ;;
        -r|--restart)
            ACTION="restart"
            shift
            ;;
        -l|--logs)
            ACTION="logs"
            shift
            ;;
        -s|--status)
            ACTION="status"
            shift
            ;;
        -c|--clean)
            CLEAN=true
            shift
            ;;
        -h|--help)
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

# 设置环境变量文件
ENV_FILE=".env.$ENVIRONMENT"
if [ ! -f "$ENV_FILE" ]; then
    log_warning "环境变量文件 $ENV_FILE 不存在，使用 .env.production"
    ENV_FILE=".env.production"
fi

if [ ! -f "$ENV_FILE" ]; then
    log_error "环境变量文件 $ENV_FILE 不存在，请先创建"
    exit 1
fi

# 检查必需的命令
check_command docker
check_command docker-compose

# 主函数
main() {
    log_info "开始部署飞书AI助手 (环境: $ENVIRONMENT)"
    
    # 清理未使用的Docker资源
    if [ "$CLEAN" = true ]; then
        log_info "清理未使用的Docker资源..."
        docker system prune -f
        log_success "Docker资源清理完成"
    fi
    
    case $ACTION in
        up)
            deploy_up
            ;;
        down)
            deploy_down
            ;;
        restart)
            deploy_restart
            ;;
        logs)
            deploy_logs
            ;;
        status)
            deploy_status
            ;;
        *)
            log_error "未知操作: $ACTION"
            exit 1
            ;;
    esac
}

# 部署启动
deploy_up() {
    log_info "启动飞书AI助手服务..."
    
    # 构建镜像（如果需要）
    if [ "$BUILD" = true ]; then
        log_info "构建Docker镜像..."
        docker-compose --env-file $ENV_FILE build --no-cache
        log_success "Docker镜像构建完成"
    fi
    
    # 启动服务
    log_info "启动所有服务..."
    docker-compose --env-file $ENV_FILE up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    deploy_status
    
    # 显示访问信息
    show_access_info
}

# 部署停止
deploy_down() {
    log_info "停止飞书AI助手服务..."
    docker-compose --env-file $ENV_FILE down
    log_success "服务已停止"
}

# 部署重启
deploy_restart() {
    log_info "重启飞书AI助手服务..."
    docker-compose --env-file $ENV_FILE restart
    log_success "服务已重启"
    
    # 等待服务启动
    sleep 5
    deploy_status
}

# 查看日志
deploy_logs() {
    log_info "查看服务日志..."
    docker-compose --env-file $ENV_FILE logs -f --tail=100
}

# 查看状态
deploy_status() {
    log_info "服务状态:"
    echo ""
    
    # 使用docker-compose ps获取状态
    docker-compose --env-file $ENV_FILE ps
    
    echo ""
    
    # 检查关键服务健康状态
    check_service_health "api" "8000"
    check_service_health "db" "5432"
    check_service_health "redis" "6379"
    check_service_health "nginx" "80"
    check_service_health "prometheus" "9090"
    check_service_health "grafana" "3000"
    check_service_health "flower" "5555"
}

# 检查服务健康状态
check_service_health() {
    local service=$1
    local port=$2
    
    if docker-compose --env-file $ENV_FILE ps | grep -q "$service.*Up"; then
        log_success "$service 服务正在运行 (端口: $port)"
    else
        log_error "$service 服务未运行"
    fi
}

# 显示访问信息
show_access_info() {
    echo ""
    log_info "飞书AI助手部署完成！"
    echo ""
    echo "访问地址:"
    echo "  API服务:      http://localhost:8000"
    echo "  API文档:      http://localhost:8000/docs"
    echo "  健康检查:     http://localhost:8000/health"
    echo ""
    echo "监控系统:"
    echo "  Grafana:      http://localhost:3000 (用户名: admin, 密码: Grafana_Admin_2026!)"
    echo "  Prometheus:   http://localhost:9090"
    echo "  Flower:       http://localhost:5555 (Celery监控)"
    echo ""
    echo "数据库:"
    echo "  PostgreSQL:   localhost:5432 (数据库: feishu_ai)"
    echo "  Redis:        localhost:6379"
    echo ""
    echo "管理命令:"
    echo "  查看日志:     $0 --logs"
    echo "  查看状态:     $0 --status"
    echo "  重启服务:     $0 --restart"
    echo "  停止服务:     $0 --down"
    echo ""
    log_info "部署时间: $(date)"
}

# 运行主函数
main "$@"