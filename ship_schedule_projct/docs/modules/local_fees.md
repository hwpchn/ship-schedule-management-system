# 本地费用模块文档

## 📋 概述

本地费用模块提供完整的本地费用管理功能，支持多种计费方式、多货币支持和前台查询服务。采用简化设计，专注于核心业务需求。

**模块路径**: `local_fees/`

## 🏗️ 模块架构

### 核心组件
```
local_fees/
├── models.py           # 数据模型定义
├── views.py           # API视图实现
├── serializers.py     # 数据序列化器
├── urls.py           # URL路由配置
├── admin.py          # 管理后台配置
├── permissions.py    # 权限控制逻辑
├── migrations/       # 数据库迁移文件
└── tests.py         # 测试用例
```

### 设计原则
- **简化设计**: 删除复杂功能，专注核心需求
- **唯一性约束**: 确保数据一致性
- **灵活计费**: 支持多种计费方式
- **前端友好**: 查询API返回前端需要的格式

## 📊 数据模型

### LocalFee模型 (本地费用)
```python
class LocalFee(models.Model):
    id = models.AutoField(primary_key=True)
    
    # 核心字段
    polCd = models.CharField(max_length=10)          # 起运港五字码
    podCd = models.CharField(max_length=10)          # 目的港五字码
    carriercd = models.CharField(max_length=20)      # 船公司英文名
    name = models.CharField(max_length=100)          # 费用类型名称
    unit_name = models.CharField(max_length=50)      # 单位名称
    
    # 价格字段
    price_20gp = models.DecimalField(max_digits=10, decimal_places=2)    # 20GP价格
    price_40gp = models.DecimalField(max_digits=10, decimal_places=2)    # 40GP价格
    price_40hq = models.DecimalField(max_digits=10, decimal_places=2)    # 40HQ价格
    price_per_bill = models.DecimalField(max_digits=10, decimal_places=2) # 每票价格
    
    currency = models.CharField(max_length=20)       # 货币
    
    # 时间字段
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 唯一性约束
```python
unique_together = ['carriercd', 'polCd', 'podCd', 'name']
```

#### 字段说明
| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| polCd | CharField | 起运港五字码 | CNSHK |
| podCd | CharField | 目的港五字码 | INMAA |
| carriercd | CharField | 船公司英文名 | IAL, MSK |
| name | CharField | 费用类型名称 | 起运港码头费, 保安费 |
| unit_name | CharField | 单位名称 | 箱型, 票 |
| price_20gp | DecimalField | 20尺普通箱价格 | 760.00 |
| price_40gp | DecimalField | 40尺普通箱价格 | 1287.00 |
| price_40hq | DecimalField | 40尺高箱价格 | 1287.00 |
| price_per_bill | DecimalField | 每票价格 | 50.00 |
| currency | CharField | 货币代码 | CNY, USD, EUR |

## 💰 计费方式

### 1. 按箱型计费
适用于大部分港口费用，根据集装箱类型收费：
```python
# 示例：起运港码头费
{
    "name": "起运港码头费",
    "unit_name": "箱型",
    "price_20gp": "760.00",
    "price_40gp": "1287.00", 
    "price_40hq": "1287.00",
    "price_per_bill": null,
    "currency": "CNY"
}
```

### 2. 按票计费
适用于文件费、保安费等固定费用：
```python
# 示例：保安费
{
    "name": "保安费",
    "unit_name": "票",
    "price_20gp": null,
    "price_40gp": null,
    "price_40hq": null,
    "price_per_bill": "50.00",
    "currency": "USD"
}
```

### 3. 混合计费
支持同时设置箱型价格和票价，灵活应对不同需求。

## 🌐 多货币支持

### 支持的货币
- **CNY** - 人民币
- **USD** - 美元
- **EUR** - 欧元
- **INR** - 印度卢比
- **THB** - 泰铢
- **SGD** - 新加坡元

### 货币处理
```python
# 货币验证
SUPPORTED_CURRENCIES = ['CNY', 'USD', 'EUR', 'INR', 'THB', 'SGD']

def validate_currency(currency):
    if currency not in SUPPORTED_CURRENCIES:
        raise ValidationError(f'不支持的货币: {currency}')
```

## 🔧 核心功能

### 1. 费用管理
```python
class LocalFeeViewSet(viewsets.ModelViewSet):
    """本地费用CRUD操作"""
    
    def list(self, request):
        """获取费用列表，支持过滤"""
        
    def create(self, request):
        """创建新费用记录"""
        
    def retrieve(self, request, pk):
        """获取费用详情"""
        
    def update(self, request, pk):
        """更新费用信息"""
        
    def destroy(self, request, pk):
        """删除费用记录"""
```

### 2. 前台查询
```python
@action(detail=False, methods=['get'], url_path='query')
def query_fees(self, request):
    """前台费用查询API"""
    # 1. 获取查询参数
    polCd = request.query_params.get('polCd')
    podCd = request.query_params.get('podCd')
    carriercd = request.query_params.get('carriercd')
    
    # 2. 构建查询条件
    queryset = LocalFee.objects.filter(polCd=polCd, podCd=podCd)
    if carriercd:
        queryset = queryset.filter(carriercd=carriercd)
    
    # 3. 排序和序列化
    queryset = queryset.order_by('id')
    serializer = LocalFeeQuerySerializer(queryset, many=True)
    
    # 4. 返回前端格式
    return Response({
        'status': 'success',
        'data': serializer.data
    })
```

### 3. 数据验证
```python
def validate(self, data):
    """数据验证逻辑"""
    # 1. 价格不能为负数
    price_fields = ['price_20gp', 'price_40gp', 'price_40hq', 'price_per_bill']
    for field in price_fields:
        if data.get(field) is not None and data[field] < 0:
            raise serializers.ValidationError(f"{field}不能为负数")
    
    # 2. 至少设置一种价格
    has_container_price = any(data.get(f) for f in ['price_20gp', 'price_40gp', 'price_40hq'])
    has_bill_price = data.get('price_per_bill') is not None
    
    if not has_container_price and not has_bill_price:
        raise serializers.ValidationError("至少需要设置一种价格")
    
    return data
```

## 📡 API接口

### CRUD接口
| 端点 | 方法 | 功能 | 权限 |
|------|------|------|------|
| `/local-fees/` | GET | 费用列表 | local_fee.list |
| `/local-fees/` | POST | 创建费用 | local_fee.create |
| `/local-fees/{id}/` | GET | 费用详情 | local_fee.detail |
| `/local-fees/{id}/` | PUT | 更新费用 | local_fee.update |
| `/local-fees/{id}/` | DELETE | 删除费用 | local_fee.delete |

### 查询接口
| 端点 | 方法 | 功能 | 权限 |
|------|------|------|------|
| `/local-fees/query/` | GET | 前台费用查询 | local_fee.query |

## 🎯 业务逻辑

### 费用查询流程
```
前台请求 → 参数验证 → 数据库查询 → 格式转换 → 返回结果
```

### 数据处理逻辑
```python
def process_fee_data(fees):
    """处理费用数据"""
    processed_data = []
    
    for fee in fees:
        # 转换为前端格式
        fee_data = {
            'id': fee.id,
            '名称': fee.name,
            '单位': fee.unit_name or '箱型',
            '20GP': str(fee.price_20gp) if fee.price_20gp else None,
            '40GP': str(fee.price_40gp) if fee.price_40gp else None,
            '40HQ': str(fee.price_40hq) if fee.price_40hq else None,
            '单票价格': str(fee.price_per_bill) if fee.price_per_bill else None,
            '币种': fee.currency
        }
        processed_data.append(fee_data)
    
    return processed_data
```

### 权限控制
```python
def get_permissions(self):
    """根据操作类型设置权限"""
    permission_map = get_permission_map()
    
    if self.action == 'list':
        return [HasPermission(permission_map.get('local_fee_list', 'local_fee.list'))]
    elif self.action == 'create':
        return [HasPermission(permission_map.get('local_fee_create', 'local_fee.create'))]
    elif self.action == 'query_fees':
        return [HasPermission(permission_map.get('local_fee_query', 'local_fee.query'))]
    # ... 其他权限
```

## 🧪 测试覆盖

### 单元测试
```python
class LocalFeeModelTest(TestCase):
    """LocalFee模型测试"""
    
    def test_create_local_fee(self):
        """测试创建本地费用"""
        
    def test_unique_constraint(self):
        """测试唯一性约束"""
        
    def test_price_validation(self):
        """测试价格验证"""
```

### API测试
```python
class LocalFeeAPITest(TestCase):
    """LocalFee API测试"""
    
    def test_create_fee(self):
        """测试创建费用API"""
        
    def test_query_fees(self):
        """测试查询费用API"""
        
    def test_permission_control(self):
        """测试权限控制"""
```

## 📊 预置测试数据

### 测试路线
**起运港**: CNSHK (上海)  
**目的港**: INMAA (马德拉斯)  
**船公司**: IAL

### 测试费用
```python
test_fees = [
    {
        "name": "起运港码头费",
        "unit_name": "箱型",
        "price_20gp": "760.00",
        "price_40gp": "1287.00",
        "price_40hq": "1287.00",
        "currency": "CNY"
    },
    {
        "name": "保安费",
        "unit_name": "票",
        "price_per_bill": "50.00",
        "currency": "USD"
    },
    {
        "name": "文件费",
        "unit_name": "票",
        "price_per_bill": "25.00",
        "currency": "USD"
    },
    {
        "name": "目的港码头费",
        "unit_name": "箱型",
        "price_20gp": "850.00",
        "price_40gp": "1400.00",
        "price_40hq": "1400.00",
        "currency": "INR"
    },
    {
        "name": "燃油附加费",
        "unit_name": "箱型",
        "price_20gp": "120.00",
        "price_40gp": "240.00",
        "price_40hq": "240.00",
        "currency": "USD"
    }
]
```

## 📝 使用示例

### 创建费用记录
```python
# 创建按箱型计费的费用
container_fee = LocalFee.objects.create(
    polCd='CNSHK',
    podCd='INMAA',
    carriercd='IAL',
    name='起运港码头费',
    unit_name='箱型',
    price_20gp=Decimal('760.00'),
    price_40gp=Decimal('1287.00'),
    price_40hq=Decimal('1287.00'),
    currency='CNY'
)

# 创建按票计费的费用
bill_fee = LocalFee.objects.create(
    polCd='CNSHK',
    podCd='INMAA',
    carriercd='IAL',
    name='保安费',
    unit_name='票',
    price_per_bill=Decimal('50.00'),
    currency='USD'
)
```

### 前台查询使用
```python
# 查询特定路线的费用
fees = LocalFee.objects.filter(
    polCd='CNSHK',
    podCd='INMAA',
    carriercd='IAL'
).order_by('id')

# 转换为前端格式
serializer = LocalFeeQuerySerializer(fees, many=True)
response_data = {
    'status': 'success',
    'data': serializer.data
}
```

### API调用示例
```bash
# 创建费用
curl -X POST http://127.0.0.1:8000/api/local-fees/local-fees/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "polCd": "CNSHK",
    "podCd": "INMAA",
    "carriercd": "IAL",
    "name": "起运港码头费",
    "unit_name": "箱型",
    "price_20gp": "760.00",
    "currency": "CNY"
  }'

# 查询费用
curl -X GET "http://127.0.0.1:8000/api/local-fees/local-fees/query/?polCd=CNSHK&podCd=INMAA&carriercd=IAL" \
  -H "Authorization: Bearer <token>"
```

## ⚠️ 注意事项

1. **唯一性约束**: 同一船公司、起运港、目的港和费用类型的组合必须唯一
2. **价格验证**: 价格不能为负数，至少需要设置一种价格
3. **计费方式**: 明确区分按箱型计费和按票计费
4. **货币一致性**: 同一费用记录只能使用一种货币
5. **前台格式**: 查询API返回中文字段名，便于前台使用
6. **权限控制**: 不同操作需要相应权限，确保数据安全
7. **数据完整性**: 删除操作需要考虑数据关联性
