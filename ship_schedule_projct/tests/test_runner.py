"""
自定义测试运行器
提供测试运行的配置和工具
"""
import os
import sys
import time
from django.test.runner import DiscoverRunner
from django.conf import settings
from django.core.management import execute_from_command_line


class CustomTestRunner(DiscoverRunner):
    """自定义测试运行器"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_time = None
        self.end_time = None
    
    def setup_test_environment(self, **kwargs):
        """设置测试环境"""
        super().setup_test_environment(**kwargs)
        
        # 设置测试专用配置
        settings.DEBUG = False
        settings.TESTING = True
        
        # 禁用不必要的中间件
        settings.MIDDLEWARE = [
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'corsheaders.middleware.CorsMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ]
        
        # 配置测试数据库
        settings.DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
        
        # 配置测试缓存
        settings.CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'test-cache',
            }
        }
        
        print("测试环境设置完成")
    
    def run_tests(self, test_labels, **kwargs):
        """运行测试"""
        self.start_time = time.time()
        
        print(f"开始运行测试: {test_labels or '所有测试'}")
        print("=" * 70)
        
        result = super().run_tests(test_labels, **kwargs)
        
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        print("=" * 70)
        print(f"测试完成，总耗时: {duration:.2f} 秒")
        
        if result == 0:
            print("✅ 所有测试通过")
        else:
            print(f"❌ {result} 个测试失败")
        
        return result
    
    def teardown_test_environment(self, **kwargs):
        """清理测试环境"""
        super().teardown_test_environment(**kwargs)
        print("测试环境清理完成")


def run_all_tests():
    """运行所有测试"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ship_schedule.settings')
    
    # 设置测试运行器
    settings.TEST_RUNNER = 'tests.test_runner.CustomTestRunner'
    
    # 运行测试
    execute_from_command_line(['manage.py', 'test'])


def run_specific_tests(test_labels):
    """运行特定测试"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ship_schedule.settings')
    
    # 设置测试运行器
    settings.TEST_RUNNER = 'tests.test_runner.CustomTestRunner'
    
    # 构建命令
    cmd = ['manage.py', 'test'] + test_labels
    
    # 运行测试
    execute_from_command_line(cmd)


def run_tests_with_coverage():
    """运行测试并生成覆盖率报告"""
    try:
        import coverage
    except ImportError:
        print("请先安装coverage: pip install coverage")
        return
    
    # 启动覆盖率收集
    cov = coverage.Coverage()
    cov.start()
    
    try:
        # 运行测试
        run_all_tests()
    finally:
        # 停止覆盖率收集
        cov.stop()
        cov.save()
        
        # 生成报告
        print("\n" + "=" * 70)
        print("覆盖率报告:")
        print("=" * 70)
        cov.report()
        
        # 生成HTML报告
        cov.html_report(directory='htmlcov')
        print("\nHTML覆盖率报告已生成到 htmlcov/ 目录")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--coverage':
            run_tests_with_coverage()
        else:
            run_specific_tests(sys.argv[1:])
    else:
        run_all_tests()
