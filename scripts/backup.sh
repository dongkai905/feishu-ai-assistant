#!/bin/bash

# 飞书AI助手备份脚本
# 使用方法: ./scripts/backup.sh [备份类型]
# 备份类型: full, database, logs, config (默认: full)

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
    echo "飞书AI助手备份脚本"
    echo ""
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -t, --type TYPE     备份类型 (full, database, logs, config)"
    echo "  -d, --dest DIR      备份目标目录 (默认: ./backups)"
    echo "  -r, --retention DAYS保留天数 (默认: 30)"
    echo "  -c, --clean         清理过期备份"
    echo "  -l, --list          列出备份文件"
    echo "  -h, --help          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --type full       # 执行完整备份"
    echo "  $0 --type database   # 只备份数据库"
    echo "  $0 --clean --retention 7  # 清理7天前的备份"
}

# 解析命令行参数
BACKUP_TYPE="full"
BACKUP_DIR="./backups"
RETENTION_DAYS=30
CLEAN_OLD=false
LIST_BACKUPS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            BACKUP_TYPE="$2"
            shift 2
            ;;
        -d|--dest)
            BACKUP_DIR="$2"
            shift 2
            ;;
        -r|--retention)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        -c|--clean)
            CLEAN_OLD=true
            shift
            ;;
        -l|--list)
            LIST_BACKUPS=true
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

# 检查备份类型是否有效
case $BACKUP_TYPE in
    full|database|logs|config)
        # 类型有效
        ;;
    *)
        log_error "无效的备份类型: $BACKUP_TYPE"
        show_help
        exit 1
        ;;
esac

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 生成时间戳
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="feishu_ai_backup_${BACKUP_TYPE}_${TIMESTAMP}"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

# 主函数
main() {
    log_info "开始飞书AI助手备份 (类型: $BACKUP_TYPE)"
    
    # 列出备份文件
    if [ "$LIST_BACKUPS" = true ]; then
        list_backups
        exit 0
    fi
    
    # 清理过期备份
    if [ "$CLEAN_OLD" = true ]; then
        clean_old_backups
    fi
    
    # 执行备份
    case $BACKUP_TYPE in
        full)
            backup_full
            ;;
        database)
            backup_database
            ;;
        logs)
            backup_logs
            ;;
        config)
            backup_config
            ;;
    esac
    
    # 显示备份信息
    show_backup_info
}

# 完整备份
backup_full() {
    log_info "执行完整备份..."
    
    # 创建备份目录
    mkdir -p "$BACKUP_PATH"
    
    # 备份数据库
    backup_database_to_path "$BACKUP_PATH"
    
    # 备份配置文件
    backup_config_to_path "$BACKUP_PATH"
    
    # 备份日志文件
    backup_logs_to_path "$BACKUP_PATH"
    
    # 备份Docker相关文件
    backup_docker_files "$BACKUP_PATH"
    
    # 创建备份清单
    create_backup_manifest "$BACKUP_PATH"
    
    # 压缩备份文件
    compress_backup "$BACKUP_PATH"
    
    log_success "完整备份完成: $BACKUP_PATH.tar.gz"
}

# 数据库备份
backup_database() {
    log_info "执行数据库备份..."
    
    # 创建备份目录
    mkdir -p "$BACKUP_PATH"
    
    # 备份数据库
    backup_database_to_path "$BACKUP_PATH"
    
    # 压缩备份文件
    compress_backup "$BACKUP_PATH"
    
    log_success "数据库备份完成: $BACKUP_PATH.tar.gz"
}

# 日志备份
backup_logs() {
    log_info "执行日志备份..."
    
    # 创建备份目录
    mkdir -p "$BACKUP_PATH"
    
    # 备份日志文件
    backup_logs_to_path "$BACKUP_PATH"
    
    # 压缩备份文件
    compress_backup "$BACKUP_PATH"
    
    log_success "日志备份完成: $BACKUP_PATH.tar.gz"
}

# 配置备份
backup_config() {
    log_info "执行配置备份..."
    
    # 创建备份目录
    mkdir -p "$BACKUP_PATH"
    
    # 备份配置文件
    backup_config_to_path "$BACKUP_PATH"
    
    # 压缩备份文件
    compress_backup "$BACKUP_PATH"
    
    log_success "配置备份完成: $BACKUP_PATH.tar.gz"
}

# 备份数据库到指定路径
backup_database_to_path() {
    local path=$1
    
    log_info "备份数据库..."
    
    # 检查Docker服务是否运行
    if docker-compose ps | grep -q "db.*Up"; then
        # 使用pg_dump备份PostgreSQL数据库
        docker-compose exec -T db pg_dump -U postgres feishu_ai > "$path/database_backup.sql"
        
        # 备份Redis数据（如果启用）
        if docker-compose ps | grep -q "redis.*Up"; then
            docker-compose exec -T redis redis-cli SAVE
            docker cp $(docker-compose ps -q redis):/data/dump.rdb "$path/redis_dump.rdb"
        fi
        
        log_success "数据库备份完成"
    else
        log_warning "数据库服务未运行，跳过数据库备份"
    fi
}

# 备份配置文件到指定路径
backup_config_to_path() {
    local path=$1
    
    log_info "备份配置文件..."
    
    # 备份环境变量文件
    cp .env* "$path/" 2>/dev/null || true
    
    # 备份Docker配置文件
    cp Dockerfile "$path/" 2>/dev/null || true
    cp docker-compose.yml "$path/" 2>/dev/null || true
    
    # 备份Nginx配置
    mkdir -p "$path/nginx"
    cp -r nginx/* "$path/nginx/" 2>/dev/null || true
    
    # 备份监控配置
    mkdir -p "$path/prometheus" "$path/grafana"
    cp -r prometheus/* "$path/prometheus/" 2>/dev/null || true
    cp -r grafana/* "$path/grafana/" 2>/dev/null || true
    
    # 备份数据库初始化脚本
    mkdir -p "$path/db"
    cp -r db/* "$path/db/" 2>/dev/null || true
    
    # 备份脚本文件
    mkdir -p "$path/scripts"
    cp scripts/*.sh "$path/scripts/" 2>/dev/null || true
    
    log_success "配置文件备份完成"
}

# 备份日志文件到指定路径
backup_logs_to_path() {
    local path=$1
    
    log_info "备份日志文件..."
    
    # 创建日志目录
    mkdir -p "$path/logs"
    
    # 备份应用日志
    if [ -d "logs" ]; then
        cp -r logs/* "$path/logs/" 2>/dev/null || true
    fi
    
    # 备份Docker日志
    docker-compose logs --no-color > "$path/docker_logs.txt" 2>/dev/null || true
    
    log_success "日志文件备份完成"
}

# 备份Docker相关文件
backup_docker_files() {
    local path=$1
    
    log_info "备份Docker相关文件..."
    
    # 保存Docker镜像列表
    docker images > "$path/docker_images.txt" 2>/dev/null || true
    
    # 保存Docker容器列表
    docker ps -a > "$path/docker_containers.txt" 2>/dev/null || true
    
    # 保存Docker卷列表
    docker volume ls > "$path/docker_volumes.txt" 2>/dev/null || true
    
    log_success "Docker文件备份完成"
}

# 创建备份清单
create_backup_manifest() {
    local path=$1
    
    cat > "$path/backup_manifest.txt" << EOF
飞书AI助手备份清单
====================

备份信息:
- 备份类型: $BACKUP_TYPE
- 备份时间: $(date)
- 备份路径: $path
- 系统版本: $(uname -a)

文件清单:
$(find "$path" -type f | sort)

备份大小:
$(du -sh "$path")

数据库信息:
$(docker-compose exec -T db psql -U postgres -d feishu_ai -c "
SELECT 
    table_name,
    pg_size_pretty(pg_total_relation_size('\"' || table_name || '\"')) as total_size,
    pg_size_pretty(pg_relation_size('\"' || table_name || '\"')) as table_size,
    pg_size_pretty(pg_total_relation_size('\"' || table_name || '\"') - pg_relation_size('\"' || table_name || '\"')) as index_size,
    (SELECT COUNT(*) FROM \"' || table_name || '\") as row_count
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY pg_total_relation_size('\"' || table_name || '\"') DESC;
" 2>/dev/null || echo "无法获取数据库信息")

系统状态:
$(docker-compose ps)

EOF
    
    log_success "备份清单创建完成"
}

# 压缩备份文件
compress_backup() {
    local path=$1
    
    log_info "压缩备份文件..."
    
    # 进入备份目录的父目录
    local parent_dir=$(dirname "$path")
    local dir_name=$(basename "$path")
    
    cd "$parent_dir" && tar -czf "$dir_name.tar.gz" "$dir_name" && cd - > /dev/null
    
    # 删除原始目录
    rm -rf "$path"
    
    log_success "备份文件压缩完成: $path.tar.gz"
}

# 清理过期备份
clean_old_backups() {
    log_info "清理 $RETENTION_DAYS 天前的备份文件..."
    
    local deleted_count=0
    local current_time=$(date +%s)
    local retention_seconds=$((RETENTION_DAYS * 24 * 60 * 60))
    
    # 查找并删除过期备份
    for backup_file in "$BACKUP_DIR"/*.tar.gz; do
        if [ -f "$backup_file" ]; then
            local file_time=$(stat -f "%m" "$backup_file" 2>/dev/null || stat -c "%Y" "$backup_file")
            local age=$((current_time - file_time))
            
            if [ $age -gt $retention_seconds ]; then
                log_info "删除过期备份: $(basename "$backup_file")"
                rm -f "$backup_file"
                deleted_count=$((deleted_count + 1))
            fi
        fi
    done
    
    if [ $deleted_count -gt 0 ]; then
        log_success "已删除 $deleted_count 个过期备份文件"
    else
        log_info "没有找到过期备份文件"
    fi
}

# 列出备份文件
list_backups() {
    log_info "备份文件列表:"
    echo ""
    
    if [ -d "$BACKUP_DIR" ]; then
        local total_size=0
        local file_count=0
        
        echo "文件名                            大小        修改时间"
        echo "------------------------------------------------------------"
        
        for backup_file in "$BACKUP_DIR"/*.tar.gz; do
            if [ -f "$backup_file" ]; then
                local file_size=$(du -h "$backup_file" | cut -f1)
                local file_time=$(stat -f "%Sm" "$backup_file" 2>/dev/null || stat -c "%y" "$backup_file" | cut -d'.' -f1)
                local file_name=$(basename "$backup_file")
                
                printf "%-35s %-10s %s\n" "$file_name" "$file_size" "$file_time"
                
                total_size=$((total_size + $(du -k "$backup_file" | cut -f1)))
                file_count=$((file_count + 1))
            fi
        done
        
        echo "------------------------------------------------------------"
        echo "总计: $file_count 个备份文件, $(numfmt --to=iec --suffix=B $((total_size * 1024)))"
        
        # 显示磁盘使用情况
        echo ""
        log_info "磁盘使用情况:"
        df -h "$BACKUP_DIR" | tail -1
    else
        log_warning "备份目录不存在: $BACKUP_DIR"
    fi
}

# 显示备份信息
show_backup_info() {
    echo ""
    log_success "备份完成！"
    echo ""
    echo "备份信息:"
    echo "  备份类型: $BACKUP_TYPE"
    echo "  备份文件: $BACKUP_PATH.tar.gz"
    echo "  备份时间: $(date)"
    echo "  文件大小: $(du -h "$BACKUP_PATH.tar.gz" | cut -f1)"
    echo ""
    echo "恢复命令:"
    echo "  tar -xzf $BACKUP_PATH.tar.gz -C /tmp/"
    echo "  # 然后根据需要恢复文件"
    echo ""
    echo "管理命令:"
    echo "  列出备份: $0 --list"
    echo "  清理备份: $0 --clean --retention $RETENTION_DAYS"
}

# 运行主函数
main "$@"