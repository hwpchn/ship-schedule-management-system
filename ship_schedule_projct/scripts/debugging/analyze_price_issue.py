#!/usr/bin/env python3
import json
from datetime import datetime

def analyze_price_logic():
    """分析价格计算逻辑问题"""
    
    # 从响应数据中提取第一个分组 (group_2) 的数据
    group_data = {
        "group_id": "group_2",
        "cabin_price": "--",
        "schedules": [
            {
                "id": 2008,
                "vessel": "INTERASIA ENHANCE",
                "etd": "2025-06-15 01:00:00",
                "vessel_info": {"price": 10.0}
            },
            {
                "id": 2003,
                "vessel": "WAN HAI 321",
                "etd": "2025-06-08 01:00:00",
                "vessel_info": {"price": 20.0}
            },
            {
                "id": 1998,
                "vessel": "WAN HAI 361",
                "etd": "2025-06-01 01:00:00",
                "vessel_info": {"price": 90.0}
            },
            {
                "id": 1993,
                "vessel": "WAN HAI 366",
                "etd": "2025-05-25 01:00:00",
                "vessel_info": {"price": "--"}
            },
            {
                "id": 2011,
                "vessel": "WAN HAI 367",
                "etd": "2025-06-22 04:00:00",
                "vessel_info": {"price": "--"}
            },
            {
                "id": 1982,
                "vessel": "INTERASIA ENHANCE",
                "etd": "2025-05-14 10:30:00",
                "vessel_info": {"price": 90.0}
            },
            {
                "id": 1986,
                "vessel": "WAN HAI 367",
                "etd": "2025-05-17 20:30:00",
                "vessel_info": {"price": "--"}
            }
        ]
    }
    
    print("🔍 分析第一个分组 (group_2) 的价格计算逻辑")
    print("=" * 80)
    print(f"API返回的分组cabin_price: {group_data['cabin_price']}")
    print(f"分组包含 {len(group_data['schedules'])} 个船期")
    print("-" * 80)
    
    # 按照API逻辑分析每个船期
    etd_schedules = []
    
    for i, schedule in enumerate(group_data['schedules']):
        etd = schedule['etd']
        vessel_info = schedule['vessel_info']
        price = vessel_info.get('price')
        
        print(f"船期 {i+1}: {schedule['vessel']} - ETD={etd}, price={price}")
        
        if etd:
            try:
                # 只提取日期部分进行比较（与API逻辑一致）
                etd_date = datetime.strptime(etd, '%Y-%m-%d %H:%M:%S').date()
                etd_schedules.append({
                    'etd_date': etd_date,
                    'etd_str': etd,
                    'price': price,
                    'schedule_index': i,
                    'vessel': schedule['vessel']
                })
            except Exception as e:
                print(f"    ❌ ETD日期解析失败: {e}")
    
    print("-" * 40)
    print("📊 ETD日期排序分析:")
    
    # 按ETD日期排序
    etd_schedules.sort(key=lambda x: x['etd_date'])
    
    for i, schedule in enumerate(etd_schedules):
        marker = "🎯 最早" if i == 0 else "   "
        print(f"{marker} {schedule['vessel']} - ETD: {schedule['etd_date']} - price: {schedule['price']}")
    
    # 找到最早的ETD日期
    if etd_schedules:
        earliest = etd_schedules[0]  # 排序后第一个就是最早的
        print("-" * 40)
        print(f"🎯 最早ETD船期: {earliest['vessel']}")
        print(f"🎯 最早ETD日期: {earliest['etd_date']}")
        print(f"🎯 对应价格: {earliest['price']}")
        
        # 模拟API价格计算逻辑
        if earliest['price'] is not None and earliest['price'] != '--':
            calculated_price = earliest['price']
        else:
            calculated_price = '--'
            
        print(f"🎯 计算出的价格: {calculated_price}")
        
        # 与API返回的价格对比
        if calculated_price != group_data['cabin_price']:
            print(f"⚠️  价格不匹配!")
            print(f"   API返回: {group_data['cabin_price']}")
            print(f"   计算结果: {calculated_price}")
            print(f"   🔍 问题分析: 最早ETD船期的价格是 {earliest['price']}，但API返回 '--'")
        else:
            print(f"✅ 价格计算正确")
    else:
        print("❌ 没有有效的ETD数据")
    
    print("=" * 80)
    print("💡 结论:")
    print("   从分析来看，API的价格计算逻辑存在问题：")
    print("   1. 最早ETD船期（2025-05-14）的价格是 90.0")
    print("   2. 但API返回的cabin_price却是 '--'")
    print("   3. 可能的原因：")
    print("      - 价格字段的数据类型处理问题")
    print("      - ETD日期比较逻辑有误")
    print("      - 价格验证逻辑过于严格")

if __name__ == "__main__":
    analyze_price_logic()
