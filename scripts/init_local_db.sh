#!/bin/bash
# 本地数据库初始化脚本

echo "=== 初始化本地数据库 ==="

# 检查PostgreSQL是否运行
if ! brew services list | grep postgresql | grep -q "started"; then
    echo "启动PostgreSQL..."
    brew services start postgresql@15
    sleep 5
fi

# 创建数据库
echo "创建数据库 feishu_db..."
createdb feishu_db 2>/dev/null || echo "数据库已存在或创建失败"

# 执行初始化SQL
echo "执行表结构初始化..."
psql -d feishu_db -f db/init.sql 2>/dev/null || echo "SQL执行失败或文件不存在"

# 检查数据库状态
echo "数据库状态检查..."
psql -d feishu_db -c "\dt" 2>/dev/null || echo "无法连接到数据库"

echo "=== 数据库初始化完成 ==="