# 船期数据抓取服务

## 项目简介
这是一个用于抓取和管理船期数据的Python服务。支持多港口组合查询，数据过滤，以及MySQL数据存储功能。

## 主要功能
1. 数据获取
   - 支持从API获取船舶航线数据
   - 支持批量获取多个港口组合的数据
   - 内置请求重试机制（最多重试3次）

2. 数据过滤
   - 支持按起运港代码和名称过滤
   - 支持按目的港代码和名称过滤
   - 智能选择最优航线（基于isReferenceCarrier和shareCabins规则）

3. 数据存储
   - 自动创建和管理MySQL数据库表
   - 支持数据版本控制
   - 自动处理重复数据

## 环境要求
- Python 3.x
- MySQL 5.7+
- 必要的Python包：
  ```
  pymysql
  requests
  ```

## 配置说明
在`config.json`中配置以下参数：
```json
{
  "token": "您的API token",
  "company_id": "公司ID",
  "days_back": 2,
  "pol_cd": "起运港代码",
  "pod_cd": "目的港代码",
  "weeks_out": "6",
  "is_transit": "0",
  "db_host": "localhost",
  "db_port": 3306,
  "db_user": "root",
  "db_password": "您的密码",
  "db_name": "shipping_project",
  "db_charset": "utf8mb4"
}
```

## 使用方法

### 1. 基本使用（单一港口组合）
```bash
python process_routes.py
```

### 2. 使用API获取多个港口组合数据
```bash
# 获取所有可用港口组合的数据
python process_routes.py --use_port_api

# 使用过滤条件
python process_routes.py --use_port_api --pol_filter_code CNSHK --pod_filter_name "新加坡"
```

### 3. 测试模式
```bash
# 使用测试数据
python process_routes.py --use_test_data

# 跳过数据库存储
python process_routes.py --skip_db
```

## 数据库表结构
主表：`vessel_schedule`
- `id`: 自增主键
- `routeCd`: 航线服务名称
- `vessel`: 船名
- `voyage`: 航次
- `polCd`: 起运港五字码
- `podCd`: 目的港五字码
- `eta`: 预计到港时间
- `etd`: 预计离港时间
- `isReferenceCarrier`: 是否主船东
- `data_version`: 数据版本号

## 常用查询示例
```sql
-- 查看最新数据
SELECT * FROM vessel_schedule 
WHERE data_version = (SELECT MAX(data_version) FROM vessel_schedule);

-- 查看特定航线
SELECT * FROM vessel_schedule 
WHERE polCd='CNSHK' AND podCd='THBKK' 
ORDER BY etd DESC;

-- 统计数据量
SELECT COUNT(*) as total, data_version 
FROM vessel_schedule 
GROUP BY data_version 
ORDER BY data_version DESC;
```

## 测试
项目包含两个测试文件：
1. `test_port_api_flow.py`: 测试API数据流程
2. `test_db_insert.py`: 测试数据库插入功能

运行测试：
```bash
python test_port_api_flow.py
python test_db_insert.py
```

## 错误处理
- API请求失败时会自动重试（最多3次）
- 数据库操作错误会记录详细日志
- 配置文件缺失时使用默认配置

## 注意事项
1. 首次运行前请确保配置文件中的数据库信息正确
2. 批量查询时建议设置合适的查询范围，避免请求次数过多
3. 建议定期清理历史版本数据，避免数据库空间占用过大

## 开发计划
- [ ] 添加更多数据源支持
- [ ] 优化数据处理逻辑
- [ ] 添加Web界面
- [ ] 支持更多数据库类型
- [ ] 添加数据导出功能

## 作者
hwpchn

## 许可证
MIT License
