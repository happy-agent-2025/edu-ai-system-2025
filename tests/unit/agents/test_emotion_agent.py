#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EmotionAgent单元测试
"""

import unittest
from backend.agents.emotion_agent import EmotionAgent


class TestEmotionAgent(unittest.TestCase):
    """EmotionAgent测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.agent = EmotionAgent()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.agent.name, "EmotionAgent")
        self.assertIn("情感", self.agent.description)
    
    def test_process_request(self):
        """测试处理请求"""
        input_data = {
            "text": "我今天很开心",
            "user_id": "test_user",
            "emotion": "happy"
        }
        
        result = self.agent.process(input_data)
        self.assertIn("response", result)
        self.assertIn("agent", result)
        self.assertEqual(result["agent"], "EmotionAgent")
        self.assertEqual(result["status"], "success")
    
    def test_generate_emotional_response(self):
        """测试生成情感响应"""
        response = self.agent._generate_emotional_response("我很 sad", "sad")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)


if __name__ == '__main__':
    unittest.main()