#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
import datetime
import os
import time
import pymysql
from unittest import mock
from typing import Dict, List, Any

# 导入我们要测试的函数
from process_routes import (
    load_config, save_to_database, process_routes, fetch_loading_ports,
    fetch_discharge_ports, fetch_vessel_schedule
)

# 创建模拟的起运港API响应
MOCK_LOADING_PORTS_RESPONSE = {
    "count": 4,
    "results": [
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
}

# 创建模拟的目的港API响应
MOCK_DISCHARGE_PORTS_RESPONSE = {
    "count": 2,
    "next": None,
    "previous": None,
    "results": [
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
}

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

# 模拟requests.get方法
def mock_requests_get(url, params=None, **kwargs):
    response = mock.Mock()
    response.raise_for_status = mock.Mock()
    
    # 根据URL返回不同的模拟响应
    if 'loading/all' in url:
        print(f"模拟请求起运港API: {url}")
        response.json = lambda: MOCK_LOADING_PORTS_RESPONSE
    elif 'discharge' in url:
        print(f"模拟请求目的港API: {url}")
        response.json = lambda: MOCK_DISCHARGE_PORTS_RESPONSE
    else:
        response.json = lambda: {"error": "未知URL"}
    
    return response

# 模拟requests.request方法
def mock_requests_request(method, url, headers=None, data=None, **kwargs):
    response = mock.Mock()
    response.raise_for_status = mock.Mock()
    
    # 解析请求数据
    if data:
        try:
            request_data = json.loads(data)
            pol_cd = request_data.get("polCd")
            pod_cd = request_data.get("podCd")
            print(f"模拟请求航线API: {url} (polCd={pol_cd}, podCd={pod_cd})")
            response.json = lambda: create_mock_vessel_data(pol_cd, pod_cd)
        except json.JSONDecodeError:
            response.json = lambda: {"code": 400, "message": "无效的请求数据"}
    else:
        response.json = lambda: {"code": 400, "message": "缺少请求数据"}
    
    return response


def run_test_with_mock():
    """使用模拟API响应测试整个流程"""
    # 保存原始函数
    original_get = requests.get
    original_request = requests.request
    
    # 替换为模拟函数
    requests.get = mock_requests_get
    requests.request = mock_requests_request
    
    try:
        # 加载配置
        config = load_config()
        print("\n=== 使用模拟API测试港口批量查询流程 ===")
        
        # 获取起运港和目的港数据
        pol_ports = fetch_loading_ports(base_url="http://localhost:8000/api")
        pod_ports = fetch_discharge_ports(base_url="http://localhost:8000/api")
        
        if not pol_ports:
            print("没有找到起运港数据，测试中断")
            return
        
        if not pod_ports:
            print("没有找到目的港数据，测试中断")
            return
        
        all_selected_routes = []
        processed_count = 0
        total_combinations = len(pol_ports) * len(pod_ports)
        
        print(f"测试中: 共找到 {len(pol_ports)} 个起运港和 {len(pod_ports)} 个目的港，总计 {total_combinations} 个组合")
        
        # 对每对起运港和目的港进行查询
        for pol in pol_ports:
            for pod in pod_ports:
                processed_count += 1
                pol_cd = pol["code"]
                pod_cd = pod["code"]
                
                print(f"正在处理组合 [{processed_count}/{total_combinations}]: 起运港 {pol_cd} ({pol.get('name_zh', '')}) -> 目的港 {pod_cd} ({pod.get('name_zh', '')})")
                
                # 更新当前配置
                current_config = config.copy()
                current_config["pol_cd"] = pol_cd
                current_config["pod_cd"] = pod_cd
                
                # 从API获取数据
                data = fetch_vessel_schedule(current_config)
                
                # 处理数据
                selected_routes = process_routes(data, pod_cd)
                
                # 添加到总结果列表
                if selected_routes:
                    all_selected_routes.extend(selected_routes)
                    print(f"该组合选择了 {len(selected_routes)} 条航线")
                else:
                    print("该组合未找到符合条件的航线")
                
                # 模拟API请求间隔
                if processed_count < total_combinations:
                    print("模拟休息1秒继续...")
                    time.sleep(0.1)  # 测试环境下，不需要实际等待
        
        # 打印总结果
        print(f"\n所有组合共选择了 {len(all_selected_routes)} 条航线:")
        for route in all_selected_routes[:10]:
            print(f"起运港: {route.get('pol', 'N/A')} ({route.get('polCd', 'N/A')}), "
                  f"目的港: {route.get('pod', 'N/A')} ({route.get('podCd', 'N/A')}), "
                  f"船名: {route.get('vessel', 'N/A')}, "
                  f"航次: {route.get('voyage', 'N/A')}")
        
        # 将数据存入数据库
        print("\n尝试将数据写入数据库...")
        save_to_database(all_selected_routes, config)
        
    finally:
        # 恢复原始函数
        requests.get = original_get
        requests.request = original_request


if __name__ == "__main__":
    run_test_with_mock()
    print("\n测试完成！请检查数据库是否已插入数据。")
    print("您可以使用以下命令执行真实API流程:")
    print("python process_routes.py --use_port_api")
