#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
延迟测试
"""

import unittest
import time
import statistics
import json
from backend.app import create_app


class LatencyTest(unittest.TestCase):
    """延迟测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_api_response_time(self):
        """测试API响应时间"""
        # 测试健康检查接口
        response_times = []
        num_requests = 70  # 进行70次请求，去掉前20次作为预热
        
        for i in range(num_requests):
            start_time = time.time()
            response = self.client.get('/api/health')
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            response_times.append(response_time)
        
        # 去掉前20次预热请求
        test_times = response_times[20:]
        
        # 计算统计信息
        avg_time = statistics.mean(test_times)
        median_time = statistics.median(test_times)
        min_time = min(test_times)
        max_time = max(test_times)
        percentile_95 = statistics.quantiles(test_times, n=20)[-1]  # 95%分位数
        
        # 输出结果
        print(f"\n=== API响应时间测试结果 ===")
        print(f"测试请求数: {len(test_times)}")
        print(f"平均响应时间: {avg_time:.2f}ms")
        print(f"中位数响应时间: {median_time:.2f}ms")
        print(f"最小响应时间: {min_time:.2f}ms")
        print(f"最大响应时间: {max_time:.2f}ms")
        print(f"95%分位数响应时间: {percentile_95:.2f}ms")
        
        # 断言检查
        self.assertLess(avg_time, 100)  # 平均响应时间小于100ms
        self.assertLess(percentile_95, 200)  # 95%请求响应时间小于200ms
    
    def test_chat_endpoint_latency(self):
        """测试聊天接口延迟"""
        response_times = []
        num_requests = 50
        
        for i in range(num_requests):
            start_time = time.time()
            response = self.client.post('/api/chat',
                                      json={
                                          'text': f'延迟测试请求 {i}',
                                          'user_id': 'latency_test_user'
                                      })
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            response_times.append(response_time)
        
        # 计算统计信息
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        percentile_95 = statistics.quantiles(response_times, n=20)[-1]  # 95%分位数
        
        # 输出结果
        print(f"\n=== 聊天接口延迟测试结果 ===")
        print(f"测试请求数: {num_requests}")
        print(f"平均响应时间: {avg_time:.2f}ms")
        print(f"中位数响应时间: {median_time:.2f}ms")
        print(f"最小响应时间: {min_time:.2f}ms")
        print(f"最大响应时间: {max_time:.2f}ms")
        print(f"95%分位数响应时间: {percentile_95:.2f}ms")
        
        # 断言检查
        self.assertLess(avg_time, 1000)  # 平均响应时间小于1000ms
        self.assertLess(percentile_95, 2000)  # 95%请求响应时间小于2000ms
    
    def test_database_query_performance(self):
        """测试数据库查询性能"""
        # 测试统计接口（涉及数据库查询）
        response_times = []
        num_requests = 30
        
        for i in range(num_requests):
            start_time = time.time()
            response = self.client.get('/api/stats')
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            response_times.append(response_time)
        
        # 计算统计信息
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        percentile_95 = statistics.quantiles(response_times, n=20)[-1]  # 95%分位数
        
        # 输出结果
        print(f"\n=== 数据库查询性能测试结果 ===")
        print(f"测试请求数: {num_requests}")
        print(f"平均响应时间: {avg_time:.2f}ms")
        print(f"中位数响应时间: {median_time:.2f}ms")
        print(f"95%分位数响应时间: {percentile_95:.2f}ms")
        
        # 断言检查
        self.assertLess(avg_time, 500)  # 平均响应时间小于500ms
        self.assertLess(percentile_95, 1000)  # 95%请求响应时间小于1000ms
    
    def test_concurrent_user_sessions(self):
        """测试并发用户会话性能"""
        def chat_session(user_id, messages, results):
            """模拟用户会话"""
            session_times = []
            for i, message in enumerate(messages):
                start_time = time.time()
                try:
                    response = self.client.post('/api/chat',
                                              json={
                                                  'text': message,
                                                  'user_id': user_id
                                              })
                    success = response.status_code == 200
                except:
                    success = False
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                session_times.append(response_time)
            
            results[user_id] = {
                'times': session_times,
                'avg_time': statistics.mean(session_times) if session_times else 0,
                'success_rate': sum(1 for t in session_times if t > 0) / len(messages) if messages else 0
            }
        
        # 模拟多个用户并发会话
        import threading
        users = [f'user_{i}' for i in range(10)]
        messages = ['你好', '我想学习数学', '能解释一下几何吗？', '谢谢你的帮助']
        threads = []
        results = {}
        
        # 创建并启动线程
        for user_id in users:
            thread = threading.Thread(target=chat_session, 
                                    args=(user_id, messages, results))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 分析结果
        all_times = []
        for user_result in results.values():
            all_times.extend(user_result['times'])
        
        avg_time = statistics.mean(all_times) if all_times else 0
        percentile_95 = statistics.quantiles(all_times, n=20)[-1] if len(all_times) >= 20 else 0
        
        # 输出结果
        print(f"\n=== 并发用户会话性能测试结果 ===")
        print(f"并发用户数: {len(users)}")
        print(f"每用户消息数: {len(messages)}")
        print(f"总请求数: {len(all_times)}")
        print(f"平均响应时间: {avg_time:.2f}ms")
        print(f"95%分位数响应时间: {percentile_95:.2f}ms")
        
        # 断言检查
        self.assertLess(avg_time, 1500)  # 平均响应时间小于1500ms


if __name__ == '__main__':
    unittest.main(verbosity=2)