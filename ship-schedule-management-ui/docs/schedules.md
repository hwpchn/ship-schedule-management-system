# 船期管理API文档

## 📋 概述

船期管理模块是系统的核心功能，提供船舶航线管理、船舶额外信息管理、共舱分组查询等功能。

**基础路径**: `/api/`

## 🚢 船舶航线管理

### 1. 获取航线列表

**端点**: `GET /api/schedules/`  
**权限**: `vessel_schedule.list`  
**描述**: 获取船舶航线列表，支持分页和过滤

#### 查询参数
| 参数 | 类型 | 说明 |
|------|------|------|
| status | integer | 数据状态过滤（1-有效，0-无效） |
| polCd | string | 起运港五字码过滤 |
| podCd | string | 目的港五字码过滤 |
| carriercd | string | 船公司代码过滤 |
| data_version | integer | 数据版本过滤 |
| search | string | 搜索船名、航次、港口等 |
| ordering | string | 排序字段（如：-fetch_date） |
| page | integer | 页码 |
| page_size | integer | 每页数量 |

#### 响应示例
```json
{
    "count": 150,
    "next": "http://127.0.0.1:8000/api/schedules/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "vessel": "MSC OSCAR",
            "voyage": "251W",
            "polCd": "CNSHA",
            "podCd": "USNYC",
            "pol": "上海",
            "pod": "纽约",
            "eta": "2025-06-15",
            "etd": "2025-05-20",
            "status": 1,
            "data_version": 20250527,
            "fetch_date": "2025-05-27T10:00:00Z"
        }
    ]
}
```

### 2. 创建航线

**端点**: `POST /api/schedules/`  
**权限**: `vessel_schedule.create`  
**描述**: 创建新的船舶航线记录

#### 请求参数
```json
{
    "polCd": "CNSHA",
    "podCd": "USNYC",
    "vessel": "MSC OSCAR",
    "voyage": "251W",
    "data_version": 20250527,
    "pol": "上海",
    "pod": "纽约",
    "eta": "2025-06-15",
    "etd": "2025-05-20",
    "carriercd": "MSK",
    "routeEtd": "3",
    "totalDuration": "26",
    "shareCabins": [
        {"carrierCd": "MSK"},
        {"carrierCd": "ONE"}
    ]
}
```

#### 必填字段
| 字段 | 类型 | 说明 |
|------|------|------|
| polCd | string | 起运港五字码 |
| podCd | string | 目的港五字码 |
| vessel | string | 船名 |
| voyage | string | 航次 |
| data_version | integer | 数据版本号 |

### 3. 获取航线详情

**端点**: `GET /api/schedules/{id}/`  
**权限**: `vessel_schedule.detail`  
**描述**: 获取特定航线的详细信息

#### 响应示例
```json
{
    "id": 1,
    "polCd": "CNSHA",
    "podCd": "USNYC",
    "vessel": "MSC OSCAR",
    "voyage": "251W",
    "data_version": 20250527,
    "fetch_timestamp": 1716811200,
    "fetch_date": "2025-05-27T10:00:00Z",
    "status": 1,
    "routeCd": "AE1",
    "routeEtd": "3",
    "carriercd": "MSK",
    "isReferenceCarrier": "Y",
    "imo": "9778693",
    "pol": "上海",
    "pod": "纽约",
    "eta": "2025-06-15",
    "etd": "2025-05-20",
    "totalDuration": "26",
    "shareCabins": [
        {"carrierCd": "MSK"},
        {"carrierCd": "ONE"}
    ],
    "remark": "正常航次"
}
```

### 4. 更新航线

**端点**: `PUT /api/schedules/{id}/`  
**权限**: `vessel_schedule.update`  
**描述**: 更新航线信息

### 5. 删除航线

**端点**: `DELETE /api/schedules/{id}/`  
**权限**: `vessel_schedule.delete`  
**描述**: 删除航线记录

## 📊 船舶额外信息管理

### 1. 获取船舶信息列表

**端点**: `GET /api/vessel-info/`  
**权限**: `vessel_info.list`  
**描述**: 获取船舶额外信息列表

#### 查询参数
| 参数 | 类型 | 说明 |
|------|------|------|
| carriercd | string | 船公司代码过滤 |
| polCd | string | 起运港五字码过滤 |
| podCd | string | 目的港五字码过滤 |
| search | string | 搜索船名、航次、船公司 |

#### 响应示例
```json
{
    "count": 50,
    "results": [
        {
            "id": 1,
            "carriercd": "MSK",
            "polCd": "CNSHA",
            "podCd": "USNYC",
            "vessel": "MSC OSCAR",
            "voyage": "251W",
            "gp_20": "100",
            "hq_40": "50",
            "cut_off_time": "2025-05-18 18:00",
            "price": "4500.00"
        }
    ]
}
```

### 2. 创建船舶信息

**端点**: `POST /api/vessel-info/`  
**权限**: `vessel_info.create`  
**描述**: 创建船舶额外信息

#### 请求参数
```json
{
    "carriercd": "MSK",
    "polCd": "CNSHA",
    "podCd": "USNYC",
    "vessel": "MSC OSCAR",
    "voyage": "251W",
    "gp_20": "100",
    "hq_40": "50",
    "cut_off_time": "2025-05-18 18:00",
    "price": "4500.00"
}
```

#### 必填字段
| 字段 | 类型 | 说明 |
|------|------|------|
| carriercd | string | 船公司代码 |
| polCd | string | 起运港五字码 |
| podCd | string | 目的港五字码 |
| vessel | string | 船名 |
| voyage | string | 航次 |

### 3. 批量操作

#### 批量创建
**端点**: `POST /api/vessel-info/bulk-create/`  
**权限**: `vessel_info.create`

```json
{
    "items": [
        {
            "carriercd": "MSK",
            "polCd": "CNSHA",
            "podCd": "USNYC",
            "vessel": "MSC OSCAR",
            "voyage": "251W",
            "price": "4500.00"
        },
        {
            "carriercd": "ONE",
            "polCd": "CNSHA",
            "podCd": "USNYC",
            "vessel": "ONE TRUST",
            "voyage": "052E",
            "price": "4200.00"
        }
    ]
}
```

#### 批量更新
**端点**: `PATCH /api/vessel-info/bulk-update/`  
**权限**: `vessel_info.update`

#### 批量删除
**端点**: `DELETE /api/vessel-info/bulk-delete/`  
**权限**: `vessel_info.delete`

```json
{
    "ids": [1, 2, 3, 4, 5]
}
```

### 4. 船舶信息查询

**端点**: `GET /api/vessel-info/query/`  
**权限**: `vessel_info.list`  
**描述**: 根据关联字段查询特定船舶信息

#### 查询参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| vessel | string | 是 | 船名 |
| voyage | string | 是 | 航次 |
| carriercd | string | 是 | 船公司代码 |
| polCd | string | 是 | 起运港五字码 |
| podCd | string | 是 | 目的港五字码 |

## 🔍 前台查询API

### 1. 共舱分组查询（含额外信息）⭐ 重要

**端点**: `GET /api/schedules/cabin-grouping-with-info/`  
**权限**: `vessel_schedule_list`  
**描述**: 前台船期查询专用API，返回分组后的船期信息及额外信息

#### 查询参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| polCd | string | 是 | 起运港五字码 |
| podCd | string | 是 | 目的港五字码 |

#### 响应示例
```json
{
    "success": true,
    "message": "共舱分组数据获取成功",
    "data": {
        "groups": [
            {
                "group_id": "group_1",
                "cabins_count": 2,
                "carrier_codes": ["MSK", "ONE"],
                "plan_open": "3",
                "plan_duration": 26,
                "cabin_price": 4500,
                "is_has_gp_20": "有现舱",
                "is_has_hq_40": "有现舱",
                "schedules": [
                    {
                        "id": 1,
                        "vessel": "MSC OSCAR",
                        "voyage": "251W",
                        "polCd": "CNSHA",
                        "podCd": "USNYC",
                        "pol": "上海",
                        "pod": "纽约",
                        "eta": "2025-06-15",
                        "etd": "2025-05-20",
                        "routeEtd": "3",
                        "carriercd": "MSK",
                        "totalDuration": "26",
                        "shareCabins": [
                            {"carrierCd": "MSK"},
                            {"carrierCd": "ONE"}
                        ],
                        "vessel_info": {
                            "id": 1,
                            "gp_20": "100",
                            "hq_40": "50",
                            "price": "4500.00",
                            "cut_off_time": "2025-05-18 18:00"
                        }
                    }
                ]
            }
        ],
        "total_groups": 1,
        "version": "20250527",
        "filter": {
            "polCd": "CNSHA",
            "podCd": "USNYC"
        }
    }
}
```

#### 响应字段说明
| 字段 | 类型 | 说明 |
|------|------|------|
| group_id | string | 分组ID |
| cabins_count | integer | 共舱数量 |
| carrier_codes | array | 船公司代码列表 |
| plan_open | string/array | 计划开船日 |
| plan_duration | integer | 计划航程时间（天） |
| cabin_price | number/string | 舱位价格，可能为"--" |
| is_has_gp_20 | string | 20尺集装箱现舱情况 |
| is_has_hq_40 | string | 40尺集装箱现舱情况 |
| vessel_info | object | 船舶额外信息 |

### 2. 基础共舱分组

**端点**: `GET /api/schedules/cabin-grouping/`  
**权限**: `vessel_schedule.list`  
**描述**: 基础共舱分组查询，不包含额外信息

#### 查询参数
同上

#### 响应示例
```json
{
    "success": true,
    "message": "共舱分组数据获取成功",
    "data": {
        "groups": [
            {
                "group_id": "group_1",
                "cabins_count": 2,
                "carrier_codes": ["MSK", "ONE"],
                "plan_open": ["3"],
                "plan_duration": "26",
                "schedules": [
                    {
                        "id": 1,
                        "vessel": "MSC OSCAR",
                        "voyage": "251W",
                        "polCd": "CNSHA",
                        "podCd": "USNYC",
                        "pol": "上海",
                        "pod": "纽约",
                        "eta": "2025-06-15",
                        "etd": "2025-05-20",
                        "routeEtd": "3",
                        "carriercd": "MSK",
                        "totalDuration": "26",
                        "shareCabins": [
                            {"carrierCd": "MSK"},
                            {"carrierCd": "ONE"}
                        ]
                    }
                ]
            }
        ],
        "total_groups": 1,
        "version": "20250527"
    }
}
```

## 🔧 共舱配置管理

### 1. 获取配置详情

**端点**: `GET /api/cabin-config/detail/`  
**权限**: `vessel_schedule.detail`  
**描述**: 获取单个航线的共舱配置详情

#### 查询参数
| 参数 | 类型 | 说明 |
|------|------|------|
| schedule_id | integer | VesselSchedule的ID |
| polCd | string | 起运港五字码（无schedule_id时必填） |
| podCd | string | 目的港五字码（无schedule_id时必填） |
| vessel | string | 船名（无schedule_id时必填） |
| voyage | string | 航次（无schedule_id时必填） |

### 2. 更新配置

**端点**: `PUT /api/cabin-config/update/`  
**权限**: `vessel_schedule.update`  
**描述**: 更新共舱配置

### 3. 删除配置

**端点**: `DELETE /api/cabin-config/delete/`  
**权限**: `vessel_schedule.delete`  
**描述**: 删除共舱配置

### 4. 批量更新配置

**端点**: `POST /api/cabin-config/bulk-update/`  
**权限**: `vessel_schedule.update`  
**描述**: 批量更新共舱配置

## 📊 统计和搜索

### 1. 航线搜索

**端点**: `GET /api/schedules/search/`  
**权限**: `vessel_schedule.list`  
**描述**: 高级搜索功能

### 2. 航线统计

**端点**: `GET /api/schedules/stats/`  
**权限**: `vessel_schedule.list`  
**描述**: 获取航线统计信息

## ⚠️ 注意事项

1. **数据版本**: 查询API只返回最新版本（data_version最大值）的数据
2. **共舱分组**: 基于shareCabins字段进行分组，相同共舱配置的航线会被分到同一组
3. **舱位显示**: "有现舱"表示有足够舱位，"--"表示无舱位或信息未知
4. **批量操作**: 支持批量创建、更新、删除，提高操作效率
5. **权限控制**: 不同操作需要相应权限，确保数据安全
