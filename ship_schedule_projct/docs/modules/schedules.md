# 船期管理模块文档

## 📋 概述

船期管理模块是系统的核心业务模块，负责船舶航线信息管理、船舶额外信息管理、共舱分组查询等功能。提供完整的船期数据管理和前台查询服务。

**模块路径**: `schedules/`

## 🏗️ 模块架构

### 核心组件
```
schedules/
├── models.py           # 数据模型定义
├── views.py           # API视图实现
├── serializers.py     # 数据序列化器
├── urls.py           # URL路由配置
├── admin.py          # 管理后台配置
├── signals.py        # 信号处理器
├── migrations/       # 数据库迁移文件
└── management/       # 管理命令
```

### 设计模式
- **领域驱动设计**: 按业务领域组织代码
- **数据同步模式**: 自动同步相关数据
- **版本控制模式**: 支持数据版本管理
- **分组聚合模式**: 共舱分组算法

## 📊 数据模型

### 1. VesselSchedule模型 (船舶航线)
```python
class VesselSchedule(models.Model):
    # 主键和核心字段
    id = models.AutoField(primary_key=True)
    polCd = models.CharField(max_length=10)      # 起运港五字码
    podCd = models.CharField(max_length=10)      # 目的港五字码
    vessel = models.CharField(max_length=100)    # 船名
    voyage = models.CharField(max_length=50)     # 航次
    data_version = models.IntegerField()         # 数据版本号
    
    # 时间和状态字段
    fetch_timestamp = models.BigIntegerField()   # 数据抓取时间戳
    fetch_date = models.DateTimeField()          # 格式化日期时间
    status = models.SmallIntegerField(default=1) # 数据状态
    
    # 航线基本信息
    routeCd = models.CharField(max_length=50)    # 航线服务名称
    routeEtd = models.CharField(max_length=20)   # 计划离港班期
    carriercd = models.CharField(max_length=20)  # 船公司英文名
    pol = models.CharField(max_length=100)       # 起运港中文名
    pod = models.CharField(max_length=100)       # 目的港中文名
    
    # 航运时间相关
    eta = models.CharField(max_length=30)        # 计划到港日期
    etd = models.CharField(max_length=30)        # 计划离港日期
    totalDuration = models.CharField(max_length=10) # 预计航程
    
    # 共舱信息
    shareCabins = models.TextField()             # 共舱结果集(JSON)
```

#### 唯一性约束
```python
unique_together = ('polCd', 'podCd', 'vessel', 'voyage', 'data_version')
```

#### 核心方法
- `get_share_cabins()` - 获取解析后的共舱信息
- `get_group_key()` - 获取分组键
- `is_latest_version()` - 检查是否最新版本

### 2. VesselInfoFromCompany模型 (船舶额外信息)
```python
class VesselInfoFromCompany(models.Model):
    # 关联字段（与VesselSchedule关联）
    carriercd = models.CharField(max_length=10)  # 船公司
    polCd = models.CharField(max_length=10)      # 起运港五字码
    podCd = models.CharField(max_length=10)      # 目的港五字码
    vessel = models.CharField(max_length=100)    # 船名
    voyage = models.CharField(max_length=50)     # 航次
    
    # 补充信息字段
    gp_20 = models.CharField(max_length=50)      # 20尺普通箱
    hq_40 = models.CharField(max_length=50)      # 40尺高箱
    cut_off_time = models.CharField(max_length=50) # 截关时间
    price = models.DecimalField(max_digits=10, decimal_places=2) # 价格
```

#### 唯一性约束
```python
unique_together = ('carriercd', 'polCd', 'podCd', 'vessel', 'voyage')
```

#### 关联关系
通过五个字段与VesselSchedule建立关联：
- carriercd ↔ carriercd
- polCd ↔ polCd  
- podCd ↔ podCd
- vessel ↔ vessel
- voyage ↔ voyage

## 🔄 数据同步机制

### 自动同步流程
```python
# 信号处理器
@receiver(post_save, sender=VesselSchedule)
def sync_vessel_info(sender, instance, created, **kwargs):
    """VesselSchedule保存后自动同步到VesselInfoFromCompany"""
    if created:
        VesselInfoFromCompany.objects.get_or_create(
            carriercd=instance.carriercd,
            polCd=instance.polCd,
            podCd=instance.podCd,
            vessel=instance.vessel,
            voyage=instance.voyage
        )
```

### 版本控制
- **数据版本**: 通过data_version字段管理数据版本
- **最新数据**: 查询时默认返回最新版本数据
- **历史数据**: 保留历史版本用于数据追溯
- **版本清理**: 定期清理过期版本数据

## 🔍 共舱分组算法

### 分组逻辑
```python
def group_schedules_by_cabin(schedules):
    """根据共舱信息对航线进行分组"""
    groups = defaultdict(list)
    
    for schedule in schedules:
        # 解析共舱信息
        share_cabins = json.loads(schedule.shareCabins or '[]')
        
        # 生成分组键
        cabin_carriers = sorted([cabin.get('carrierCd', '') for cabin in share_cabins])
        group_key = '_'.join(cabin_carriers) if cabin_carriers else schedule.carriercd
        
        # 添加到对应分组
        groups[group_key].append(schedule)
    
    return groups
```

### 分组规则
1. **共舱配置相同**: 具有相同shareCabins配置的航线分为一组
2. **船公司排序**: 按船公司代码排序生成分组键
3. **单独航线**: 无共舱配置的航线单独成组
4. **分组命名**: 使用group_1, group_2等命名

### 分组信息计算
```python
def calculate_group_info(group_schedules):
    """计算分组统计信息"""
    return {
        'cabins_count': len(group_schedules),
        'carrier_codes': list(set(s.carriercd for s in group_schedules)),
        'plan_open': calculate_plan_open(group_schedules),
        'plan_duration': calculate_plan_duration(group_schedules),
        'cabin_price': calculate_cabin_price(group_schedules),
        'is_has_gp_20': calculate_container_availability(group_schedules, 'gp_20'),
        'is_has_hq_40': calculate_container_availability(group_schedules, 'hq_40')
    }
```

## 🔧 核心功能

### 1. 船舶航线管理
```python
class VesselScheduleViewSet:
    """船舶航线CRUD操作"""
    
    def list(self, request):
        """获取航线列表，支持过滤和分页"""
        
    def create(self, request):
        """创建新航线，自动同步到VesselInfo"""
        
    def retrieve(self, request, pk):
        """获取航线详情"""
        
    def update(self, request, pk):
        """更新航线信息"""
        
    def destroy(self, request, pk):
        """删除航线（软删除）"""
```

### 2. 船舶额外信息管理
```python
class VesselInfoViewSet:
    """船舶额外信息CRUD操作"""
    
    def bulk_create(self, request):
        """批量创建船舶信息"""
        
    def bulk_update(self, request):
        """批量更新船舶信息"""
        
    def bulk_delete(self, request):
        """批量删除船舶信息"""
        
    def query(self, request):
        """根据关联字段查询特定船舶信息"""
```

### 3. 前台查询API
```python
def cabin_grouping_with_vessel_info_api(request):
    """共舱分组查询（含额外信息）"""
    # 1. 获取查询参数
    # 2. 查询最新版本航线数据
    # 3. 执行共舱分组算法
    # 4. 关联船舶额外信息
    # 5. 计算分组统计信息
    # 6. 返回结构化数据
```

### 4. 共舱配置管理
```python
def cabin_config_management():
    """共舱配置管理功能"""
    # 1. 配置详情查询
    # 2. 配置更新操作
    # 3. 配置删除操作
    # 4. 批量配置更新
```

## 📡 API接口

### 船舶航线接口
| 端点 | 方法 | 功能 | 权限 |
|------|------|------|------|
| `/schedules/` | GET | 航线列表 | vessel_schedule.list |
| `/schedules/` | POST | 创建航线 | vessel_schedule.create |
| `/schedules/{id}/` | GET | 航线详情 | vessel_schedule.detail |
| `/schedules/{id}/` | PUT | 更新航线 | vessel_schedule.update |
| `/schedules/{id}/` | DELETE | 删除航线 | vessel_schedule.delete |

### 船舶信息接口
| 端点 | 方法 | 功能 | 权限 |
|------|------|------|------|
| `/vessel-info/` | GET | 信息列表 | vessel_info.list |
| `/vessel-info/` | POST | 创建信息 | vessel_info.create |
| `/vessel-info/bulk-create/` | POST | 批量创建 | vessel_info.create |
| `/vessel-info/bulk-update/` | PATCH | 批量更新 | vessel_info.update |
| `/vessel-info/bulk-delete/` | DELETE | 批量删除 | vessel_info.delete |

### 前台查询接口
| 端点 | 方法 | 功能 | 权限 |
|------|------|------|------|
| `/schedules/cabin-grouping-with-info/` | GET | 共舱分组查询 | vessel_schedule_list |
| `/schedules/cabin-grouping/` | GET | 基础共舱分组 | vessel_schedule.list |
| `/vessel-info/query/` | GET | 船舶信息查询 | vessel_info.list |

## 🎯 业务逻辑

### 数据处理流程
```
数据导入 → 版本控制 → 自动同步 → 分组计算 → 前台展示
```

### 查询优化
```python
# 查询优化策略
def optimized_query():
    # 1. 只查询最新版本数据
    latest_version = VesselSchedule.objects.aggregate(
        Max('data_version')
    )['data_version__max']
    
    # 2. 使用索引字段过滤
    schedules = VesselSchedule.objects.filter(
        data_version=latest_version,
        status=1,
        polCd=polCd,
        podCd=podCd
    ).select_related().prefetch_related()
    
    # 3. 批量关联查询
    vessel_infos = VesselInfoFromCompany.objects.filter(
        polCd=polCd,
        podCd=podCd
    ).in_bulk(fieldname='vessel_voyage_key')
```

### 缓存策略
```python
# 缓存热点数据
@cache_result(timeout=300)  # 5分钟缓存
def get_cabin_grouping_data(polCd, podCd):
    """缓存共舱分组数据"""
    # 执行分组查询逻辑
    pass
```

## 🧪 测试覆盖

### 单元测试
- 模型字段验证测试
- 数据同步机制测试
- 分组算法测试
- 业务逻辑测试

### 集成测试
- API接口测试
- 数据库操作测试
- 权限控制测试
- 批量操作测试

### 性能测试
- 大数据量查询测试
- 分组算法性能测试
- 并发访问测试
- 缓存效果测试

## 📊 性能优化

### 数据库优化
```python
# 数据库索引
class Meta:
    indexes = [
        models.Index(fields=['polCd', 'podCd', 'data_version']),
        models.Index(fields=['carriercd', 'vessel', 'voyage']),
        models.Index(fields=['fetch_date', 'status']),
    ]
```

### 查询优化
- 使用select_related减少数据库查询
- 使用prefetch_related优化关联查询
- 合理使用数据库索引
- 分页查询避免大数据量加载

### 缓存优化
- Redis缓存热点数据
- 查询结果缓存
- 分组计算结果缓存
- 版本化缓存策略

## 📝 使用示例

### 创建航线数据
```python
# 创建船舶航线
schedule_data = {
    'polCd': 'CNSHA',
    'podCd': 'USNYC',
    'vessel': 'MSC OSCAR',
    'voyage': '251W',
    'data_version': 20250527,
    'carriercd': 'MSK',
    'shareCabins': json.dumps([
        {'carrierCd': 'MSK'},
        {'carrierCd': 'ONE'}
    ])
}
schedule = VesselSchedule.objects.create(**schedule_data)

# 自动创建对应的船舶额外信息
vessel_info = VesselInfoFromCompany.objects.get(
    carriercd='MSK',
    polCd='CNSHA',
    podCd='USNYC',
    vessel='MSC OSCAR',
    voyage='251W'
)
```

### 前台查询使用
```python
# 前台共舱分组查询
response = requests.get(
    '/api/schedules/cabin-grouping-with-info/',
    params={'polCd': 'CNSHA', 'podCd': 'USNYC'},
    headers={'Authorization': f'Bearer {token}'}
)

# 处理分组数据
groups = response.json()['data']['groups']
for group in groups:
    print(f"分组: {group['group_id']}")
    print(f"共舱数量: {group['cabins_count']}")
    print(f"船公司: {group['carrier_codes']}")
    print(f"价格: {group['cabin_price']}")
```

## ⚠️ 注意事项

1. **数据版本**: 确保查询最新版本数据，避免显示过期信息
2. **数据同步**: VesselSchedule和VesselInfoFromCompany需要保持同步
3. **分组算法**: 共舱分组基于shareCabins字段，确保数据格式正确
4. **性能考虑**: 大数据量查询时注意分页和缓存
5. **权限控制**: 不同操作需要相应权限，确保数据安全
6. **数据完整性**: 批量操作时注意事务处理和错误回滚
