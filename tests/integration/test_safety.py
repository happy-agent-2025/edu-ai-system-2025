#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
安全流程集成测试
"""

import unittest
import json
from unittest.mock import patch
from backend.app import create_app


class TestSafetyFlow(unittest.TestCase):
    """安全流程测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('backend.api.routes.meta_agent')
    @patch('backend.api.routes.safety_agent')
    @patch('backend.api.routes.db_manager')
    def test_safe_content_flow(self, mock_db, mock_safety, mock_meta):
        """测试安全内容流程"""
        # 模拟安全响应
        mock_meta.process.return_value = {
            'response': '这是一个安全的教育内容',
            'agent': 'EduAgent'
        }
        
        mock_safety.process.return_value = {
            'status': 'approved',
            'message': 'Content approved',
            'original_response': '这是一个安全的教育内容'
        }
        
        # 发送请求
        response = self.client.post('/api/chat',
                                  json={
                                      'text': '我想学习科学',
                                      'user_id': 'safety_test_user'
                                  })
        
        # 检查响应
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('response', data)
        self.assertIn('agent', data)
        self.assertEqual(data['response'], '这是一个安全的教育内容')
    
    @patch('backend.api.routes.meta_agent')
    @patch('backend.api.routes.safety_agent')
    @patch('backend.api.routes.db_manager')
    def test_unsafe_content_flow(self, mock_db, mock_safety, mock_meta):
        """测试不安全内容处理流程"""
        # 模拟不安全响应
        mock_meta.process.return_value = {
            'response': '包含不适当内容的响应',
            'agent': 'EduAgent'
        }
        
        mock_safety.process.return_value = {
            'status': 'rejected',
            'message': 'Content rejected',
            'reason': '包含不适当内容',
            'original_response': '包含不适当内容的响应'
        }
        
        # 发送请求
        response = self.client.post('/api/chat',
                                  json={
                                      'text': '危险请求',
                                      'user_id': 'safety_test_user'
                                  })
        
        # 检查响应（应该返回安全的响应）
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('response', data)
        # 应该返回安全的响应而不是原始不安全响应
        self.assertNotEqual(data['response'], '包含不适当内容的响应')
    
    @patch('backend.api.routes.meta_agent')
    @patch('backend.api.routes.safety_agent')
    @patch('backend.api.routes.db_manager')
    def test_safety_log_recording(self, mock_db, mock_safety, mock_meta):
        """测试安全日志记录"""
        # 模拟不安全响应
        mock_meta.process.return_value = {
            'response': '不安全内容',
            'agent': 'EduAgent'
        }
        
        mock_safety.process.return_value = {
            'status': 'rejected',
            'message': 'Content rejected',
            'reason': '测试违规',
            'original_response': '不安全内容'
        }
        
        # 发送请求
        response = self.client.post('/api/chat',
                                  json={
                                      'text': '测试安全日志',
                                      'user_id': 'safety_log_test_user'
                                  })
        
        # 检查响应
        self.assertEqual(response.status_code, 200)
        
        # 验证数据库调用
        mock_db.insert_safety_log.assert_called_once()
        mock_db.insert_conversation.assert_called_once()
    
    def test_safety_violations_endpoint(self):
        """测试安全违规记录接口"""
        response = self.client.get('/api/safety/violations')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('violations', data)


if __name__ == '__main__':
    unittest.main()