#!/usr/bin/env python
"""
测试运行脚本
提供多种测试运行方式和选项
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path


def setup_environment():
    """设置测试环境"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ship_schedule.settings')

    # 添加项目根目录到Python路径
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))


def run_django_tests(test_labels=None, verbosity=2, keepdb=False, parallel=False):
    """运行Django测试"""
    cmd = ['python3', 'manage.py', 'test']

    if test_labels:
        cmd.extend(test_labels)

    cmd.extend([f'--verbosity={verbosity}', '--settings=ship_schedule.test_settings'])

    if keepdb:
        cmd.append('--keepdb')

    if parallel:
        cmd.extend(['--parallel', 'auto'])

    print(f"运行命令: {' '.join(cmd)}")
    return subprocess.run(cmd).returncode


def run_pytest_tests(test_path=None, coverage=False, html_report=False, markers=None):
    """运行pytest测试"""
    cmd = ['pytest']

    if test_path:
        cmd.append(test_path)
    else:
        cmd.append('tests/')

    if coverage:
        cmd.extend(['--cov=.', '--cov-report=term-missing'])
        if html_report:
            cmd.append('--cov-report=html')

    if markers:
        cmd.extend(['-m', markers])

    print(f"运行命令: {' '.join(cmd)}")
    return subprocess.run(cmd).returncode


def run_specific_test_suite(suite):
    """运行特定测试套件"""
    test_suites = {
        'models': 'tests.test_models',
        'auth': 'tests.test_authentication_api',
        'schedules': 'tests.test_schedules_api',
        'local_fees': 'tests.test_local_fees_api',
        'permissions': 'tests.test_permissions',
        'performance': 'tests.test_performance',
        'integration': 'tests.test_integration',
    }

    if suite not in test_suites:
        print(f"未知的测试套件: {suite}")
        print(f"可用的测试套件: {', '.join(test_suites.keys())}")
        return 1

    return run_django_tests([test_suites[suite]])


def run_coverage_report():
    """运行覆盖率测试并生成报告"""
    print("运行覆盖率测试...")

    # 运行测试并收集覆盖率
    cmd = [
        'coverage', 'run', '--source=.',
        'manage.py', 'test'
    ]

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("测试失败，无法生成覆盖率报告")
        return result.returncode

    # 生成控制台报告
    print("\n" + "="*70)
    print("覆盖率报告:")
    print("="*70)
    subprocess.run(['coverage', 'report'])

    # 生成HTML报告
    subprocess.run(['coverage', 'html'])
    print("\nHTML覆盖率报告已生成到 htmlcov/ 目录")

    return 0


def run_performance_tests():
    """运行性能测试"""
    print("运行性能测试...")
    return run_django_tests(['tests.test_performance'], verbosity=2)


def run_integration_tests():
    """运行集成测试"""
    print("运行集成测试...")
    return run_django_tests(['tests.test_integration'], verbosity=2)


def run_all_tests_with_report():
    """运行所有测试并生成详细报告"""
    print("运行完整测试套件...")

    # 测试套件列表
    test_suites = [
        ('模型测试', 'tests.test_models'),
        ('认证API测试', 'tests.test_authentication_api'),
        ('船期API测试', 'tests.test_schedules_api'),
        ('本地费用API测试', 'tests.test_local_fees_api'),
        ('权限系统测试', 'tests.test_permissions'),
        ('集成测试', 'tests.test_integration'),
    ]

    results = {}

    for suite_name, suite_path in test_suites:
        print(f"\n{'='*50}")
        print(f"运行 {suite_name}")
        print('='*50)

        result = run_django_tests([suite_path], verbosity=1)
        results[suite_name] = result

    # 打印总结报告
    print(f"\n{'='*70}")
    print("测试结果总结:")
    print('='*70)

    total_passed = 0
    total_failed = 0

    for suite_name, result in results.items():
        status = "✅ 通过" if result == 0 else "❌ 失败"
        print(f"{suite_name:<20} {status}")

        if result == 0:
            total_passed += 1
        else:
            total_failed += 1

    print(f"\n总计: {total_passed} 个套件通过, {total_failed} 个套件失败")

    return 0 if total_failed == 0 else 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='船舶航线管理系统测试运行器')

    parser.add_argument(
        'command',
        choices=[
            'all', 'models', 'auth', 'schedules', 'local_fees',
            'permissions', 'performance', 'integration', 'coverage',
            'pytest', 'report'
        ],
        help='要运行的测试类型'
    )

    parser.add_argument(
        '--keepdb',
        action='store_true',
        help='保留测试数据库'
    )

    parser.add_argument(
        '--parallel',
        action='store_true',
        help='并行运行测试'
    )

    parser.add_argument(
        '--verbosity',
        type=int,
        default=2,
        choices=[0, 1, 2, 3],
        help='输出详细程度'
    )

    parser.add_argument(
        '--path',
        type=str,
        help='指定测试路径'
    )

    parser.add_argument(
        '--markers',
        type=str,
        help='pytest标记过滤器'
    )

    args = parser.parse_args()

    # 设置环境
    setup_environment()

    # 根据命令运行相应的测试
    if args.command == 'all':
        return run_django_tests(
            verbosity=args.verbosity,
            keepdb=args.keepdb,
            parallel=args.parallel
        )
    elif args.command == 'coverage':
        return run_coverage_report()
    elif args.command == 'performance':
        return run_performance_tests()
    elif args.command == 'integration':
        return run_integration_tests()
    elif args.command == 'pytest':
        return run_pytest_tests(
            test_path=args.path,
            coverage=True,
            html_report=True,
            markers=args.markers
        )
    elif args.command == 'report':
        return run_all_tests_with_report()
    else:
        return run_specific_test_suite(args.command)


if __name__ == '__main__':
    sys.exit(main())
