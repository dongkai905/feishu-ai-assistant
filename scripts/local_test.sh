#!/bin/bash

# 飞书AI助手本地测试脚本
# 用于在没有Docker的环境中测试所有功能

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
    echo "飞书AI助手本地测试脚本"
    echo ""
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -a, --all          执行所有测试"
    echo "  -d, --deps         检查依赖"
    echo "  -c, --config       检查配置"
    echo "  -s, --server       测试服务器"
    echo "  -f, --feishu       测试飞书API"
    echo "  -t, --tests        运行单元测试"
    echo "  -p, --performance  性能测试"
    echo "  -h, --help         显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --all           # 执行所有测试"
    echo "  $0 --server        # 只测试服务器"
    echo "  $0 --feishu        # 只测试飞书API"
}

# 解析命令行参数
TEST_ALL=false
TEST_DEPS=false
TEST_CONFIG=false
TEST_SERVER=false
TEST_FEISHU=false
TEST_UNIT=false
TEST_PERF=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--all)
            TEST_ALL=true
            shift
            ;;
        -d|--deps)
            TEST_DEPS=true
            shift
            ;;
        -c|--config)
            TEST_CONFIG=true
            shift
            ;;
        -s|--server)
            TEST_SERVER=true
            shift
            ;;
        -f|--feishu)
            TEST_FEISHU=true
            shift
            ;;
        -t|--tests)
            TEST_UNIT=true
            shift
            ;;
        -p|--performance)
            TEST_PERF=true
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

# 如果没有指定任何测试，默认执行所有测试
if [ "$TEST_ALL" = false ] && [ "$TEST_DEPS" = false ] && [ "$TEST_CONFIG" = false ] && [ "$TEST_SERVER" = false ] && [ "$TEST_FEISHU" = false ] && [ "$TEST_UNIT" = false ] && [ "$TEST_PERF" = false ]; then
    TEST_ALL=true
fi

# 如果指定了所有测试，设置所有标志为true
if [ "$TEST_ALL" = true ]; then
    TEST_DEPS=true
    TEST_CONFIG=true
    TEST_SERVER=true
    TEST_FEISHU=true
    TEST_UNIT=true
    TEST_PERF=true
fi

# 主函数
main() {
    log_info "开始飞书AI助手本地测试"
    
    # 检查依赖
    if [ "$TEST_DEPS" = true ]; then
        check_dependencies
    fi
    
    # 检查配置
    if [ "$TEST_CONFIG" = true ]; then
        check_configuration
    fi
    
    # 测试服务器
    if [ "$TEST_SERVER" = true ]; then
        test_server
    fi
    
    # 测试飞书API
    if [ "$TEST_FEISHU" = true ]; then
        test_feishu_api
    fi
    
    # 运行单元测试
    if [ "$TEST_UNIT" = true ]; then
        run_unit_tests
    fi
    
    # 性能测试
    if [ "$TEST_PERF" = true ]; then
        performance_test
    fi
    
    # 显示测试总结
    show_test_summary
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    echo ""
    echo "Python依赖检查:"
    echo "----------------"
    
    # 检查Python版本
    local python_version=$(python3 --version 2>&1 | awk '{print $2}')
    log_info "Python版本: $python_version"
    
    # 检查主要依赖
    local dependencies=(
        "fastapi"
        "uvicorn"
        "lark-oapi"
        "python-dotenv"
        "pydantic"
        "sqlalchemy"
        "redis"
        "celery"
        "prometheus-client"
    )
    
    for dep in "${dependencies[@]}"; do
        if python3 -c "import $dep" 2>/dev/null; then
            log_success "$dep: 已安装"
        else
            log_error "$dep: 未安装"
        fi
    done
    
    echo ""
    echo "系统依赖检查:"
    echo "--------------"
    
    # 检查系统命令
    local commands=("python3" "pip3" "curl" "git" "make")
    for cmd in "${commands[@]}"; do
        if command -v $cmd > /dev/null 2>&1; then
            log_success "$cmd: 可用"
        else
            log_warning "$cmd: 不可用"
        fi
    done
    
    echo ""
}

# 检查配置
check_configuration() {
    log_info "检查配置..."
    
    echo ""
    echo "配置文件检查:"
    echo "--------------"
    
    # 检查环境变量文件
    local config_files=(".env" ".env.production" "Dockerfile" "docker-compose.yml" "requirements.txt")
    
    for file in "${config_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "$file: 存在"
            
            # 检查文件大小
            local file_size=$(wc -l < "$file" 2>/dev/null || echo "0")
            if [ "$file_size" -gt 0 ]; then
                log_info "  行数: $file_size"
            fi
        else
            log_error "$file: 不存在"
        fi
    done
    
    # 检查源代码目录
    echo ""
    echo "源代码检查:"
    echo "------------"
    
    local source_files=(
        "src/main.py"
        "src/feishu_client.py"
        "src/calendar_assistant.py"
        "src/task_assistant.py"
        "tests/test_main.py"
    )
    
    for file in "${source_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "$file: 存在"
        else
            log_error "$file: 不存在"
        fi
    done
    
    # 检查脚本目录
    echo ""
    echo "脚本文件检查:"
    echo "--------------"
    
    local script_files=(
        "scripts/deploy.sh"
        "scripts/backup.sh"
        "scripts/monitor_setup.sh"
        "scripts/health_check.sh"
        "scripts/test_api.py"
    )
    
    for script in "${script_files[@]}"; do
        if [ -f "$script" ]; then
            log_success "$script: 存在"
            
            # 检查执行权限
            if [ -x "$script" ]; then
                log_info "  可执行: 是"
            else
                log_warning "  可执行: 否"
            fi
        else
            log_error "$script: 不存在"
        fi
    done
    
    echo ""
}

# 测试服务器
test_server() {
    log_info "测试服务器..."
    
    echo ""
    echo "服务器测试:"
    echo "------------"
    
    # 检查服务器是否在运行
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        log_success "服务器: 正在运行"
        
        # 测试API端点
        test_api_endpoints
    else
        log_warning "服务器: 未运行，尝试启动..."
        
        # 尝试启动服务器
        start_server_test
    fi
    
    echo ""
}

# 测试API端点
test_api_endpoints() {
    log_info "测试API端点..."
    
    local endpoints=(
        "/"
        "/health"
        "/version"
        "/system/info"
        "/calendar/today"
        "/tasks"
        "/assistant/daily-report"
    )
    
    local total_endpoints=${#endpoints[@]}
    local successful_endpoints=0
    
    for endpoint in "${endpoints[@]}"; do
        local url="http://localhost:8000$endpoint"
        
        if curl -s -f "$url" > /dev/null 2>&1; then
            log_success "$endpoint: 正常"
            successful_endpoints=$((successful_endpoints + 1))
        else
            log_error "$endpoint: 失败"
        fi
    done
    
    # 计算成功率
    local success_rate=$((successful_endpoints * 100 / total_endpoints))
    log_info "API端点测试完成: $successful_endpoints/$total_endpoints ($success_rate%)"
    
    if [ $success_rate -eq 100 ]; then
        log_success "所有API端点测试通过！"
    elif [ $success_rate -ge 80 ]; then
        log_warning "大部分API端点测试通过"
    else
        log_error "API端点测试失败较多"
    fi
}

# 启动服务器测试
start_server_test() {
    log_info "启动测试服务器..."
    
    # 检查是否已经有服务器进程
    local server_pid=$(lsof -ti:8000 2>/dev/null || echo "")
    
    if [ -n "$server_pid" ]; then
        log_warning "端口8000已被占用，PID: $server_pid"
        return
    fi
    
    # 在后台启动服务器
    python3 src/main.py > /tmp/feishu_server_test.log 2>&1 &
    local server_pid=$!
    
    # 等待服务器启动
    log_info "等待服务器启动..."
    sleep 5
    
    # 检查服务器是否启动成功
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        log_success "测试服务器启动成功 (PID: $server_pid)"
        
        # 测试API端点
        test_api_endpoints
        
        # 停止测试服务器
        log_info "停止测试服务器..."
        kill $server_pid 2>/dev/null || true
        wait $server_pid 2>/dev/null || true
    else
        log_error "测试服务器启动失败"
        
        # 显示日志
        log_info "服务器日志:"
        tail -20 /tmp/feishu_server_test.log
        
        # 清理
        kill $server_pid 2>/dev/null || true
    fi
}

# 测试飞书API
test_feishu_api() {
    log_info "测试飞书API..."
    
    echo ""
    echo "飞书API测试:"
    echo "-------------"
    
    # 检查环境变量
    if [ ! -f ".env.production" ]; then
        log_error "生产环境配置文件不存在"
        return
    fi
    
    # 加载环境变量
    source .env.production 2>/dev/null || true
    
    # 检查凭证
    if [ -z "$FEISHU_APP_ID" ] || [ -z "$FEISHU_APP_SECRET" ]; then
        log_error "飞书凭证未配置"
        return
    fi
    
    log_success "飞书凭证: 已配置"
    log_info "App ID: $FEISHU_APP_ID"
    
    # 创建测试脚本
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
    
    # 运行测试
    if python3 "$test_script"; then
        log_success "飞书API连接测试: 通过"
    else
        log_error "飞书API连接测试: 失败"
    fi
    
    # 清理临时文件
    rm -f "$test_script"
    
    echo ""
}

# 运行单元测试
run_unit_tests() {
    log_info "运行单元测试..."
    
    echo ""
    echo "单元测试:"
    echo "----------"
    
    if [ -f "tests/test_main.py" ]; then
        # 运行测试
        if python3 -m pytest tests/ -v; then
            log_success "单元测试: 全部通过"
        else
            log_error "单元测试: 有失败用例"
        fi
    else
        log_warning "单元测试文件不存在，跳过"
    fi
    
    echo ""
}

# 性能测试
performance_test() {
    log_info "性能测试..."
    
    echo ""
    echo "性能测试:"
    echo "----------"
    
    # 检查服务器是否运行
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        log_warning "服务器未运行，跳过性能测试"
        return
    fi
    
    # 测试响应时间
    log_info "测试API响应时间..."
    
    local total_requests=10
    local total_time=0
    local successful_requests=0
    
    for i in $(seq 1 $total_requests); do
        local start_time=$(date +%s%N)
        
        if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
            local end_time=$(date +%s%N)
            local request_time=$((($end_time - $start_time) / 1000000))
            total_time=$((total_time + request_time))
            successful_requests=$((successful_requests + 1))
            
            log_info "请求 $i: ${request_time}ms"
        else
            log_error "请求 $i: 失败"
        fi
        
        # 短暂延迟
        sleep 0.1
    done
    
    # 计算统计信息
    if [ $successful_requests -gt 0 ]; then
        local avg_time=$((total_time / successful_requests))
        local success_rate=$((successful_requests * 100 / total_requests))
        
        log_info "性能测试结果:"
        log_info "  总请求数: $total_requests"
        log_info "  成功请求: $successful_requests ($success_rate%)"
        log_info "  平均响应时间: ${avg_time}ms"
        
        if [ $avg_time -lt 100 ]; then
            log_success "性能: 优秀 (<100ms)"
        elif [ $avg_time -lt 500 ]; then
            log_success "性能: 良好 (<500ms)"
        elif [ $avg_time -lt 1000 ]; then
            log_warning "性能: 一般 (<1000ms)"
        else
            log_error "性能: 较差 (>1000ms)"
        fi
    else
        log_error "性能测试: 所有请求都失败"
    fi
    
    echo ""
}

# 显示测试总结
show_test_summary() {
    echo ""
    echo "测试总结:"
    echo "----------"
    
    log_info "测试完成时间: $(date)"
    log_info "所有测试执行完毕"
    
    echo ""
    log_success "飞书AI助手本地测试完成！"
    echo ""
    
    # 显示下一步建议
    log_info "下一步建议:"
    echo "1. 如果所有测试通过，系统可以投入生产使用"
    echo "2. 如果有测试失败，请根据错误信息进行修复"
    echo "3. 运行生产部署脚本: ./scripts/deploy.sh --env production"
    echo "4. 设置监控系统: ./scripts/monitor_setup.sh --setup"
    echo "5. 定期健康检查: ./scripts/health_check.sh --all"
    echo ""
}

# 运行主函数
main "$@"