#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
压力测试
"""

import unittest
import time
import threading
import json
from backend.app import create_app


class StressTest(unittest.TestCase):
    """压力测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_concurrent_requests(self):
        """测试并发请求"""
        def make_request(client, results, index):
            """发送单个请求"""
            start_time = time.time()
            try:
                response = client.post('/api/chat',
                                     json={
                                         'text': f'并发测试请求 {index}',
                                         'user_id': f'concurrent_user_{index}'
                                     })
                end_time = time.time()
                results[index] = {
                    'status_code': response.status_code,
                    'response_time': end_time - start_time,
                    'success': response.status_code == 200
                }
            except Exception as e:
                end_time = time.time()
                results[index] = {
                    'status_code': 500,
                    'response_time': end_time - start_time,
                    'success': False,
                    'error': str(e)
                }
        
        # 并发请求数
        num_requests = 50
        threads = []
        results = [None] * num_requests
        
        # 创建并发线程
        for i in range(num_requests):
            thread = threading.Thread(target=make_request, 
                                    args=(self.client, results, i))
            threads.append(thread)
        
        # 记录开始时间
        test_start_time = time.time()
        
        # 启动所有线程
        for thread in threads:
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 记录结束时间
        test_end_time = time.time()
        
        # 分析结果
        successful_requests = sum(1 for r in results if r and r['success'])
        total_response_time = sum(r['response_time'] for r in results if r)
        average_response_time = total_response_time / num_requests if num_requests > 0 else 0
        
        # 输出测试结果
        print(f"\n=== 并发请求测试结果 ===")
        print(f"总请求数: {num_requests}")
        print(f"成功请求数: {successful_requests}")
        print(f"成功率: {successful_requests/num_requests*100:.2f}%")
        print(f"总测试时间: {test_end_time - test_start_time:.2f}秒")
        print(f"平均响应时间: {average_response_time:.4f}秒")
        
        # 断言检查
        self.assertGreater(successful_requests, num_requests * 0.8)  # 成功率至少80%
        self.assertLess(average_response_time, 5.0)  # 平均响应时间小于5秒
    
    def test_high_load_chat_requests(self):
        """测试高负载聊天请求"""
        # 发送大量连续请求
        num_requests = 100
        successful_count = 0
        total_time = 0
        
        for i in range(num_requests):
            start_time = time.time()
            try:
                response = self.client.post('/api/chat',
                                          json={
                                              'text': f'高负载测试请求 {i}',
                                              'user_id': 'high_load_user'
                                          })
                
                if response.status_code == 200:
                    successful_count += 1
                
                end_time = time.time()
                total_time += (end_time - start_time)
                
            except Exception as e:
                print(f"请求 {i} 失败: {e}")
                end_time = time.time()
                total_time += (end_time - start_time)
        
        average_time = total_time / num_requests if num_requests > 0 else 0
        
        # 输出结果
        print(f"\n=== 高负载测试结果 ===")
        print(f"总请求数: {num_requests}")
        print(f"成功请求数: {successful_count}")
        print(f"成功率: {successful_count/num_requests*100:.2f}%")
        print(f"平均响应时间: {average_time:.4f}秒")
        
        # 断言检查
        self.assertGreater(successful_count, num_requests * 0.9)  # 成功率至少90%
    
    def test_database_concurrent_access(self):
        """测试数据库并发访问"""
        def get_stats(results, index):
            """获取统计信息"""
            start_time = time.time()
            try:
                response = self.client.get('/api/stats')
                end_time = time.time()
                results[index] = {
                    'status_code': response.status_code,
                    'response_time': end_time - start_time,
                    'success': response.status_code == 200
                }
            except Exception as e:
                end_time = time.time()
                results[index] = {
                    'status_code': 500,
                    'response_time': end_time - start_time,
                    'success': False,
                    'error': str(e)
                }
        
        # 并发获取统计信息
        num_requests = 30
        threads = []
        results = [None] * num_requests
        
        # 创建并发线程
        for i in range(num_requests):
            thread = threading.Thread(target=get_stats, args=(results, i))
            threads.append(thread)
        
        # 启动所有线程
        for thread in threads:
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 分析结果
        successful_requests = sum(1 for r in results if r and r['success'])
        total_response_time = sum(r['response_time'] for r in results if r)
        average_response_time = total_response_time / num_requests if num_requests > 0 else 0
        
        # 输出测试结果
        print(f"\n=== 数据库并发访问测试结果 ===")
        print(f"总请求数: {num_requests}")
        print(f"成功请求数: {successful_requests}")
        print(f"成功率: {successful_requests/num_requests*100:.2f}%")
        print(f"平均响应时间: {average_response_time:.4f}秒")
        
        # 断言检查
        self.assertGreater(successful_requests, num_requests * 0.8)  # 成功率至少80%


if __name__ == '__main__':
    unittest.main(verbosity=2)