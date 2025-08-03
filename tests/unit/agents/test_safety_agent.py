#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SafetyAgent单元测试
"""

import unittest
from backend.agents.safety_agent import SafetyAgent


class TestSafetyAgent(unittest.TestCase):
    """SafetyAgent测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.agent = SafetyAgent()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.agent.name, "SafetyAgent")
        self.assertIn("安全", self.agent.description)
    
    def test_safe_content_check(self):
        """测试安全内容检查"""
        input_data = {
            "response": "这是一个安全的响应",
            "agent": "TestAgent"
        }
        
        result = self.agent.process(input_data)
        self.assertEqual(result["status"], "approved")
        self.assertIn("original_response", result)
    
    def test_unsafe_content_check(self):
        """测试不安全内容检查"""
        input_data = {
            "response": "包含暴力内容的响应",
            "agent": "TestAgent"
        }
        
        # 修改SafetyAgent的unsafe_keywords以测试
        self.agent.unsafe_keywords.append("暴力")
        result = self.agent.process(input_data)
        self.assertEqual(result["status"], "rejected")
        self.assertIn("reason", result)
    
    def test_generate_safe_response(self):
        """测试生成安全响应"""
        response = self.agent.generate_safe_response("危险请求")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        self.assertIn("安全", response)


if __name__ == '__main__':
    unittest.main()