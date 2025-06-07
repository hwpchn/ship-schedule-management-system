#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import datetime
import os
from process_routes import (
    load_config, save_to_database, process_routes, 
    setup_database, get_latest_data_version
)

# 创建模拟的起运港数据
mock_loading_ports = [
    {
        "id": 1,
        "code": "CNSHK",
        "name_zh": "蛇口",
        "created_at": "2025-05-14T19:31:49.470823",
        "updated_at": "2025-05-14T19:31:49.470836"
    },
    {
        "id": 2, 
        "code": "CNDCB",
        "name_zh": "大铲湾",
        "created_at": "2025-05-14T19:31:49.471689",
        "updated_at": "2025-05-14T19:31:49.471694"
    }
]

# 创建模拟的目的港数据
mock_discharge_ports = [
    {
        "id": 69,
        "code": "AEAJM",
        "name_zh": "AJMAN(阿治曼,阿联酋)",
        "created_at": "2025-05-14T19:31:49.511807",
        "updated_at": "2025-05-14T19:31:49.511813"
    },
    {
        "id": 70,
        "code": "SGSIN",
        "name_zh": "新加坡",
        "created_at": "2025-05-14T19:31:49.511807", 
        "updated_at": "2025-05-14T19:31:49.511813"
    }
]

# 创建模拟的航线API响应
def create_mock_vessel_data(pol_cd, pod_cd):
    return {
        "code": 200,
        "message": "Success",
        "result": [
            {
                "routeCd": "TEST-ROUTE",
                "routeEtd": "周三",
                "carriercd": "TEST",
                "isReferenceCarrier": "1",
                "imo": "1234567",
                "vessel": f"TEST-VESSEL-{pol_cd}",
                "voyage": f"V001-{pod_cd}",
                "shipAgency": "TEST AGENCY",
                "polCd": pol_cd,
                "pol": f"Port of {pol_cd}",
                "polTerminal": "Terminal A",
                "polTerminalCd": "TERM-A",
                "podCd": pod_cd,
                "pod": f"Port of {pod_cd}",
                "podTerminal": "Terminal B",
                "podTerminalCd": "TERM-B",
                "eta": "2025-05-20",
                "etd": "2025-05-15",
                "totalDuration": "5",
                "isTransit": "0",
                "shareCabins": [{"carrier": "TEST"}],
                "bookingCutoff": "2025-05-14T12:00:00",
                "cyOpen": "2025-05-10T08:00:00",
                "cyClose": "2025-05-14T18:00:00"
            },
            {
                "routeCd": "TEST-ROUTE2",
                "routeEtd": "周四",
                "carriercd": "OTHER",
                "isReferenceCarrier": "0",
                "imo": "7654321",
                "vessel": f"TEST-VESSEL-{pol_cd}",
                "voyage": f"V001-{pod_cd}",
                "shipAgency": "OTHER AGENCY",
                "polCd": pol_cd,
                "pol": f"Port of {pol_cd}",
                "polTerminal": "Terminal A",
                "polTerminalCd": "TERM-A",
                "podCd": pod_cd,
                "pod": f"Port of {pod_cd}",
                "podTerminal": "Terminal B",
                "podTerminalCd": "TERM-B",
                "eta": "2025-05-21",
                "etd": "2025-05-16",
                "totalDuration": "5",
                "isTransit": "0",
                "shareCabins": [{"carrier": "OTHER1"}, {"carrier": "OTHER2"}],
                "bookingCutoff": "2025-05-15T12:00:00",
                "cyOpen": "2025-05-11T08:00:00",
                "cyClose": "2025-05-15T18:00:00"
            }
        ]
    }

def main():
    # 显示当前工作目录，用于调试
    print(f"当前工作目录: {os.getcwd()}")
    
    # 加载配置
    config = load_config()
    
    # 确保数据库连接信息正确
    print("数据库配置:")
    for key in ['db_host', 'db_port', 'db_user', 'db_password', 'db_name', 'db_charset']:
        # 如果是密码，隐藏实际值
        if key == 'db_password':
            print(f"  {key}: {'*' * len(config.get(key, ''))}")
        else:
            print(f"  {key}: {config.get(key, 'N/A')}")
    
    # 测试数据库连接
    try:
        conn = setup_database(config)
        current_version = get_latest_data_version(conn)
        print(f"数据库连接成功! 当前最新数据版本: {current_version}")
        conn.close()
    except Exception as e:
        print(f"数据库连接测试失败: {e}")
        print("请检查数据库配置后重试")
        return
    
    all_selected_routes = []
    
    # 模拟处理每对起运港和目的港组合
    print(f"共找到 {len(mock_loading_ports)} 个起运港和 {len(mock_discharge_ports)} 个目的港")
    total = len(mock_loading_ports) * len(mock_discharge_ports)
    count = 0
    
    for pol in mock_loading_ports:
        for pod in mock_discharge_ports:
            count += 1
            pol_cd = pol["code"]
            pod_cd = pod["code"]
            
            print(f"处理组合 [{count}/{total}]: 起运港 {pol_cd} ({pol['name_zh']}) -> 目的港 {pod_cd} ({pod['name_zh']})")
            
            # 创建模拟数据
            data = create_mock_vessel_data(pol_cd, pod_cd)
            
            # 处理数据
            selected_routes = process_routes(data, pod_cd)
            
            if selected_routes:
                all_selected_routes.extend(selected_routes)
                print(f"该组合选择了 {len(selected_routes)} 条航线")
                for route in selected_routes:
                    print(f"  船名: {route.get('vessel', 'N/A')}, 航次: {route.get('voyage', 'N/A')}")
            else:
                print("该组合未找到符合条件的航线")
    
    # 打印总结果
    print(f"\n所有组合共选择了 {len(all_selected_routes)} 条航线")
    
    # 将数据存入数据库
    print("\n尝试将数据写入数据库...")
    save_to_database(all_selected_routes, config)
    
    print("\n测试完成！请检查数据库中是否已插入数据。")
    print("可以使用以下SQL查询验证:")
    print("SELECT COUNT(*) FROM vessel_schedule;")
    print("SELECT polCd, podCd, vessel, voyage, data_version FROM vessel_schedule ORDER BY id DESC LIMIT 10;")

if __name__ == "__main__":
    main()
