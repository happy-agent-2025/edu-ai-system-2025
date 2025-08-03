#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EduAgent单元测试
"""

import unittest
from backend.agents.edu_agent import EduAgent


class TestEduAgent(unittest.TestCase):
    """EduAgent测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.agent = EduAgent()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.agent.name, "EduAgent")
        self.assertIn("教育", self.agent.description)
    
    def test_process_request(self):
        """测试处理请求"""
        input_data = {
            "text": "什么是光合作用？",
            "user_id": "test_user"
        }
        
        result = self.agent.process(input_data)
        self.assertIn("response", result)
        self.assertIn("agent", result)
        self.assertEqual(result["agent"], "EduAgent")
        self.assertEqual(result["status"], "success")
    
    def test_generate_educational_response(self):
        """测试生成教育响应"""
        response = self.agent._generate_educational_response("你好")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)


if __name__ == '__main__':
    unittest.main()