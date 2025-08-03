#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整流程集成测试
"""

import unittest
import json
import tempfile
import os
from backend.app import create_app
from backend.database.manager import DatabaseManager


class TestFullFlow(unittest.TestCase):
    """完整流程测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        # 创建临时数据库
        cls.db_fd, cls.db_path = tempfile.mkstemp()
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['DATABASE'] = cls.db_path
        cls.client = cls.app.test_client()
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        # 关闭临时数据库
        os.close(cls.db_fd)
        os.unlink(cls.db_path)
    
    def test_full_conversation_flow(self):
        """测试完整对话流程"""
        user_id = "integration_test_user"
        user_text = "你好，我想学习数学"
        
        # 发送聊天请求
        response = self.client.post('/api/chat',
                                  json={
                                      'text': user_text,
                                      'user_id': user_id
                                  })
        
        # 检查响应
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('response', data)
        self.assertIn('agent', data)
        
        # 检查对话历史
        history_response = self.client.get(f'/api/user/{user_id}/history')
        self.assertEqual(history_response.status_code, 200)
        
        history_data = json.loads(history_response.data)
        self.assertEqual(history_data['status'], 'success')
        self.assertGreater(len(history_data['history']), 0)
        
        # 检查最近的对话记录
        latest_conversation = history_data['history'][0]
        self.assertEqual(latest_conversation['user_input'], user_text)
        self.assertEqual(latest_conversation['user_id'], user_id)
    
    def test_multiple_conversations_flow(self):
        """测试多轮对话流程"""
        user_id = "multi_conversation_test_user"
        conversations = [
            "你好",
            "我想学习数学",
            "能告诉我什么是几何吗？"
        ]
        
        # 进行多轮对话
        for user_text in conversations:
            response = self.client.post('/api/chat',
                                      json={
                                          'text': user_text,
                                          'user_id': user_id
                                      })
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'success')
        
        # 检查对话历史
        history_response = self.client.get(f'/api/user/{user_id}/history?limit=10')
        self.assertEqual(history_response.status_code, 200)
        
        history_data = json.loads(history_response.data)
        self.assertEqual(history_data['status'], 'success')
        self.assertGreaterEqual(len(history_data['history']), len(conversations))
    
    def test_system_statistics_flow(self):
        """测试系统统计流程"""
        # 获取系统统计
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('stats', data)
        
        stats = data['stats']
        self.assertIn('users', stats)
        self.assertIn('conversations', stats)
        self.assertIn('safety', stats)
    
    def test_search_functionality_flow(self):
        """测试搜索功能流程"""
        user_id = "search_test_user"
        search_term = "数学"
        
        # 先进行一些对话
        self.client.post('/api/chat',
                        json={
                            'text': "我想学习数学",
                            'user_id': user_id
                        })
        
        # 搜索对话记录
        response = self.client.get(f'/api/search?q={search_term}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('results', data)
        self.assertIn('count', data)


if __name__ == '__main__':
    unittest.main()