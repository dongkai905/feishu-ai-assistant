#!/bin/bash

# 飞书AI助手健康检查脚本
# 使用方法: ./scripts/health_check.sh

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

# 显示帮助
show_help() {
    echo "飞书AI助手健康检查脚本"
    echo ""
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -a, --all          执行所有健康检查"
    echo "  -s, --services     检查服务状态"
    echo "  -d, --database     检查数据库状态"
    echo "  -m, --monitoring   检查监控系统"
    echo "  -p, --performance  检查性能指标"
    echo "  -f, --feishu       检查飞书API连接"
    echo "  -r, --report       生成健康检查报告"
    echo "  -h, --help         显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --all           # 执行所有健康检查"
    echo "  $0 --services      # 只检查服务状态"
    echo "  $0 --report        # 生成详细报告"
}

# 解析命令行参数
CHECK_ALL=false
CHECK_SERVICES=false
CHECK_DATABASE=false
CHECK_MONITORING=false
CHECK_PERFORMANCE=false
CHECK_FEISHU=false
GENERATE_REPORT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--all)
            CHECK_ALL=true
            shift
            ;;
        -s|--services)
            CHECK_SERVICES=true
            shift
            ;;
        -d|--database)
            CHECK_DATABASE=true
            shift
            ;;
        -m|--monitoring)
            CHECK_MONITORING=true
            shift
            ;;
        -p|--performance)
            CHECK_PERFORMANCE=true
            shift
            ;;
        -f|--feishu)
            CHECK_FEISHU=true
            shift
            ;;
        -r|--report)
            GENERATE_REPORT=true
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

# 如果没有指定任何检查，默认执行所有检查
if [ "$CHECK_ALL" = false ] && [ "$CHECK_SERVICES" = false ] && [ "$CHECK_DATABASE" = false ] && [ "$CHECK_MONITORING" = false ] && [ "$CHECK_PERFORMANCE" = false ] && [ "$CHECK_FEISHU" = false ]; then
    CHECK_ALL=true
fi

# 如果指定了所有检查，设置所有标志为true
if [ "$CHECK_ALL" = true ]; then
    CHECK_SERVICES=true
    CHECK_DATABASE=true
    CHECK_MONITORING=true
    CHECK_PERFORMANCE=true
    CHECK_FEISHU=true
fi

# 报告文件
REPORT_FILE="health_check_report_$(date +%Y%m%d_%H%M%S).txt"

# 主函数
main() {
    log_info "开始飞书AI助手健康检查"
    
    # 初始化报告
    if [ "$GENERATE_REPORT" = true ]; then
        echo "飞书AI助手健康检查报告" > "$REPORT_FILE"
        echo "生成时间: $(date)" >> "$REPORT_FILE"
        echo "==========================================" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi
    
    # 检查服务状态
    if [ "$CHECK_SERVICES" = true ]; then
        check_services
    fi
    
    # 检查数据库状态
    if [ "$CHECK_DATABASE" = true ]; then
        check_database
    fi
    
    # 检查监控系统
    if [ "$CHECK_MONITORING" = true ]; then
        check_monitoring
    fi
    
    # 检查性能指标
    if [ "$CHECK_PERFORMANCE" = true ]; then
        check_performance
    fi
    
    # 检查飞书API连接
    if [ "$CHECK_FEISHU" = true ]; then
        check_feishu_api
    fi
    
    # 显示总结
    show_summary
    
    # 如果生成报告，显示报告位置
    if [ "$GENERATE_REPORT" = true ]; then
        echo "" >> "$REPORT_FILE"
        echo "检查完成时间: $(date)" >> "$REPORT_FILE"
        log_success "健康检查报告已生成: $REPORT_FILE"
    fi
}

# 记录到报告
log_to_report() {
    if [ "$GENERATE_REPORT" = true ]; then
        echo "$1" >> "$REPORT_FILE"
    fi
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    log_to_report "## 服务状态检查"
    log_to_report ""
    
    local all_healthy=true
    
    echo ""
    echo "服务状态:"
    echo "----------"
    
    # 获取所有服务状态
    local services=$(docker-compose ps --services)
    
    for service in $services; do
        local status=$(docker-compose ps $service | tail -1 | awk '{print $4}')
        
        if [ "$status" = "Up" ]; then
            log_success "$service: 运行中"
            log_to_report "✅ $service: 运行中"
        else
            log_error "$service: $status"
            log_to_report "❌ $service: $status"
            all_healthy=false
        fi
    done
    
    echo ""
    
    # 检查端口占用
    log_info "检查端口占用..."
    log_to_report ""
    log_to_report "### 端口占用检查"
    
    local ports="8000 5432 6379 80 3000 9090 5555"
    for port in $ports; do
        if lsof -i :$port > /dev/null 2>&1; then
            local process=$(lsof -i :$port | grep LISTEN | head -1 | awk '{print $1}')
            log_success "端口 $port: 被 $process 占用"
            log_to_report "✅ 端口 $port: 被 $process 占用"
        else
            log_warning "端口 $port: 未占用"
            log_to_report "⚠️  端口 $port: 未占用"
        fi
    done
    
    log_to_report ""
    
    if [ "$all_healthy" = true ]; then
        log_success "所有服务运行正常"
    else
        log_error "有服务运行异常"
    fi
}

# 检查数据库状态
check_database() {
    log_info "检查数据库状态..."
    log_to_report "## 数据库状态检查"
    log_to_report ""
    
    echo ""
    echo "数据库状态:"
    echo "------------"
    
    # 检查PostgreSQL
    if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        log_success "PostgreSQL: 连接正常"
        log_to_report "✅ PostgreSQL: 连接正常"
        
        # 检查数据库大小
        local db_size=$(docker-compose exec -T db psql -U postgres -d feishu_ai -t -c "SELECT pg_size_pretty(pg_database_size('feishu_ai'));" 2>/dev/null || echo "未知")
        log_info "数据库大小: $db_size"
        log_to_report "   数据库大小: $db_size"
        
        # 检查表数量
        local table_count=$(docker-compose exec -T db psql -U postgres -d feishu_ai -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null || echo "0")
        log_info "表数量: $table_count"
        log_to_report "   表数量: $table_count"
    else
        log_error "PostgreSQL: 连接失败"
        log_to_report "❌ PostgreSQL: 连接失败"
    fi
    
    # 检查Redis
    if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis: 连接正常"
        log_to_report "✅ Redis: 连接正常"
        
        # 检查Redis信息
        local redis_info=$(docker-compose exec redis redis-cli INFO | grep -E "(used_memory_human|connected_clients|uptime_in_days)" | head -3)
        log_info "Redis信息:"
        echo "$redis_info" | while read line; do
            log_info "  $line"
            log_to_report "   $line"
        done
    else
        log_error "Redis: 连接失败"
        log_to_report "❌ Redis: 连接失败"
    fi
    
    log_to_report ""
}

# 检查监控系统
check_monitoring() {
    log_info "检查监控系统..."
    log_to_report "## 监控系统检查"
    log_to_report ""
    
    echo ""
    echo "监控系统状态:"
    echo "--------------"
    
    # 检查Prometheus
    if curl -s http://localhost:9090/-/healthy > /dev/null; then
        log_success "Prometheus: 运行正常"
        log_to_report "✅ Prometheus: 运行正常"
        
        # 检查目标状态
        local targets=$(curl -s http://localhost:9090/api/v1/targets | python3 -c "
import json, sys
data = json.load(sys.stdin)
for target in data['data']['activeTargets']:
    print(f\"  {target['labels']['instance']}: {target['health']}\")
" 2>/dev/null || echo "  无法获取目标状态")
        
        log_info "Prometheus目标:"
        echo "$targets"
        log_to_report "   目标状态:"
        echo "$targets" | while read line; do
            log_to_report "   $line"
        done
    else
        log_error "Prometheus: 运行异常"
        log_to_report "❌ Prometheus: 运行异常"
    fi
    
    # 检查Grafana
    if curl -s http://localhost:3000/api/health > /dev/null; then
        log_success "Grafana: 运行正常"
        log_to_report "✅ Grafana: 运行正常"
        
        # 检查数据源
        local datasources=$(curl -s -u admin:Grafana_Admin_2026! http://localhost:3000/api/datasources | python3 -c "
import json, sys
data = json.load(sys.stdin)
for ds in data:
    print(f\"  {ds['name']}: {ds['type']}\")
" 2>/dev/null || echo "  无法获取数据源")
        
        log_info "Grafana数据源:"
        echo "$datasources"
        log_to_report "   数据源:"
        echo "$datasources" | while read line; do
            log_to_report "   $line"
        done
    else
        log_error "Grafana: 运行异常"
        log_to_report "❌ Grafana: 运行异常"
    fi
    
    # 检查API指标端点
    if curl -s http://localhost:8000/metrics | grep -q "TYPE"; then
        log_success "API指标端点: 正常"
        log_to_report "✅ API指标端点: 正常"
        
        # 获取指标数量
        local metric_count=$(curl -s http://localhost:8000/metrics | grep -c "^[^#]" || echo "0")
        log_info "指标数量: $metric_count"
        log_to_report "   指标数量: $metric_count"
    else
        log_error "API指标端点: 不可用"
        log_to_report "❌ API指标端点: 不可用"
    fi
    
    log_to_report ""
}

# 检查性能指标
check_performance() {
    log_info "检查性能指标..."
    log_to_report "## 性能指标检查"
    log_to_report ""
    
    echo ""
    echo "性能指标:"
    echo "----------"
    
    # 检查API响应时间
    local start_time=$(date +%s%N)
    if curl -s http://localhost:8000/health > /dev/null; then
        local end_time=$(date +%s%N)
        local response_time=$((($end_time - $start_time) / 1000000))
        
        if [ $response_time -lt 100 ]; then
            log_success "API响应时间: ${response_time}ms (优秀)"
            log_to_report "✅ API响应时间: ${response_time}ms (优秀)"
        elif [ $response_time -lt 500 ]; then
            log_success "API响应时间: ${response_time}ms (良好)"
            log_to_report "✅ API响应时间: ${response_time}ms (良好)"
        else
            log_warning "API响应时间: ${response_time}ms (较慢)"
            log_to_report "⚠️  API响应时间: ${response_time}ms (较慢)"
        fi
    else
        log_error "API健康检查失败"
        log_to_report "❌ API健康检查失败"
    fi
    
    # 检查系统资源
    log_info "系统资源使用:"
    log_to_report "### 系统资源使用"
    
    # CPU使用率
    local cpu_usage=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')
    if [ $(echo "$cpu_usage < 70" | bc) -eq 1 ]; then
        log_success "CPU使用率: ${cpu_usage}% (正常)"
        log_to_report "✅ CPU使用率: ${cpu_usage}% (正常)"
    else
        log_warning "CPU使用率: ${cpu_usage}% (较高)"
        log_to_report "⚠️  CPU使用率: ${cpu_usage}% (较高)"
    fi
    
    # 内存使用率
    local mem_total=$(sysctl -n hw.memsize)
    local mem_free=$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
    local page_size=$(vm_stat | grep "page size" | awk '{print $8}' | sed 's/\.//')
    local mem_free_bytes=$((mem_free * page_size))
    local mem_used_percent=$((100 - (mem_free_bytes * 100 / mem_total)))
    
    if [ $mem_used_percent -lt 80 ]; then
        log_success "内存使用率: ${mem_used_percent}% (正常)"
        log_to_report "✅ 内存使用率: ${mem_used_percent}% (正常)"
    else
        log_warning "内存使用率: ${mem_used_percent}% (较高)"
        log_to_report "⚠️  内存使用率: ${mem_used_percent}% (较高)"
    fi
    
    # 磁盘使用率
    local disk_usage=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $disk_usage -lt 80 ]; then
        log_success "磁盘使用率: ${disk_usage}% (正常)"
        log_to_report "✅ 磁盘使用率: ${disk_usage}% (正常)"
    else
        log_warning "磁盘使用率: ${disk_usage}% (较高)"
        log_to_report "⚠️  磁盘使用率: ${disk_usage}% (较高)"
    fi
    
    log_to_report ""
}

# 检查飞书API连接
check_feishu_api() {
    log_info "检查飞书API连接..."
    log_to_report "## 飞书API连接检查"
    log_to_report ""
    
    echo ""
    echo "飞书API连接:"
    echo "-------------"
    
    # 检查环境变量
    if [ -f ".env.production" ]; then
        source .env.production
        
        if [ -n "$FEISHU_APP_ID" ] && [ -n "$FEISHU_APP_SECRET" ]; then
            log_success "飞书凭证: 已配置"
            log_to_report "✅ 飞书凭证: 已配置"
            log_info "App ID: $FEISHU_APP_ID"
            log_to_report "   App ID: $FEISHU_APP_ID"
        else
            log_error "飞书凭证: 未配置"
            log_to_report "❌ 飞书凭证: 未配置"
        fi
    else
        log_error "环境变量文件不存在"
        log_to_report "❌ 环境变量文件不存在"
    fi
    
    # 尝试连接飞书API
    log_info "测试飞书API连接..."
    
    # 使用Python脚本测试连接
    local test_script=$(mktemp)
    cat > "$test_script" << 'EOF'
import os
import sys
from lark_oapi import Client, Config

# 从环境变量获取凭证
app_id = os.getenv('FEISHU_APP_ID')
app_secret = os.getenv('FEISHU_APP_SECRET')

if not app_id or not app_secret:
    print("ERROR: 飞书凭证未配置")
    sys.exit(1)

try:
    # 创建配置
    config = Config.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .build()
    
    # 创建客户端
    client = Client(config)
    
    # 测试获取访问令牌
    from lark_oapi.api.authen.v1 import GetAccessTokenRequest
    request = GetAccessTokenRequest.builder() \
        .request_body(GetAccessTokenRequest.RequestBody.builder()
            .app_id(app_id)
            .app_secret(app_secret)
            .build()) \
        .build()
    
    response = client.authen.v1.access_token.get(request)
    
    if response.success():
        print("SUCCESS: 飞书API连接正常")
        print(f"令牌有效期: {response.data.expire}秒")
        sys.exit(0)
    else:
        print(f"ERROR: 飞书API连接失败: {response.msg}")
        sys.exit(1)
        
except Exception as e:
    print(f"ERROR: 飞书API连接异常: {str(e)}")
    sys.exit(1)
EOF
    
    # 运行测试脚本
    if source .env.production 2>/dev/null && python3 "$test_script"; then
        log_success "飞书API: 连接正常"
        log_to_report "✅ 飞书API: 连接正常"
    else
        log_error "飞书API: 连接失败"
        log_to_report "❌ 飞书API: 连接失败"
    fi
    
    # 清理临时文件
    rm -f "$test_script"
    
    log_to_report ""
}

# 显示总结
show_summary() {
    echo ""
    echo "健康检查总结:"
    echo "--------------"
    
    local total_checks=0
    local passed_checks=0
    local failed_checks=0
    local warning_checks=0
    
    # 从报告中统计结果
    if [ -f "$REPORT_FILE" ]; then
        total_checks=$(grep -c -E "(✅|❌|⚠️)" "$REPORT_FILE" || echo "0")
        passed_checks=$(grep -c "✅" "$REPORT_FILE" || echo "0")
        failed_checks=$(grep -c "❌" "$REPORT_FILE" || echo "0")
        warning_checks=$(grep -c "⚠️" "$REPORT_FILE" || echo "0")
    fi
    
    echo "总检查项: $total_checks"
    echo "通过: $passed_checks"
    echo "失败: $failed_checks"
    echo "警告: $warning_checks"
    
    # 计算通过率
    if [ $total_checks -gt 0 ]; then
        local pass_rate=$((passed_checks * 100 / total_checks))
        echo "通过率: $pass_rate%"
        
        if [ $pass_rate -ge 90 ]; then
            log_success "系统健康状态: 优秀"
        elif [ $pass_rate -ge 70 ]; then
            log_warning "系统健康状态: 良好"
        else
            log_error "系统健康状态: 需要关注"
        fi
    fi
    
    echo ""
    
    # 显示建议
    if [ $failed_checks -gt 0 ]; then
        log_error "发现 $failed_checks 个严重问题，需要立即处理:"
        grep "❌" "$REPORT_FILE" | head -5
        echo ""
    fi
    
    if [ $warning_checks -gt 0 ]; then
        log_warning "发现 $warning_checks 个警告，建议处理:"
        grep "⚠️" "$REPORT_FILE" | head -5
        echo ""
    fi
    
    if [ $failed_checks -eq 0 ] && [ $warning_checks -eq 0 ]; then
        log_success "所有检查通过，系统运行正常！"
    fi
    
    echo ""
    log_info "健康检查完成时间: $(date)"
}

# 运行主函数
main "$@"