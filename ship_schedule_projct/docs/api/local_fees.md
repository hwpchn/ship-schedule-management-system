# 本地费用API文档

## 📋 概述

本地费用模块提供完整的本地费用管理功能，支持费用的增删改查操作，以及专门的前台查询API。

**基础路径**: `/api/local-fees/`

## 💰 本地费用管理

### 1. 获取费用列表

**端点**: `GET /api/local-fees/local-fees/`  
**权限**: `local_fee.list`  
**描述**: 获取本地费用列表，支持分页和过滤

#### 查询参数
| 参数 | 类型 | 说明 |
|------|------|------|
| polCd | string | 起运港五字码过滤 |
| podCd | string | 目的港五字码过滤 |
| carriercd | string | 船公司代码过滤 |
| search | string | 搜索费用名称、港口代码等 |
| page | integer | 页码 |
| page_size | integer | 每页数量 |

#### 响应示例
```json
{
    "count": 25,
    "next": "http://127.0.0.1:8000/api/local-fees/local-fees/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "polCd": "CNSHK",
            "podCd": "INMAA",
            "carriercd": "IAL",
            "name": "起运港码头费",
            "unit_name": "箱型",
            "price_20gp": "760.00",
            "price_40gp": "1287.00",
            "price_40hq": "1287.00",
            "price_per_bill": null,
            "currency": "CNY",
            "created_at": "2025-05-27T10:00:00Z",
            "updated_at": "2025-05-27T10:00:00Z"
        }
    ]
}
```

### 2. 创建本地费用

**端点**: `POST /api/local-fees/local-fees/`  
**权限**: `local_fee.create`  
**描述**: 创建新的本地费用记录

#### 请求参数
```json
{
    "polCd": "CNSHK",
    "podCd": "INMAA",
    "carriercd": "IAL",
    "name": "起运港码头费",
    "unit_name": "箱型",
    "price_20gp": "760.00",
    "price_40gp": "1287.00",
    "price_40hq": "1287.00",
    "currency": "CNY"
}
```

#### 字段说明
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| polCd | string | 是 | 起运港五字码 |
| podCd | string | 是 | 目的港五字码 |
| carriercd | string | 否 | 船公司英文名 |
| name | string | 是 | 费用类型名称（如：起运港码头费、保安费） |
| unit_name | string | 否 | 单位名称（默认：箱型） |
| price_20gp | decimal | 否 | 20GP价格 |
| price_40gp | decimal | 否 | 40GP价格 |
| price_40hq | decimal | 否 | 40HQ价格 |
| price_per_bill | decimal | 否 | 每票价格（用于按票计费的费用） |
| currency | string | 否 | 货币代码（如：CNY、USD、EUR） |

#### 响应示例
```json
{
    "status": "success",
    "message": "本地费用创建成功",
    "data": {
        "id": 1,
        "polCd": "CNSHK",
        "podCd": "INMAA",
        "carriercd": "IAL",
        "name": "起运港码头费",
        "unit_name": "箱型",
        "price_20gp": "760.00",
        "price_40gp": "1287.00",
        "price_40hq": "1287.00",
        "price_per_bill": null,
        "currency": "CNY",
        "created_at": "2025-05-27T10:00:00Z",
        "updated_at": "2025-05-27T10:00:00Z"
    }
}
```

### 3. 获取费用详情

**端点**: `GET /api/local-fees/local-fees/{id}/`  
**权限**: `local_fee.detail`  
**描述**: 获取特定本地费用的详细信息

#### 响应示例
```json
{
    "id": 1,
    "polCd": "CNSHK",
    "podCd": "INMAA",
    "carriercd": "IAL",
    "name": "起运港码头费",
    "unit_name": "箱型",
    "price_20gp": "760.00",
    "price_40gp": "1287.00",
    "price_40hq": "1287.00",
    "price_per_bill": null,
    "currency": "CNY",
    "created_at": "2025-05-27T10:00:00Z",
    "updated_at": "2025-05-27T10:00:00Z"
}
```

### 4. 更新本地费用

**端点**: `PUT /api/local-fees/local-fees/{id}/`  
**权限**: `local_fee.update`  
**描述**: 更新本地费用信息

#### 请求参数
与创建时相同，支持部分更新

#### 响应示例
```json
{
    "status": "success",
    "message": "本地费用更新成功",
    "data": {
        // 更新后的费用信息
    }
}
```

### 5. 删除本地费用

**端点**: `DELETE /api/local-fees/local-fees/{id}/`  
**权限**: `local_fee.delete`  
**描述**: 删除本地费用记录

#### 响应示例
```json
{
    "status": "success",
    "message": "本地费用删除成功"
}
```

## 🔍 前台查询API ⭐ 重要

### 费用查询（前端格式）

**端点**: `GET /api/local-fees/local-fees/query/`  
**权限**: `local_fee.query`  
**描述**: 前台专用的费用查询API，返回前端友好的格式

#### 查询参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| polCd | string | 是 | 起运港五字码 |
| podCd | string | 是 | 目的港五字码 |
| carriercd | string | 否 | 船公司英文名 |

#### 响应示例
```json
{
    "status": "success",
    "data": [
        {
            "id": 1,
            "名称": "起运港码头费",
            "单位": "箱型",
            "20GP": "760.00",
            "40GP": "1287.00",
            "40HQ": "1287.00",
            "单票价格": null,
            "币种": "CNY"
        },
        {
            "id": 2,
            "名称": "保安费",
            "单位": "票",
            "20GP": null,
            "40GP": null,
            "40HQ": null,
            "单票价格": "50.00",
            "币种": "USD"
        },
        {
            "id": 3,
            "名称": "文件费",
            "单位": "票",
            "20GP": null,
            "40GP": null,
            "40HQ": null,
            "单票价格": "25.00",
            "币种": "USD"
        },
        {
            "id": 4,
            "名称": "目的港码头费",
            "单位": "箱型",
            "20GP": "850.00",
            "40GP": "1400.00",
            "40HQ": "1400.00",
            "单票价格": null,
            "币种": "INR"
        },
        {
            "id": 5,
            "名称": "燃油附加费",
            "单位": "箱型",
            "20GP": "120.00",
            "40GP": "240.00",
            "40HQ": "240.00",
            "单票价格": null,
            "币种": "USD"
        }
    ]
}
```

#### 响应字段说明
| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 费用记录ID |
| 名称 | string | 费用类型名称 |
| 单位 | string | 计费单位（箱型/票） |
| 20GP | string/null | 20尺普通箱价格 |
| 40GP | string/null | 40尺普通箱价格 |
| 40HQ | string/null | 40尺高箱价格 |
| 单票价格 | string/null | 按票计费的价格 |
| 币种 | string | 货币代码 |

## 📊 数据模型

### LocalFee模型字段
```python
class LocalFee(models.Model):
    id = models.AutoField(primary_key=True)
    
    # 核心字段
    polCd = models.CharField(max_length=10)           # 起运港五字码
    podCd = models.CharField(max_length=10)           # 目的港五字码
    carriercd = models.CharField(max_length=20)       # 船公司英文名
    name = models.CharField(max_length=100)           # 费用类型名称
    unit_name = models.CharField(max_length=50)       # 单位名称
    
    # 价格字段
    price_20gp = models.DecimalField(max_digits=10, decimal_places=2)    # 20GP价格
    price_40gp = models.DecimalField(max_digits=10, decimal_places=2)    # 40GP价格
    price_40hq = models.DecimalField(max_digits=10, decimal_places=2)    # 40HQ价格
    price_per_bill = models.DecimalField(max_digits=10, decimal_places=2) # 每票价格
    
    currency = models.CharField(max_length=20)        # 货币
    
    # 时间字段
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 唯一性约束
模型使用组合唯一约束：`unique_together = ['carriercd', 'polCd', 'podCd', 'name']`

确保同一船公司、起运港、目的港和费用类型的组合是唯一的。

## 💡 使用示例

### 创建费用记录
```bash
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
    "price_40gp": "1287.00",
    "price_40hq": "1287.00",
    "currency": "CNY"
  }'
```

### 查询费用（前台格式）
```bash
curl -X GET "http://127.0.0.1:8000/api/local-fees/local-fees/query/?polCd=CNSHK&podCd=INMAA&carriercd=IAL" \
  -H "Authorization: Bearer <token>"
```

### 更新费用记录
```bash
curl -X PUT http://127.0.0.1:8000/api/local-fees/local-fees/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "price_20gp": "800.00",
    "price_40gp": "1350.00"
  }'
```

## 🧪 测试数据

系统已预置测试数据，用于前台对接测试：

**测试路线**: CNSHK → INMAA (上海 → 马德拉斯)  
**测试船公司**: IAL  
**费用数量**: 5个

### 测试费用列表
1. **起运港码头费** - 箱型计费 (CNY)
2. **保安费** - 票计费 (USD)
3. **文件费** - 票计费 (USD)
4. **目的港码头费** - 箱型计费 (INR)
5. **燃油附加费** - 箱型计费 (USD)

## ⚠️ 注意事项

1. **唯一性约束**: 同一船公司、起运港、目的港和费用类型的组合必须唯一
2. **价格验证**: 价格不能为负数
3. **计费方式**: 支持按箱型计费和按票计费两种方式
4. **货币支持**: 支持多种货币（CNY、USD、EUR、INR等）
5. **前台格式**: 查询API返回中文字段名，便于前台直接使用
6. **权限控制**: 不同操作需要相应权限，确保数据安全
