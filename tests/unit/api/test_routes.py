#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API路由单元测试
"""

import unittest
import json
from unittest.mock import patch, MagicMock
from backend.app import create_app


class TestAPIRoutes(unittest.TestCase):
    """API路由测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_health_check(self):
        """测试健康检查接口"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('message', data)
        self.assertEqual(data['status'], 'healthy')
    
    @patch('backend.api.routes.meta_agent')
    @patch('backend.api.routes.safety_agent')
    @patch('backend.api.routes.db_manager')
    def test_chat_endpoint_success(self, mock_db, mock_safety, mock_meta):
        """测试聊天接口成功情况"""
        # 模拟Agent响应
        mock_meta.process.return_value = {
            'response': '这是一个测试响应',
            'agent': 'TestAgent'
        }
        
        mock_safety.process.return_value = {
            'status': 'approved',
            'message': 'Content approved',
            'original_response': '这是一个测试响应'
        }
        
        # 发送请求
        response = self.client.post('/api/chat', 
                                  json={
                                      'text': '你好',
                                      'user_id': 'test_user'
                                  })
        
        # 检查响应
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('response', data)
        self.assertIn('agent', data)
        self.assertEqual(data['status'], 'success')
    
    @patch('backend.api.routes.meta_agent')
    @patch('backend.api.routes.safety_agent')
    @patch('backend.api.routes.db_manager')
    def test_chat_endpoint_safety_rejection(self, mock_db, mock_safety, mock_meta):
        """测试聊天接口安全检查拒绝情况"""
        # 模拟Agent响应
        mock_meta.process.return_value = {
            'response': '不安全的内容',
            'agent': 'TestAgent'
        }
        
        mock_safety.process.return_value = {
            'status': 'rejected',
            'message': 'Content rejected',
            'reason': '包含不适当内容',
            'original_response': '不安全的内容'
        }
        
        # 发送请求
        response = self.client.post('/api/chat', 
                                  json={
                                      'text': '危险请求',
                                      'user_id': 'test_user'
                                  })
        
        # 检查响应
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('response', data)
        self.assertEqual(data['status'], 'success')
    
    def test_chat_endpoint_missing_text(self):
        """测试聊天接口缺少文本参数"""
        response = self.client.post('/api/chat', 
                                  json={
                                      'user_id': 'test_user'
                                  })
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('message', data)
        self.assertEqual(data['status'], 'error')
    
    @patch('backend.api.routes.db_queries')
    def test_user_history_endpoint(self, mock_queries):
        """测试用户历史接口"""
        # 模拟查询结果
        mock_queries.get_user_conversation_history.return_value = []
        
        response = self.client.get('/api/user/test_user/history')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('history', data)
        self.assertEqual(data['status'], 'success')
    
    @patch('backend.api.routes.db_queries')
    def test_stats_endpoint(self, mock_queries):
        """测试统计接口"""
        # 模拟查询结果
        mock_queries.get_system_statistics.return_value = {}
        
        response = self.client.get('/api/stats')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('stats', data)
        self.assertEqual(data['status'], 'success')


if __name__ == '__main__':
    unittest.main()