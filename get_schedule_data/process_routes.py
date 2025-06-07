import json
import requests
import datetime
import argparse
import os
import pymysql
import time
from typing import Dict, List, Any

# 默认配置
DEFAULT_CONFIG = {
    "token": "8904e8ad-ce37-4abe-859c-2f0dcd3841d2",
    "company_id": "100091",
    "days_back": 2,
    "pol_cd": "CNXMN",
    "pod_cd": "VNVUT",
    "weeks_out": "6",
    "is_transit": "0",
    # 数据库默认配置（将从配置文件中覆盖）
    "db_host": "localhost",
    "db_port": 3306,
    "db_user": "root",
    "db_password": "",
    "db_name": "shipping_project",
    "db_charset": "utf8mb4"
}

def load_config(config_file: str = "config.json") -> Dict[str, str]:
    """从配置文件加载配置，如果不存在则使用默认配置"""
    config = DEFAULT_CONFIG.copy()
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                config.update(user_config)
                print(f"已从{config_file}加载配置")
                
                # 检查数据库配置
                db_keys = ['db_host', 'db_port', 'db_user', 'db_password', 'db_name', 'db_charset']
                missing_keys = [key for key in db_keys if key not in user_config]
                if missing_keys:
                    print(f"警告：配置文件缺少以下数据库配置项：{', '.join(missing_keys)}")
                    print("请更新配置文件或使用默认配置")
        else:
            print(f"配置文件{config_file}不存在，使用默认配置")
    except Exception as e:
        print(f"加载配置文件出错: {e}，使用默认配置")
    return config

def fetch_loading_ports(base_url="http://localhost:8000/api", code=None, name=None) -> List[Dict[str, Any]]:
    """获取所有起运港数据
    
    Args:
        base_url: API基础URL
        code: 按起运港代码过滤
        name: 按起运港名称过滤
        
    Returns:
        起运港数据列表，每个港口是一个字典
    """
    url = f"{base_url}/ports/loading/all/"
    params = {}
    if code:
        params["code"] = code
    if name:
        params["name"] = name
    
    try:
        print(f"正在获取起运港数据...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        print(f"成功获取 {data.get('count', 0)} 个起运港数据")
        return data.get("results", [])
    except requests.exceptions.RequestException as e:
        print(f"获取起运港数据失败: {e}")
        return []

def fetch_discharge_ports(base_url="http://localhost:8000/api", code=None, name=None) -> List[Dict[str, Any]]:
    """获取所有目的港数据，支持分页
    
    Args:
        base_url: API基础URL
        code: 按目的港代码过滤
        name: 按目的港名称过滤
        
    Returns:
        目的港数据列表，每个港口是一个字典
    """
    url = f"{base_url}/ports/discharge/"
    params = {}
    if code:
        params["code"] = code
    if name:
        params["name"] = name
    
    all_results = []
    next_url = url
    
    while next_url:
        try:
            print(f"正在获取目的港数据: {next_url}")
            response = requests.get(next_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            all_results.extend(data.get("results", []))
            
            # 处理分页
            next_url = data.get("next")
            # 如果有下一页但URL已经包含了参数，不要再附加参数
            if next_url and params:
                params = {}
            
        except requests.exceptions.RequestException as e:
            print(f"获取目的港数据失败: {e}")
            break
    
    print(f"成功获取 {len(all_results)} 个目的港数据")
    return all_results

def fetch_vessel_schedule(config: Dict[str, str]) -> Dict[str, Any]:
    """从API获取航线数据，失败时最多重试3次"""
    # 计算起始日期（当前日期减去days_back天）
    days_back = int(config.get("days_back", 2))
    start_date = (datetime.datetime.now() - datetime.timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    # 修正URL拼接方式
    url = f"https://api.trackingeyes.com/api/schedule/vesselSchedule?token={config['token']}&companyCode={config['company_id']}&orgCode=null"
    
    payload = json.dumps({
        "polCd": config['pol_cd'],
        "podCd": config['pod_cd'],
        "etd": start_date,
        "weeksOut": config['weeks_out'],
        "isTransit": config['is_transit']
    })
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    # 最大重试次数
    max_retries = 3
    retry_delay = 1  # 初始重试延迟（秒）
    
    for attempt in range(max_retries + 1):  # +1是因为第一次不算重试
        try:
            print(f"请求API，尝试 {attempt + 1}/{max_retries + 1}")
            response = requests.request("POST", url, headers=headers, data=payload)
            response.raise_for_status()  # 检查请求是否成功
            
            # 检查API返回状态码
            resp_data = response.json()
            if resp_data.get("code") == 200:
                print(f"API请求成功，状态码: {resp_data.get('code')}")
                return resp_data
            else:
                error_msg = f"API返回错误: 状态码 {resp_data.get('code')}, 消息: {resp_data.get('message', '无消息')}"
                if attempt < max_retries:
                    print(f"{error_msg}, 将在{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避策略，每次重试延迟加倍
                else:
                    print(f"最终{error_msg}, 达到最大重试次数")
                    return resp_data
                    
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                print(f"API请求失败: {e}, 将在{retry_delay}秒后重试...")
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数退避策略
            else:
                print(f"API请求失败: {e}, 达到最大重试次数")
                return {"code": 500, "message": f"API请求失败: {e}", "result": []}
    
    # 理论上不会执行到这里，但为了代码完整性
    return {"code": 500, "message": "未知错误，所有重试均失败", "result": []}

def process_routes(data, requested_pod_cd=None):
    """处理航线数据，根据规则选择最优航线"""
    # 检查API是否返回成功
    if data.get("code") != 200 or not data.get("result"):
        print(f"API返回错误或无数据: {data.get('message', '未知错误')}")
        return []

    # 1. 只过滤pod为指定pod_cd的航线
    pod_cd = requested_pod_cd or data.get("requested_pod_cd", "")  # 首选传入的pod_cd参数
    if not pod_cd:
        # 从结果中的第一条数据获取podCd
        if data["result"] and "podCd" in data["result"][0]:
            pod_cd = data["result"][0]["podCd"]
    
    filtered_routes = [route for route in data['result'] if route.get('podCd') == pod_cd]
    
    # 创建一个字典，按vessel+voyage组合键来分组存储航线
    vessel_voyage_groups = {}
    for route in filtered_routes:
        key = f"{route.get('vessel', '')}_{route.get('voyage', '')}"
        if key not in vessel_voyage_groups:
            vessel_voyage_groups[key] = []
        vessel_voyage_groups[key].append(route)
    
    # 存储最终选择的航线
    selected_routes = []
    
    # 对每组具有相同vessel+voyage的航线进行处理
    for key, routes in vessel_voyage_groups.items():
        # 2. 如果isReferenceCarrier为1且shareCabins长度为1的航线优先选择
        priority_routes = [r for r in routes if r.get('isReferenceCarrier') == '1' and len(r.get('shareCabins', [])) == 1]
        
        if priority_routes:
            # 存在符合条件的优先级航线，选择第一个即可
            selected_routes.append(priority_routes[0])
        else:
            # 3. 如果isReferenceCarrier为1但shareCabins长度不为1的航线
            reference_routes = [r for r in routes if r.get('isReferenceCarrier') == '1']
            if reference_routes:
                selected_routes.append(reference_routes[0])
    
    return selected_routes

def setup_database(config):
    """初始化数据库连接并创建表（如果不存在）"""
    try:
        # 创建数据库连接
        print(f"正在连接数据库 {config['db_host']}:{config['db_port']}...")
        conn = pymysql.connect(
            host=config['db_host'],
            port=int(config['db_port']),
            user=config['db_user'],
            password=config['db_password'],
            charset=config['db_charset']
        )
        
        cursor = conn.cursor()
        
        # 创建数据库（如果不存在）
        print(f"检查数据库 {config['db_name']} 是否存在...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{config['db_name']}` CHARACTER SET {config['db_charset']} COLLATE {config['db_charset']}_general_ci")
        
        # 选择数据库
        print(f"使用数据库 {config['db_name']}...")
        cursor.execute(f"USE `{config['db_name']}`")
        
        # 创建表
        print("检查数据表 vessel_schedule 是否存在...")
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS `vessel_schedule` (
            `id` INT AUTO_INCREMENT,
            `routeCd` VARCHAR(50) COMMENT '航线服务名称',
            `routeEtd` VARCHAR(20) COMMENT '计划离港班期（周几）',
            `carriercd` VARCHAR(20) COMMENT '船公司英文名',
            `isReferenceCarrier` VARCHAR(5) COMMENT '是否主船东（0=否，1=是）',
            `imo` VARCHAR(20) COMMENT '国际海事组织号码',
            `vessel` VARCHAR(100) NOT NULL COMMENT '船名',
            `voyage` VARCHAR(50) NOT NULL COMMENT '航次',
            `shipAgency` VARCHAR(100) COMMENT '船代',
            `polCd` VARCHAR(10) NOT NULL COMMENT '起运港五字码',
            `pol` VARCHAR(100) COMMENT '起运港英文名',
            `polTerminal` VARCHAR(100) COMMENT '起运港码头',
            `polTerminalCd` VARCHAR(20) COMMENT '起运港码头代码',
            `podCd` VARCHAR(10) NOT NULL COMMENT '目的港五字码',
            `pod` VARCHAR(100) COMMENT '目的港英文名',
            `podTerminal` VARCHAR(100) COMMENT '目的港码头',
            `podTerminalCd` VARCHAR(20) COMMENT '目的港码头代码',
            `eta` VARCHAR(30) COMMENT '计划到港日期',
            `etd` VARCHAR(30) COMMENT '计划离港日期',
            `totalDuration` VARCHAR(10) COMMENT '预计航程',
            `isTransit` VARCHAR(5) COMMENT '直航 0中转1',
            `transitPortEn` VARCHAR(100) COMMENT '中转1港口名',
            `transitPortCd` VARCHAR(10) COMMENT '中转1港口代码',
            `vesselAfterTransit` VARCHAR(100) COMMENT '中转1船名（研发中，暂不支持）',
            `voyageAfterTransit` VARCHAR(50) COMMENT '中转1航次（研发中，暂不支持）',
            `secondTransitPortEn` VARCHAR(100) COMMENT '中转2港口名',
            `secondTransitPortCd` VARCHAR(10) COMMENT '中转2港口代码',
            `secondVesselAfterTransit` VARCHAR(100) COMMENT '中转2船名（研发中，暂不支持）',
            `secondVoyageAfterTransit` VARCHAR(50) COMMENT '中转2航次（研发中，暂不支持）',
            `bookingCutoff` VARCHAR(30) COMMENT '截订舱时间',
            `cyOpen` VARCHAR(30) COMMENT '进港时间',
            `cyClose` VARCHAR(30) COMMENT '截港时间',
            `customCutoff` VARCHAR(30) COMMENT '截放行',
            `cutOff` VARCHAR(30) COMMENT '截申报',
            `siCutoff` VARCHAR(30) COMMENT '截单时间',
            `vgmCutoff` VARCHAR(30) COMMENT '截VGM时间',
            `shareCabins` TEXT COMMENT '共舱结果集',
            `fetch_timestamp` BIGINT NOT NULL COMMENT '数据抓取时间戳',
            `fetch_date` DATETIME NOT NULL COMMENT '数据抓取日期时间',
            `data_version` INT NOT NULL COMMENT '数据版本号',
            `status` TINYINT DEFAULT 1 COMMENT '数据状态：1-有效，0-无效',
            `remark` TEXT COMMENT '备注',
            `ext_field1` VARCHAR(255) COMMENT '扩展字段1',
            `ext_field2` VARCHAR(255) COMMENT '扩展字段2',
            `ext_field3` TEXT COMMENT '扩展字段3',
            PRIMARY KEY (`id`),
            UNIQUE KEY `unique_route` (`polCd`, `podCd`, `vessel`, `voyage`, `data_version`)
        ) ENGINE=InnoDB DEFAULT CHARSET=%s COMMENT='船舶航线数据';
        """
        
        # 使用参数化查询，避免字符串格式化错误
        cursor.execute(create_table_sql % config['db_charset'])
        conn.commit()
        print("数据库初始化完成")
        
        # 关闭游标但保持连接打开以供后续使用
        cursor.close()
        
        return conn
    except pymysql.MySQLError as e:
        print(f"数据库连接或初始化错误: {e}")
        raise

def get_latest_data_version(conn):
    """获取当前最新的数据版本号"""
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(data_version) FROM vessel_schedule")
    result = cursor.fetchone()
    cursor.close()
    
    if result and result[0] is not None:
        return result[0]
    return 0

def save_to_database(selected_routes, config, data_version=None):
    """将筛选出的数据保存到数据库"""
    if not selected_routes:
        print("没有筛选出数据，不写入数据库")
        return
    
    print(f"===DEBUG=== 开始存储 {len(selected_routes)} 条数据到数据库")
    print(f"===DEBUG=== 数据库配置: host={config.get('db_host')}, db={config.get('db_name')}")
    
    try:
        # 设置数据库并获取连接
        print("===DEBUG=== 正在连接数据库...")
        conn = setup_database(config)
        
        # 获取当前时间戳和格式化日期时间
        current_timestamp = int(datetime.datetime.now().timestamp())
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 获取最新的数据版本号并加1，除非外部已提供
        if data_version is None:
            print("===DEBUG=== 正在获取最新数据版本号...")
            new_data_version = get_latest_data_version(conn) + 1
            print(f"===DEBUG=== 新数据版本号: {new_data_version}")
        else:
            new_data_version = data_version
            print(f"===DEBUG=== 使用外部提供的数据版本号: {new_data_version}")
        
        cursor = conn.cursor()
        
        # 插入数据
        success_count = 0
        error_count = 0
        
        print("===DEBUG=== 开始插入数据...")
        for i, route in enumerate(selected_routes):
            try:
                # 准备SQL语句
                sql = """
                INSERT INTO vessel_schedule (
                    routeCd, routeEtd, carriercd, isReferenceCarrier, imo, vessel, voyage, shipAgency,
                    polCd, pol, polTerminal, polTerminalCd, podCd, pod, podTerminal, podTerminalCd,
                    eta, etd, totalDuration, isTransit, transitPortEn, transitPortCd,
                    vesselAfterTransit, voyageAfterTransit, secondTransitPortEn, secondTransitPortCd,
                    secondVesselAfterTransit, secondVoyageAfterTransit, bookingCutoff,
                    cyOpen, cyClose, customCutoff, cutOff, siCutoff, vgmCutoff,
                    shareCabins, fetch_timestamp, fetch_date, data_version, status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                ON DUPLICATE KEY UPDATE
                    routeCd = VALUES(routeCd),
                    routeEtd = VALUES(routeEtd),
                    carriercd = VALUES(carriercd),
                    isReferenceCarrier = VALUES(isReferenceCarrier),
                    imo = VALUES(imo),
                    shipAgency = VALUES(shipAgency),
                    pol = VALUES(pol),
                    polTerminal = VALUES(polTerminal),
                    polTerminalCd = VALUES(polTerminalCd),
                    pod = VALUES(pod),
                    podTerminal = VALUES(podTerminal),
                    podTerminalCd = VALUES(podTerminalCd),
                    eta = VALUES(eta),
                    etd = VALUES(etd),
                    totalDuration = VALUES(totalDuration),
                    isTransit = VALUES(isTransit),
                    transitPortEn = VALUES(transitPortEn),
                    transitPortCd = VALUES(transitPortCd),
                    vesselAfterTransit = VALUES(vesselAfterTransit),
                    voyageAfterTransit = VALUES(voyageAfterTransit),
                    secondTransitPortEn = VALUES(secondTransitPortEn),
                    secondTransitPortCd = VALUES(secondTransitPortCd),
                    secondVesselAfterTransit = VALUES(secondVesselAfterTransit),
                    secondVoyageAfterTransit = VALUES(secondVoyageAfterTransit),
                    bookingCutoff = VALUES(bookingCutoff),
                    cyOpen = VALUES(cyOpen),
                    cyClose = VALUES(cyClose),
                    customCutoff = VALUES(customCutoff),
                    cutOff = VALUES(cutOff),
                    siCutoff = VALUES(siCutoff),
                    vgmCutoff = VALUES(vgmCutoff),
                    shareCabins = VALUES(shareCabins),
                    fetch_timestamp = VALUES(fetch_timestamp),
                    fetch_date = VALUES(fetch_date),
                    data_version = VALUES(data_version),
                    status = VALUES(status)
                """
                
                # 准备数据
                shareCabins_json = json.dumps(route.get('shareCabins', []), ensure_ascii=False)
                
                # 参数值
                params = (
                    route.get('routeCd', ''),
                    route.get('routeEtd', ''),
                    route.get('carriercd', ''),
                    route.get('isReferenceCarrier', ''),
                    route.get('imo', ''),
                    route.get('vessel', ''),
                    route.get('voyage', ''),
                    route.get('shipAgency', ''),
                    route.get('polCd', ''),
                    route.get('pol', ''),
                    route.get('polTerminal', ''),
                    route.get('polTerminalCd', ''),
                    route.get('podCd', ''),
                    route.get('pod', ''),
                    route.get('podTerminal', ''),
                    route.get('podTerminalCd', ''),
                    route.get('eta', ''),
                    route.get('etd', ''),
                    route.get('totalDuration', ''),
                    route.get('isTransit', ''),
                    route.get('transitPortEn', ''),
                    route.get('transitPortCd', ''),
                    route.get('vesselAfterTransit', ''),
                    route.get('voyageAfterTransit', ''),
                    route.get('secondTransitPortEn', ''),
                    route.get('secondTransitPortCd', ''),
                    route.get('secondVesselAfterTransit', ''),
                    route.get('secondVoyageAfterTransit', ''),
                    route.get('bookingCutoff', ''),
                    route.get('cyOpen', ''),
                    route.get('cyClose', ''),
                    route.get('customCutoff', ''),
                    route.get('cutOff', ''),
                    route.get('siCutoff', ''),
                    route.get('vgmCutoff', ''),
                    shareCabins_json,
                    current_timestamp,
                    current_datetime,
                    new_data_version,
                    1  # status 默认为1（有效）
                )
                
                # 执行SQL
                if i % 10 == 0:
                    print(f"===DEBUG=== 正在插入第 {i+1}/{len(selected_routes)} 条数据...")
                
                cursor.execute(sql, params)
                success_count += 1
            except Exception as row_error:
                error_count += 1
                print(f"===DEBUG=== 插入第 {i+1} 条数据出错: {row_error}")
                # 继续处理下一条，不中断整个过程
                continue
        
        # 提交事务
        print("===DEBUG=== 正在提交事务...")
        conn.commit()
        print(f"成功将 {success_count} 条数据写入数据库，失败 {error_count} 条，数据版本号: {new_data_version}")
        
        # 关闭连接
        cursor.close()
        conn.close()
        print("===DEBUG=== 数据库连接已关闭")
        
    except Exception as e:
        print(f"数据库操作出错: {e}")
        print(f"===DEBUG=== 错误类型: {type(e).__name__}")
        print(f"===DEBUG=== 错误详情: {str(e)}")
        if 'conn' in locals() and conn:
            conn.close()
            print("===DEBUG=== 异常情况下数据库连接已关闭")

def save_config(config: Dict[str, str], config_file: str = "config.json") -> None:
    """保存配置到文件"""
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"配置已保存到 {config_file}")

def save_data(data: Dict[str, Any], data_file: str = "vessel_data.json") -> None:
    """保存API返回的数据到文件"""
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"API返回数据已保存到 {data_file}")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='航线数据查询和处理工具')
    parser.add_argument('--token', help='API访问令牌')
    parser.add_argument('--company_id', help='公司ID')
    parser.add_argument('--days_back', type=int, help='从当前日期往前多少天开始查询')
    parser.add_argument('--pol_cd', help='起始港代码')
    parser.add_argument('--pod_cd', help='目的港代码')
    parser.add_argument('--weeks_out', help='往后查询多少周')
    parser.add_argument('--is_transit', help='是否包含中转')
    parser.add_argument('--save_config', action='store_true', help='保存当前配置到config.json')
    parser.add_argument('--use_test_data', action='store_true', help='使用测试数据而不是API请求')
    parser.add_argument('--skip_db', action='store_true', help='跳过数据库存储')
    parser.add_argument('--api_base_url', default='http://localhost:8000/api', help='API基础URL')
    parser.add_argument('--use_port_api', action='store_true', help='使用API获取起运港和目的港数据')
    parser.add_argument('--pol_filter_code', help='起运港代码过滤条件')
    parser.add_argument('--pol_filter_name', help='起运港名称过滤条件')
    parser.add_argument('--pod_filter_code', help='目的港代码过滤条件')  
    parser.add_argument('--pod_filter_name', help='目的港名称过滤条件')
    parser.add_argument('--config_file', default='config.json', help='配置文件路径 (默认: config.json, Docker环境可用: config.docker.json)')
    parser.add_argument('--env', choices=['local', 'docker', 'container'], help='运行环境 (local=本地, docker=Docker外部, container=容器内部)')
    return parser.parse_args()

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 根据环境选择配置文件
    config_file = args.config_file
    if args.env:
        if args.env == 'docker':
            config_file = 'config.docker.json'
        elif args.env == 'container':
            config_file = 'config.container.json'
        elif args.env == 'local':
            config_file = 'config.json'
    
    # 加载配置
    config = load_config(config_file)
    
    # 用命令行参数更新配置
    for key, value in vars(args).items():
        if value is not None and key in config:
            config[key] = str(value)
    
    # 如果需要，保存配置
    if args.save_config:
        save_config(config)
    
    # 判断是否使用API获取港口数据
    if args.use_port_api:
        # 获取起运港和目的港数据
        pol_ports = fetch_loading_ports(
            base_url=args.api_base_url, 
            code=args.pol_filter_code, 
            name=args.pol_filter_name
        )
        pod_ports = fetch_discharge_ports(
            base_url=args.api_base_url, 
            code=args.pod_filter_code, 
            name=args.pod_filter_name
        )
        
        if not pol_ports:
            print("没有找到符合条件的起运港，退出程序")
            return
        
        if not pod_ports:
            print("没有找到符合条件的目的港，退出程序")
            return
        
        # 【调试】仅选择少量港口进行测试
        # pol_ports = pol_ports[:1]  # 只取第一个起运港
        # pod_ports = pod_ports[:3]  # 只取前三个目的港
        
        all_selected_routes = []
        processed_count = 0
        total_combinations = len(pol_ports) * len(pod_ports)
        
        print(f"共找到 {len(pol_ports)} 个起运港和 {len(pod_ports)} 个目的港，总计 {total_combinations} 个组合")
        
        # 如果需要保存到数据库，获取最新的数据版本号并加1
        if not args.skip_db:
            try:
                print("初始化数据库连接...")
                conn = setup_database(config)
                new_data_version = get_latest_data_version(conn) + 1
                print(f"本次数据版本号: {new_data_version}")
                conn.close()
            except Exception as e:
                print(f"初始化数据库失败: {e}")
                return
        else:
            new_data_version = 0
        
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
                
                # 获取数据
                if args.use_test_data:
                    try:
                        with open('test.json', 'r') as file:
                            data = json.load(file)
                        print("使用测试数据")
                    except FileNotFoundError:
                        print("测试数据文件test.json不存在，改用API请求")
                        data = fetch_vessel_schedule(current_config)
                else:
                    # 从API获取数据
                    data = fetch_vessel_schedule(current_config)
                
                # 处理数据
                selected_routes = process_routes(data, pod_cd)
                
                # 添加到总结果列表
                if selected_routes:
                    all_selected_routes.extend(selected_routes)
                    
                    # 打印结果
                    print(f"该组合选择了 {len(selected_routes)} 条航线")
                    
                    # 立即保存到数据库
                    if not args.skip_db:
                        try:
                            print(f"正在将该组合的 {len(selected_routes)} 条航线保存到数据库...")
                            save_to_database(selected_routes, config, new_data_version)
                            print("该组合数据已保存到数据库")
                        except Exception as e:
                            print(f"保存该组合数据失败: {e}")
                else:
                    print("该组合未找到符合条件的航线")
                
                # 避免API请求过于频繁
                if processed_count < total_combinations:
                    print("休息1秒后继续...")
                    time.sleep(1)
        
        # 保存最后一次请求的数据（调试用）
        save_data(data)
        
        # 打印总结果
        print(f"\n所有组合共选择了 {len(all_selected_routes)} 条航线:")
        for route in all_selected_routes[:10]:  # 只显示前10条，避免输出过多
            print(f"起运港: {route.get('pol', 'N/A')} ({route.get('polCd', 'N/A')}), "
                  f"目的港: {route.get('pod', 'N/A')} ({route.get('podCd', 'N/A')}), "
                  f"船名: {route.get('vessel', 'N/A')}, "
                  f"航次: {route.get('voyage', 'N/A')}")
        
        if len(all_selected_routes) > 10:
            print(f"...以及其他 {len(all_selected_routes) - 10} 条数据")
    
    else:
        # 原有的单一港口组合查询逻辑
        # 获取数据
        if args.use_test_data:
            try:
                with open('test.json', 'r') as file:
                    data = json.load(file)
                print("使用测试数据")
            except FileNotFoundError:
                print("测试数据文件test.json不存在，改用API请求")
                data = fetch_vessel_schedule(config)
                save_data(data)
        else:
            # 从API获取数据
            data = fetch_vessel_schedule(config)
            save_data(data)
        
        # 处理数据
        selected_routes = process_routes(data)
        
        # 打印结果
        print(f"共选择了 {len(selected_routes)} 条航线:")
        for route in selected_routes:
            print(f"船名: {route.get('vessel', 'N/A')}, "
                f"航次: {route.get('voyage', 'N/A')}, "
                f"承运人: {route.get('carriercd', 'N/A')}, "
                f"航线代码: {route.get('routeCd', 'N/A')}, "
                f"isReferenceCarrier: {route.get('isReferenceCarrier', 'N/A')}, "
                f"shareCabins长度: {len(route.get('shareCabins', []))}")
        
        # 将数据存入数据库
        if not args.skip_db:
            save_to_database(selected_routes, config)

if __name__ == "__main__":
    main()