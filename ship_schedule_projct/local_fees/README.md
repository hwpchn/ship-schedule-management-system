# 本地费用管理模块

## 概述

本模块提供了简化的本地费用管理功能，支持基本的增删查改操作。根据您的需求重新设计，删除了复杂的旧接口，实现了简洁高效的API。

## 模型设计

### LocalFee 模型

```python
class LocalFee(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    
    # 核心字段
    polCd = models.CharField(max_length=10, verbose_name="起运港五字码")
    podCd = models.CharField(max_length=10, verbose_name="目的港五字码")
    carriercd = models.CharField(max_length=20, blank=True, null=True, verbose_name="船公司英文名")
    name = models.CharField(max_length=100, verbose_name="费用类型名称")  # 起运港吊头费、保安费等
    unit_name = models.CharField(max_length=50, default="箱型", verbose_name="单位名称")  # 箱型、票等
    
    # 价格字段
    price_20gp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="20GP价格")
    price_40gp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="40GP价格") 
    price_40hq = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="40HQ价格")
    price_per_bill = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="每票价格")
    
    currency = models.CharField(max_length=20, blank=True, null=True, verbose_name="货币")
    
    # 时间字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'local_fee'
        verbose_name = "本地费用"
        verbose_name_plural = "本地费用"
        # 唯一性约束
        unique_together = ['carriercd', 'polCd', 'podCd', 'name']
```

### 唯一性约束

模型使用 `unique_together = ['carriercd', 'polCd', 'podCd', 'name']` 确保同一船公司、起运港、目的港和费用类型的组合是唯一的。

## API 接口

### 基础URL
所有API的基础URL为：`/api/local-fees/`

### 认证
所有API都需要用户认证，请在请求头中包含：
```
Authorization: Bearer <your_token>
```

### 权限系统

本模块使用细粒度的权限控制：

#### 权限分类
- **本地费用管理** - 包含所有本地费用相关权限

#### 具体权限
- `local_fee.list` - 查看本地费用列表
- `local_fee.detail` - 查看本地费用详情  
- `local_fee.create` - 创建本地费用
- `local_fee.update` - 修改本地费用
- `local_fee.delete` - 删除本地费用
- `local_fee.query` - 查询本地费用（前台API专用）

#### 权限说明
- **查看权限**：`local_fee.list`、`local_fee.detail`、`local_fee.query` - 适用于普通业务用户
- **编辑权限**：`local_fee.create`、`local_fee.update`、`local_fee.delete` - 适用于管理员用户
- **前台查询**：`local_fee.query` - 专门用于前台查询API，所有业务用户都应该拥有

### 1. 创建本地费用

**POST** `/api/local-fees/local-fees/`

**权限要求**: `local_fee.create`

**请求体示例：**
```json
{
    "polCd": "CNSHK",
    "podCd": "THBKK",
    "carriercd": "MSK",
    "name": "起运港码头费",
    "unit_name": "箱型",
    "price_20gp": "760.00",
    "price_40gp": "1287.00",
    "price_40hq": "1287.00",
    "currency": "CNY"
}
```

**响应示例：**
```json
{
    "status": "success",
    "message": "本地费用创建成功",
    "data": {
        "id": 1,
        "polCd": "CNSHK",
        "podCd": "THBKK",
        "carriercd": "MSK",
        "name": "起运港码头费",
        "unit_name": "箱型",
        "price_20gp": "760.00",
        "price_40gp": "1287.00",
        "price_40hq": "1287.00",
        "price_per_bill": null,
        "currency": "CNY",
        "created_at": "2025-05-27T20:46:06.123456Z",
        "updated_at": "2025-05-27T20:46:06.123456Z"
    }
}
```

### 2. 查询本地费用（前端格式）⭐ 重要

**GET** `/api/local-fees/local-fees/query/?polCd=CNSHK&podCd=INMAA&carriercd=IAL`

**权限要求**: `local_fee.query`

**查询参数：**
- `polCd` (必填): 起运港五字码
- `podCd` (必填): 目的港五字码
- `carriercd` (可选): 船公司英文名

**响应示例：**
```json
{
    "status": "success",
    "data": [
        {
            "id": 15,
            "名称": "起运港码头费",
            "单位": "箱型",
            "20GP": "760.00",
            "40GP": "1287.00",
            "40HQ": "1287.00",
            "单票价格": null,
            "币种": "CNY"
        },
        {
            "id": 16,
            "名称": "保安费",
            "单位": "票",
            "20GP": null,
            "40GP": null,
            "40HQ": null,
            "单票价格": "50.00",
            "币种": "USD"
        }
    ]
}
```

### 3. 获取所有本地费用

**GET** `/api/local-fees/local-fees/`

**权限要求**: `local_fee.list`

**查询参数（可选）：**
- `polCd`: 按起运港过滤
- `podCd`: 按目的港过滤
- `carriercd`: 按船公司过滤

### 4. 获取单个本地费用

**GET** `/api/local-fees/local-fees/{id}/`

**权限要求**: `local_fee.detail`

### 5. 更新本地费用

**PUT** `/api/local-fees/local-fees/{id}/`

**权限要求**: `local_fee.update`

**请求体格式与创建相同**

### 6. 删除本地费用

**DELETE** `/api/local-fees/local-fees/{id}/`

**权限要求**: `local_fee.delete`

**响应示例：**
```json
{
    "status": "success",
    "message": "本地费用删除成功"
}
```

## 前台对接信息

### 测试数据
已为前台测试准备了模拟数据：
- **起运港**: CNSHK (上海)
- **目的港**: INMAA (马德拉斯)  
- **船公司**: IAL
- **费用数量**: 5个

### 测试费用列表
1. **起运港码头费** - 箱型计费 (CNY)
   - 20GP: 760.00
   - 40GP: 1287.00
   - 40HQ: 1287.00

2. **保安费** - 票计费 (USD)
   - 单票价格: 50.00

3. **文件费** - 票计费 (USD)
   - 单票价格: 25.00

4. **目的港码头费** - 箱型计费 (INR)
   - 20GP: 850.00
   - 40GP: 1400.00
   - 40HQ: 1400.00

5. **燃油附加费** - 箱型计费 (USD)
   - 20GP: 120.00
   - 40GP: 240.00
   - 40HQ: 240.00

### 前台查询示例
```javascript
// 查询本地费用
const response = await fetch('/api/local-fees/local-fees/query/?polCd=CNSHK&podCd=INMAA&carriercd=IAL', {
    headers: {
        'Authorization': 'Bearer ' + token
    }
});
const data = await response.json();
console.log(data.data); // 费用列表
```

### 权限配置建议
为前台用户配置以下权限：
- `local_fee.query` - 必需，用于查询费用
- `local_fee.list` - 可选，用于列表查看
- `local_fee.detail` - 可选，用于详情查看

## 测试

### 运行模型测试
```bash
python3 test_api.py
```

### 运行HTTP API测试
```bash
python3 test_http_api.py
```

### 使用pytest（需要安装pytest）
```bash
pip install pytest pytest-django
pytest local_fees/tests.py -v
```

### 权限测试
```bash
python3 test_permissions.py
```

## 数据库迁移

模块已经包含了完整的数据库迁移文件：

```bash
# 应用迁移
python3 manage.py migrate local_fees
```

## 管理后台

模块提供了Django Admin管理界面，可以通过 `/admin/` 访问本地费用管理。

## 文件结构

```
local_fees/
├── __init__.py
├── admin.py              # Django Admin配置
├── apps.py              # 应用配置
├── models.py            # 数据模型
├── serializers.py       # API序列化器
├── views.py             # API视图
├── urls.py              # URL路由
├── tests.py             # 测试文件
├── permissions.py       # 权限配置
├── migrations/          # 数据库迁移文件
│   └── 0006_reset_to_simple_model.py
└── README.md           # 本文档
```

## 特性

1. **简化设计**: 删除了复杂的旧接口，只保留必要的功能
2. **唯一性约束**: 确保数据的一致性
3. **灵活查询**: 支持多种查询条件
4. **前端友好**: 查询API返回前端需要的格式
5. **完整测试**: 包含模型和API的完整测试
6. **细粒度权限**: 与现有权限系统完全兼容
7. **管理后台**: 提供完整的后台管理界面

## 使用示例

### Python代码示例

```python
from local_fees.models import LocalFee
from decimal import Decimal

# 创建本地费用
local_fee = LocalFee.objects.create(
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

# 查询本地费用
fees = LocalFee.objects.filter(
    polCd='CNSHK',
    podCd='INMAA',
    carriercd='IAL'
).order_by('id')
```

### JavaScript/前端示例

```javascript
// 查询本地费用
const response = await fetch('/api/local-fees/local-fees/query/?polCd=CNSHK&podCd=INMAA&carriercd=IAL', {
    headers: {
        'Authorization': 'Bearer ' + token
    }
});
const data = await response.json();
console.log(data.data); // 费用列表

// 创建本地费用
const createResponse = await fetch('/api/local-fees/local-fees/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({
        polCd: 'CNSHK',
        podCd: 'INMAA',
        carriercd: 'IAL',
        name: '起运港码头费',
        unit_name: '箱型',
        price_20gp: '760.00',
        price_40gp: '1287.00',
        price_40hq: '1287.00',
        currency: 'CNY'
    })
});
```

## 注意事项

1. 所有价格字段都是可选的，但建议至少填写一种价格类型
2. `unit_name` 字段有默认值"箱型"
3. 查询API的 `polCd` 和 `podCd` 是必填参数
4. 唯一性约束确保不会创建重复的费用记录
5. 所有API都需要用户认证和相应权限
6. 前台查询使用专门的 `local_fee.query` 权限

## 权限故障排除

如果遇到权限问题：

1. **403 Forbidden**: 用户没有相应权限，请联系管理员分配权限
2. **401 Unauthorized**: 用户未登录或token过期，请重新登录
3. **权限不生效**: 检查用户是否被分配了正确的角色，角色是否包含所需权限

## 更新日志

### v2.0 (2025-05-27)
- ✅ 重新设计权限系统，使用细粒度权限控制
- ✅ 清理所有旧的本地费用权限（82个）
- ✅ 统一权限名称为中文
- ✅ 创建6个新的简化权限
- ✅ 为前台测试准备模拟数据
- ✅ 完善权限测试和文档 