"""
性能测试用例
测试系统在大数据量和高并发情况下的性能表现
"""
import time
import threading
from decimal import Decimal
from django.test import TestCase, TransactionTestCase
from django.test.utils import override_settings
from django.db import connection
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from authentication.models import Permission, Role
from schedules.models import VesselSchedule, VesselInfoFromCompany
from local_fees.models import LocalFee

User = get_user_model()


class DatabasePerformanceTest(TestCase):
    """数据库性能测试"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_bulk_create_vessel_schedules(self):
        """测试批量创建船舶航线性能"""
        schedules = []
        start_time = time.time()
        
        # 准备1000条数据
        for i in range(1000):
            schedules.append(VesselSchedule(
                polCd='CNSHA',
                podCd='USNYC',
                vessel=f'VESSEL_{i}',
                voyage=f'V{i:04d}',
                data_version=20250527,
                carriercd='TEST',
                fetch_timestamp=1716825600,
                fetch_date=timezone.now(),
                status=1
            ))
        
        # 批量创建
        VesselSchedule.objects.bulk_create(schedules)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # 验证数据已创建
        self.assertEqual(VesselSchedule.objects.count(), 1000)
        
        # 性能断言：批量创建1000条记录应在5秒内完成
        self.assertLess(creation_time, 5.0, f"批量创建耗时 {creation_time:.2f} 秒，超过预期")
        
        print(f"批量创建1000条船舶航线记录耗时: {creation_time:.2f} 秒")
    
    def test_query_performance_with_large_dataset(self):
        """测试大数据集查询性能"""
        # 创建大量测试数据
        schedules = []
        for i in range(5000):
            schedules.append(VesselSchedule(
                polCd=f'CN{i%10:03d}',
                podCd=f'US{i%10:03d}',
                vessel=f'VESSEL_{i}',
                voyage=f'V{i:04d}',
                data_version=20250527,
                carriercd=f'CARRIER_{i%5}',
                fetch_timestamp=1716825600,
                fetch_date=timezone.now(),
                status=1
            ))
        
        VesselSchedule.objects.bulk_create(schedules)
        
        # 测试查询性能
        start_time = time.time()
        
        # 执行复杂查询
        results = VesselSchedule.objects.filter(
            polCd__startswith='CN',
            status=1,
            data_version=20250527
        ).order_by('-fetch_date')[:100]
        
        # 强制执行查询
        list(results)
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # 性能断言：查询应在1秒内完成
        self.assertLess(query_time, 1.0, f"查询耗时 {query_time:.2f} 秒，超过预期")
        
        print(f"大数据集查询耗时: {query_time:.2f} 秒")
    
    def test_database_query_count(self):
        """测试数据库查询次数优化"""
        # 创建测试数据
        for i in range(10):
            VesselSchedule.objects.create(
                polCd='CNSHA',
                podCd='USNYC',
                vessel=f'VESSEL_{i}',
                voyage=f'V{i:03d}',
                data_version=20250527,
                carriercd='TEST',
                fetch_timestamp=1716825600,
                fetch_date=timezone.now(),
                status=1
            )
        
        # 测试查询次数
        with self.assertNumQueries(1):
            # 应该只执行一次数据库查询
            schedules = list(VesselSchedule.objects.filter(polCd='CNSHA'))
            self.assertEqual(len(schedules), 10)
    
    def test_index_performance(self):
        """测试数据库索引性能"""
        # 创建大量数据
        schedules = []
        for i in range(10000):
            schedules.append(VesselSchedule(
                polCd=f'CN{i%100:03d}',
                podCd=f'US{i%100:03d}',
                vessel=f'VESSEL_{i}',
                voyage=f'V{i:05d}',
                data_version=20250527,
                carriercd=f'CARRIER_{i%10}',
                fetch_timestamp=1716825600,
                fetch_date=timezone.now(),
                status=1
            ))
        
        VesselSchedule.objects.bulk_create(schedules)
        
        # 测试索引字段查询性能
        start_time = time.time()
        
        results = VesselSchedule.objects.filter(
            polCd='CN001',
            podCd='US001',
            data_version=20250527
        )
        list(results)
        
        end_time = time.time()
        indexed_query_time = end_time - start_time
        
        # 测试非索引字段查询性能
        start_time = time.time()
        
        results = VesselSchedule.objects.filter(
            vessel__contains='VESSEL_1'
        )
        list(results)
        
        end_time = time.time()
        non_indexed_query_time = end_time - start_time
        
        print(f"索引字段查询耗时: {indexed_query_time:.3f} 秒")
        print(f"非索引字段查询耗时: {non_indexed_query_time:.3f} 秒")
        
        # 索引查询应该更快
        self.assertLess(indexed_query_time, 0.1, "索引查询性能不佳")


class APIPerformanceTest(APITestCase):
    """API性能测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = APIClient()
        
        # 创建测试用户和权限
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建权限
        permission = Permission.objects.create(
            code='vessel_schedule.list',
            name='船期列表查看',
            category='船期管理'
        )
        
        role = Role.objects.create(
            name='测试角色',
            description='测试角色'
        )
        role.permissions.add(permission)
        self.user.roles.add(role)
        
        # 创建大量测试数据
        schedules = []
        for i in range(1000):
            schedules.append(VesselSchedule(
                polCd=f'CN{i%10:03d}',
                podCd=f'US{i%10:03d}',
                vessel=f'VESSEL_{i}',
                voyage=f'V{i:04d}',
                data_version=20250527,
                carriercd=f'CARRIER_{i%5}',
                fetch_timestamp=1716825600,
                fetch_date=timezone.now(),
                status=1
            ))
        
        VesselSchedule.objects.bulk_create(schedules)
    
    def test_api_response_time(self):
        """测试API响应时间"""
        self.client.force_authenticate(user=self.user)
        
        start_time = time.time()
        
        response = self.client.get('/api/schedules/')
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # API响应时间应在2秒内
        self.assertLess(response_time, 2.0, f"API响应时间 {response_time:.2f} 秒，超过预期")
        
        print(f"API响应时间: {response_time:.3f} 秒")
    
    def test_pagination_performance(self):
        """测试分页性能"""
        self.client.force_authenticate(user=self.user)
        
        # 测试不同页面大小的性能
        page_sizes = [10, 50, 100, 200]
        
        for page_size in page_sizes:
            start_time = time.time()
            
            response = self.client.get(f'/api/schedules/?page_size={page_size}')
            
            end_time = time.time()
            response_time = end_time - start_time
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['results']), page_size)
            
            print(f"页面大小 {page_size} 的响应时间: {response_time:.3f} 秒")
            
            # 响应时间应随页面大小线性增长，但不应超过合理范围
            self.assertLess(response_time, 3.0, f"页面大小 {page_size} 响应时间过长")
    
    def test_filter_performance(self):
        """测试过滤查询性能"""
        self.client.force_authenticate(user=self.user)
        
        # 测试不同过滤条件的性能
        filters = [
            {'polCd': 'CN001'},
            {'carriercd': 'CARRIER_1'},
            {'polCd': 'CN001', 'podCd': 'US001'},
            {'search': 'VESSEL_1'},
        ]
        
        for filter_params in filters:
            start_time = time.time()
            
            response = self.client.get('/api/schedules/', filter_params)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
            print(f"过滤条件 {filter_params} 的响应时间: {response_time:.3f} 秒")
            
            # 过滤查询应在1秒内完成
            self.assertLess(response_time, 1.0, f"过滤查询响应时间过长: {response_time:.3f} 秒")
    
    def test_concurrent_api_requests(self):
        """测试并发API请求性能"""
        self.client.force_authenticate(user=self.user)
        
        results = []
        errors = []
        
        def make_request():
            try:
                start_time = time.time()
                response = self.client.get('/api/schedules/?page_size=20')
                end_time = time.time()
                
                results.append({
                    'status_code': response.status_code,
                    'response_time': end_time - start_time
                })
            except Exception as e:
                errors.append(str(e))
        
        # 创建10个并发请求
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # 启动所有线程
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证结果
        self.assertEqual(len(errors), 0, f"并发请求出现错误: {errors}")
        self.assertEqual(len(results), 10, "并发请求数量不正确")
        
        # 所有请求都应该成功
        for result in results:
            self.assertEqual(result['status_code'], 200)
        
        # 计算平均响应时间
        avg_response_time = sum(r['response_time'] for r in results) / len(results)
        
        print(f"10个并发请求总耗时: {total_time:.3f} 秒")
        print(f"平均响应时间: {avg_response_time:.3f} 秒")
        
        # 并发请求的平均响应时间应在合理范围内
        self.assertLess(avg_response_time, 2.0, f"并发请求平均响应时间过长: {avg_response_time:.3f} 秒")


class MemoryPerformanceTest(TestCase):
    """内存性能测试"""
    
    def test_large_dataset_memory_usage(self):
        """测试大数据集内存使用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建大量数据
        schedules = []
        for i in range(10000):
            schedules.append(VesselSchedule(
                polCd=f'CN{i%100:03d}',
                podCd=f'US{i%100:03d}',
                vessel=f'VESSEL_{i}',
                voyage=f'V{i:05d}',
                data_version=20250527,
                carriercd=f'CARRIER_{i%10}',
                fetch_timestamp=1716825600,
                fetch_date=timezone.now(),
                status=1
            ))
        
        VesselSchedule.objects.bulk_create(schedules)
        
        # 查询大量数据
        results = list(VesselSchedule.objects.all())
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"初始内存使用: {initial_memory:.2f} MB")
        print(f"最终内存使用: {final_memory:.2f} MB")
        print(f"内存增长: {memory_increase:.2f} MB")
        
        # 内存增长应在合理范围内（小于500MB）
        self.assertLess(memory_increase, 500, f"内存使用增长过多: {memory_increase:.2f} MB")
        
        # 验证数据正确性
        self.assertEqual(len(results), 10000)
    
    def test_queryset_iterator_memory_efficiency(self):
        """测试查询集迭代器内存效率"""
        import psutil
        import os
        
        # 创建大量数据
        schedules = []
        for i in range(5000):
            schedules.append(VesselSchedule(
                polCd='CNSHA',
                podCd='USNYC',
                vessel=f'VESSEL_{i}',
                voyage=f'V{i:04d}',
                data_version=20250527,
                carriercd='TEST',
                fetch_timestamp=1716825600,
                fetch_date=timezone.now(),
                status=1
            ))
        
        VesselSchedule.objects.bulk_create(schedules)
        
        process = psutil.Process(os.getpid())
        
        # 测试普通查询的内存使用
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        results_list = list(VesselSchedule.objects.all())
        
        list_memory = process.memory_info().rss / 1024 / 1024
        list_memory_increase = list_memory - initial_memory
        
        # 清理内存
        del results_list
        
        # 测试迭代器查询的内存使用
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        count = 0
        for schedule in VesselSchedule.objects.iterator(chunk_size=100):
            count += 1
        
        iterator_memory = process.memory_info().rss / 1024 / 1024
        iterator_memory_increase = iterator_memory - initial_memory
        
        print(f"普通查询内存增长: {list_memory_increase:.2f} MB")
        print(f"迭代器查询内存增长: {iterator_memory_increase:.2f} MB")
        
        # 迭代器应该使用更少的内存
        self.assertLess(iterator_memory_increase, list_memory_increase, 
                       "迭代器查询应该使用更少的内存")
        
        # 验证数据正确性
        self.assertEqual(count, 5000)


class CachePerformanceTest(TestCase):
    """缓存性能测试"""
    
    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'test-cache',
        }
    })
    def test_cache_performance(self):
        """测试缓存性能"""
        from django.core.cache import cache
        
        # 创建测试数据
        schedules = []
        for i in range(1000):
            schedules.append(VesselSchedule(
                polCd='CNSHA',
                podCd='USNYC',
                vessel=f'VESSEL_{i}',
                voyage=f'V{i:04d}',
                data_version=20250527,
                carriercd='TEST',
                fetch_timestamp=1716825600,
                fetch_date=timezone.now(),
                status=1
            ))
        
        VesselSchedule.objects.bulk_create(schedules)
        
        cache_key = 'test_schedules'
        
        # 测试无缓存查询时间
        start_time = time.time()
        
        schedules_data = list(VesselSchedule.objects.filter(polCd='CNSHA').values())
        
        no_cache_time = time.time() - start_time
        
        # 设置缓存
        cache.set(cache_key, schedules_data, 300)
        
        # 测试有缓存查询时间
        start_time = time.time()
        
        cached_data = cache.get(cache_key)
        
        cache_time = time.time() - start_time
        
        print(f"无缓存查询时间: {no_cache_time:.4f} 秒")
        print(f"缓存查询时间: {cache_time:.4f} 秒")
        print(f"性能提升: {no_cache_time / cache_time:.2f} 倍")
        
        # 缓存查询应该显著更快
        self.assertLess(cache_time, no_cache_time / 10, "缓存性能提升不明显")
        
        # 验证数据一致性
        self.assertEqual(len(cached_data), len(schedules_data))


class LoadTestCase(TransactionTestCase):
    """负载测试"""
    
    def test_high_volume_data_processing(self):
        """测试高容量数据处理"""
        start_time = time.time()
        
        # 模拟大批量数据导入
        batch_size = 1000
        total_records = 10000
        
        for batch_start in range(0, total_records, batch_size):
            schedules = []
            for i in range(batch_start, min(batch_start + batch_size, total_records)):
                schedules.append(VesselSchedule(
                    polCd=f'CN{i%100:03d}',
                    podCd=f'US{i%100:03d}',
                    vessel=f'VESSEL_{i}',
                    voyage=f'V{i:05d}',
                    data_version=20250527,
                    carriercd=f'CARRIER_{i%20}',
                    fetch_timestamp=1716825600,
                    fetch_date=timezone.now(),
                    status=1
                ))
            
            VesselSchedule.objects.bulk_create(schedules)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 验证数据完整性
        total_count = VesselSchedule.objects.count()
        self.assertEqual(total_count, total_records)
        
        print(f"处理 {total_records} 条记录耗时: {processing_time:.2f} 秒")
        print(f"平均处理速度: {total_records / processing_time:.0f} 记录/秒")
        
        # 处理速度应该达到合理水平（至少1000记录/秒）
        records_per_second = total_records / processing_time
        self.assertGreater(records_per_second, 1000, 
                          f"数据处理速度过慢: {records_per_second:.0f} 记录/秒")
