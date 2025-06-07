# Docker环境下的爬虫使用指南

## 🐳 数据库连接配置变更

### Docker环境下的数据库配置
- **数据库名**: `huan_hai` (从 `shipping_project` 变更)
- **端口映射**: `3307:3306` (避免与本地MySQL冲突)
- **主机地址**: `localhost:3307` (外部访问)

## 📋 配置文件说明

### 1. config.json (本地环境)
```json
{
  "db_host": "localhost",
  "db_port": 3306,
  "db_name": "shipping_project"
}
```

### 2. config.docker.json (Docker外部访问)
```json
{
  "db_host": "localhost", 
  "db_port": 3307,
  "db_name": "huan_hai"
}
```

### 3. config.container.json (容器内部)
```json
{
  "db_host": "db",
  "db_port": 3306, 
  "db_name": "huan_hai"
}
```

## 🚀 使用方法

### 方法一：指定环境 (推荐)
```bash
# Docker环境 (从外部连接Docker容器数据库)
python process_routes.py --env docker

# 容器内部环境 (如果爬虫也在容器中)
python process_routes.py --env container

# 本地环境
python process_routes.py --env local
```

### 方法二：指定配置文件
```bash
# 使用Docker配置
python process_routes.py --config_file config.docker.json

# 使用容器配置
python process_routes.py --config_file config.container.json
```

### 方法三：批量获取多港口数据
```bash
# Docker环境下获取所有港口组合数据
python process_routes.py --env docker --use_port_api

# 带过滤条件
python process_routes.py --env docker --use_port_api --pol_filter_code CNSHK
```

## 🔍 验证连接

### 1. 检查Docker容器状态
```bash
docker-compose ps
```

### 2. 检查MySQL连接
```bash
# 进入MySQL容器
docker exec -it ship_schedule_db mysql -u root -p099118

# 检查数据库
SHOW DATABASES;
USE huan_hai;
SHOW TABLES;
```

### 3. 测试爬虫连接
```bash
# 测试连接但不存储数据
python process_routes.py --env docker --skip_db

# 使用测试数据验证
python process_routes.py --env docker --use_test_data
```

## 📊 数据验证

### 检查数据是否正确存储
```sql
-- 连接到Docker数据库
mysql -h localhost -P 3307 -u root -p099118

-- 检查数据
USE huan_hai;
SELECT COUNT(*) FROM vessel_schedule;
SELECT * FROM vessel_schedule ORDER BY fetch_date DESC LIMIT 5;
```

### Django ORM验证
```python
# 在Django shell中验证
python manage.py shell

from schedules.models import VesselSchedule
print(f"总记录数: {VesselSchedule.objects.count()}")
print(f"最新版本: {VesselSchedule.objects.aggregate(max_version=models.Max('data_version'))}")
```

## ⚠️ 注意事项

1. **端口冲突**: Docker容器映射到3307端口，避免与本地MySQL(3306)冲突
2. **数据库名变更**: 从`shipping_project`变更为`huan_hai`
3. **网络连接**: 确保Docker容器启动后再运行爬虫
4. **权限问题**: 确保MySQL用户有足够权限创建表和插入数据

## 🛠️ 故障排除

### 1. 连接失败
```bash
# 检查容器状态
docker-compose ps

# 重启数据库容器
docker-compose restart db

# 查看容器日志
docker-compose logs db
```

### 2. 权限问题
```sql
-- 进入MySQL容器授权
docker exec -it ship_schedule_db mysql -u root -p099118
GRANT ALL PRIVILEGES ON huan_hai.* TO 'root'@'%';
FLUSH PRIVILEGES;
```

### 3. 表不存在
爬虫会自动创建`vessel_schedule`表，如果失败：
```bash
# 手动运行Django迁移
docker-compose exec web python manage.py migrate
```

## 📈 性能优化

### 大批量数据处理
```bash
# 批量处理多个港口组合
python process_routes.py --env docker --use_port_api

# 分批处理避免超时
python process_routes.py --env docker --pol_filter_code CNSHK --pod_filter_code THBKK
```

## 🔄 自动化部署

### 创建定时任务
```bash
# 添加到crontab
# 每天凌晨2点运行
0 2 * * * cd /path/to/get_schedule_data && python process_routes.py --env docker --use_port_api
```

---

**快速开始**: `python process_routes.py --env docker --use_port_api`