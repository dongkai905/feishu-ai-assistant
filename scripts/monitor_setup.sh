#!/bin/bash

# 飞书AI助手监控系统设置脚本
# 使用方法: ./scripts/monitor_setup.sh

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
    echo "飞书AI助手监控系统设置脚本"
    echo ""
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -s, --setup         设置监控系统"
    echo "  -c, --check         检查监控系统状态"
    echo "  -d, --dashboards    导入Grafana仪表板"
    echo "  -a, --alerts        设置告警规则"
    echo "  -r, --restart       重启监控服务"
    echo "  -h, --help          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --setup           # 完整设置监控系统"
    echo "  $0 --check           # 检查监控状态"
    echo "  $0 --dashboards      # 导入仪表板"
}

# 解析命令行参数
SETUP=false
CHECK=false
DASHBOARDS=false
ALERTS=false
RESTART=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--setup)
            SETUP=true
            shift
            ;;
        -c|--check)
            CHECK=true
            shift
            ;;
        -d|--dashboards)
            DASHBOARDS=true
            shift
            ;;
        -a|--alerts)
            ALERTS=true
            shift
            ;;
        -r|--restart)
            RESTART=true
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

# 如果没有指定任何操作，默认执行完整设置
if [ "$SETUP" = false ] && [ "$CHECK" = false ] && [ "$DASHBOARDS" = false ] && [ "$ALERTS" = false ] && [ "$RESTART" = false ]; then
    SETUP=true
fi

# 主函数
main() {
    log_info "开始飞书AI助手监控系统设置"
    
    # 检查监控系统状态
    if [ "$CHECK" = true ] || [ "$SETUP" = true ]; then
        check_monitoring_status
    fi
    
    # 设置监控系统
    if [ "$SETUP" = true ]; then
        setup_monitoring_system
    fi
    
    # 导入Grafana仪表板
    if [ "$DASHBOARDS" = true ] || [ "$SETUP" = true ]; then
        import_grafana_dashboards
    fi
    
    # 设置告警规则
    if [ "$ALERTS" = true ] || [ "$SETUP" = true ]; then
        setup_alert_rules
    fi
    
    # 重启监控服务
    if [ "$RESTART" = true ]; then
        restart_monitoring_services
    fi
    
    # 显示监控信息
    show_monitoring_info
}

# 检查监控系统状态
check_monitoring_status() {
    log_info "检查监控系统状态..."
    
    echo ""
    echo "服务状态检查:"
    echo "--------------"
    
    # 检查Prometheus
    if docker-compose ps | grep -q "prometheus.*Up"; then
        log_success "Prometheus: 运行中"
        
        # 检查Prometheus目标
        log_info "检查Prometheus目标..."
        curl -s http://localhost:9090/api/v1/targets | python3 -m json.tool | grep -A5 '"health"'
    else
        log_error "Prometheus: 未运行"
    fi
    
    # 检查Grafana
    if docker-compose ps | grep -q "grafana.*Up"; then
        log_success "Grafana: 运行中"
        
        # 检查Grafana数据源
        log_info "检查Grafana数据源..."
        curl -s -u admin:Grafana_Admin_2026! http://localhost:3000/api/datasources | python3 -m json.tool | grep '"name"'
    else
        log_error "Grafana: 未运行"
    fi
    
    # 检查API指标端点
    log_info "检查API指标端点..."
    if curl -s http://localhost:8000/metrics | grep -q "TYPE"; then
        log_success "API指标端点: 正常"
    else
        log_error "API指标端点: 不可用"
    fi
    
    # 检查Redis指标
    log_info "检查Redis指标..."
    if docker-compose exec redis redis-cli INFO | grep -q "uptime_in_seconds"; then
        log_success "Redis指标: 正常"
    else
        log_warning "Redis指标: 需要配置Redis exporter"
    fi
    
    echo ""
}

# 设置监控系统
setup_monitoring_system() {
    log_info "设置监控系统..."
    
    # 创建必要的目录
    mkdir -p prometheus grafana/dashboards grafana/datasources
    
    # 检查配置文件是否存在
    if [ ! -f "prometheus/prometheus.yml" ]; then
        log_warning "Prometheus配置文件不存在，创建默认配置..."
        create_prometheus_config
    fi
    
    if [ ! -f "grafana/datasources/prometheus.yml" ]; then
        log_warning "Grafana数据源配置不存在，创建默认配置..."
        create_grafana_datasource
    fi
    
    if [ ! -f "grafana/dashboards/dashboards.yml" ]; then
        log_warning "Grafana仪表板配置不存在，创建默认配置..."
        create_grafana_dashboards_config
    fi
    
    # 启动监控服务
    log_info "启动监控服务..."
    docker-compose up -d prometheus grafana
    
    # 等待服务启动
    log_info "等待监控服务启动..."
    sleep 15
    
    # 检查服务是否正常运行
    if curl -s http://localhost:9090/-/healthy > /dev/null; then
        log_success "Prometheus启动成功"
    else
        log_error "Prometheus启动失败"
    fi
    
    if curl -s http://localhost:3000/api/health > /dev/null; then
        log_success "Grafana启动成功"
    else
        log_error "Grafana启动失败"
    fi
    
    log_success "监控系统设置完成"
}

# 创建Prometheus配置
create_prometheus_config() {
    cat > prometheus/prometheus.yml << 'EOF'
# 全局配置
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  scrape_timeout: 10s

# 告警规则文件
rule_files:
  # - "alert_rules.yml"

# 抓取配置
scrape_configs:
  # Prometheus自身监控
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 30s

  # 飞书AI助手API监控
  - job_name: 'feishu-ai-assistant-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
    scrape_timeout: 10s
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'feishu-ai-assistant-api'

  # Redis监控
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s
    metrics_path: '/metrics'
    params:
      format: [prometheus]
EOF
    
    log_success "Prometheus配置文件创建完成"
}

# 创建Grafana数据源配置
create_grafana_datasource() {
    cat > grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      timeInterval: 15s
      queryTimeout: 60s
      httpMethod: POST
EOF
    
    log_success "Grafana数据源配置创建完成"
}

# 创建Grafana仪表板配置
create_grafana_dashboards_config() {
    cat > grafana/dashboards/dashboards.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF
    
    log_success "Grafana仪表板配置创建完成"
}

# 导入Grafana仪表板
import_grafana_dashboards() {
    log_info "导入Grafana仪表板..."
    
    # 创建仪表板目录
    mkdir -p grafana/dashboards
    
    # 创建API监控仪表板
    create_api_monitoring_dashboard
    
    # 创建系统监控仪表板
    create_system_monitoring_dashboard
    
    # 创建数据库监控仪表板
    create_database_monitoring_dashboard
    
    # 重启Grafana以加载新仪表板
    docker-compose restart grafana
    
    log_success "Grafana仪表板导入完成"
}

# 创建API监控仪表板
create_api_monitoring_dashboard() {
    cat > grafana/dashboards/api_monitoring.json << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "飞书AI助手 API 监控",
    "tags": ["api", "monitoring", "feishu"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "API请求率",
        "type": "graph",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{endpoint}}",
            "refId": "A"
          }
        ]
      },
      {
        "id": 2,
        "title": "API响应时间",
        "type": "graph",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P95响应时间",
            "refId": "A"
          }
        ]
      },
      {
        "id": 3,
        "title": "错误率",
        "type": "stat",
        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 8},
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m])) * 100",
            "legendFormat": "错误率",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "red", "value": 5}
              ]
            }
          }
        }
      }
    ],
    "time": {"from": "now-1h", "to": "now"},
    "refresh": "10s"
  },
  "overwrite": true
}
EOF
    
    log_success "API监控仪表板创建完成"
}

# 创建系统监控仪表板
create_system_monitoring_dashboard() {
    cat > grafana/dashboards/system_monitoring.json << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "系统监控",
    "tags": ["system", "monitoring"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "CPU使用率",
        "type": "gauge",
        "gridPos": {"h": 6, "w": 6, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "100 - (avg by(instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "CPU使用率",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 70},
                {"color": "red", "value": 90}
              ]
            }
          }
        }
      },
      {
        "id": 2,
        "title": "内存使用率",
        "type": "gauge",
        "gridPos": {"h": 6, "w": 6, "x": 6, "y": 0},
        "targets": [
          {
            "expr": "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100",
            "legendFormat": "内存使用率",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "unit": "percent",
            "min": 0,
            "max": 100,
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 80},
                {"color": "red", "value": 90}
              ]
            }
          }
        }
      }
    ],
    "time": {"from": "now-1h", "to": "now"},
    "refresh": "10s"
  },
  "overwrite": true
}
EOF
    
    log_success "系统监控仪表板创建完成"
}

# 创建数据库监控仪表板
create_database_monitoring_dashboard() {
    cat > grafana/dashboards/database_monitoring.json << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "数据库监控",
    "tags": ["database", "postgresql", "redis"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "数据库连接数",
        "type": "graph",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "pg_stat_database_numbackends",
            "legendFormat": "{{datname}}",
            "refId": "A"
          }
        ]
      },
      {
        "id": 2,
        "title": "Redis内存使用",
        "type": "graph",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
        "targets": [
          {
            "expr": "redis_memory_used_bytes",
            "legendFormat": "已用内存",
            "refId": "A"
          },
          {
            "expr": "redis_memory_max_bytes",
            "legendFormat": "最大内存",
            "refId": "B"
          }
        ]
      }
    ],
    "time": {"from": "now-1h", "to": "now"},
    "refresh": "10s"
  },
  "overwrite": true
}
EOF
    
    log_success "数据库监控仪表板创建完成"
}

# 设置告警规则
setup_alert_rules() {
    log_info "设置告警规则..."
    
    # 创建告警规则文件
    cat > prometheus/alert_rules.yml << 'EOF'
groups:
  - name: feishu_ai_alerts
    rules:
      # API错误率告警
      - alert: HighAPIErrorRate
        expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100 > 5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "API错误率过高"
          description: "API错误率超过5% (当前值: {{ $value }}%)"
      
      # 高响应时间告警
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "API响应时间过长"
          description: "P95响应时间超过2秒 (当前值: {{ $value }}秒)"
      
      # 服务宕机告警
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "服务 {{ $labels.instance }} 宕机"
          description: "服务 {{ $labels.instance }} 已经宕机超过1分钟"
      
      # 高内存使用告警
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "内存使用率过高"
          description: "内存使用率超过90% (当前值: {{ $value }}%)"
      
      # 高CPU使用告警
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CPU使用率过高"
          description: "CPU使用率超过80% (当前值: {{ $value }}%)"
EOF
    
    # 更新Prometheus配置以包含告警规则
    if grep -q "rule_files" prometheus/prometheus.yml; then
        sed -i '' 's|# - "alert_rules.yml"|- "alert_rules.yml"|' prometheus/prometheus.yml
    fi
    
    # 重启Prometheus以加载告警规则
    docker-compose restart prometheus
    
    log_success "告警规则设置完成"
}

# 重启监控服务
restart_monitoring_services() {
    log_info "重启监控服务..."
    
    docker-compose restart prometheus grafana
    
    # 等待服务重启
    sleep 10
    
    # 检查服务状态
    if curl -s http://localhost:9090/-/healthy > /dev/null; then
        log_success "Prometheus重启成功"
    else
        log_error "Prometheus重启失败"
    fi
    
    if curl -s http://localhost:3000/api/health > /dev/null; then
        log_success "Grafana重启成功"
    else
        log_error "Grafana重启失败"
    fi
    
    log_success "监控服务重启完成"
}

# 显示监控信息
show_monitoring_info() {
    echo ""
    log_success "监控系统设置完成！"
    echo ""
    echo "监控系统访问信息:"
    echo "  Grafana仪表板:    http://localhost:3000"
    echo "    用户名:         admin"
    echo "    密码:           Grafana_Admin_2026!"
    echo ""
    echo "  Prometheus:       http://localhost:9090"
    echo "  API指标端点:      http://localhost:8000/metrics"
    echo ""
    echo "预配置的仪表板:"
    echo "  1. 飞书AI助手 API 监控"
    echo "  2. 系统监控"
    echo "  3. 数据库监控"
    echo ""
    echo "告警规则:"
    echo "  1. API错误率 > 5% (持续2分钟)"
    echo "  2. API响应时间 > 2秒 (持续2分钟)"
    echo "  3. 服务宕机 (持续1分钟)"
    echo "  4. 内存使用率 > 90% (持续5分钟)"
    echo "  5. CPU使用率 > 80% (持续5分钟)"
    echo ""
    echo "管理命令:"
    echo "  检查状态:        $0 --check"
    echo "  重启服务:        $0 --restart"
    echo "  导入仪表板:      $0 --dashboards"
    echo "  设置告警:        $0 --alerts"
    echo ""
    log_info "监控系统设置时间: $(date)"
}

# 运行主函数
main "$@"