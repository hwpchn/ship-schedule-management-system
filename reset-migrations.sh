#!/bin/bash

# 重置Django迁移脚本

echo "🔄 重置Django迁移文件..."

cd ship_schedule_projct

# 备份性能索引迁移文件
cp authentication/migrations/0007_add_performance_indexes.py authentication/migrations/0007_add_performance_indexes.py.bak
cp local_fees/migrations/0007_add_performance_indexes.py local_fees/migrations/0007_add_performance_indexes.py.bak  
cp schedules/migrations/0006_add_performance_indexes.py schedules/migrations/0006_add_performance_indexes.py.bak

# 删除性能索引迁移文件（避免冲突）
rm -f authentication/migrations/0007_add_performance_indexes.py
rm -f local_fees/migrations/0007_add_performance_indexes.py
rm -f schedules/migrations/0006_add_performance_indexes.py

echo "✅ 迁移重置完成"
echo "📝 已备份性能索引迁移文件到 .bak"