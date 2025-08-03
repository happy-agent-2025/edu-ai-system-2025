#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MetaAgent单元测试
"""

import unittest
from backend.agents.meta_agent import MetaAgent


class TestMetaAgent(unittest.TestCase):
    """MetaAgent测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.agent = MetaAgent()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.agent.name, "MetaAgent")
        self.assertIn("意图识别", self.agent.description)
    
    def test_identify_edu_intent(self):
        """测试教育意图识别"""
        edu_texts = [
            "我想学习数学",
            "什么是光合作用",
            "请解释一下物理定律",
            "帮我解答这道题"
        ]
        
        for text in edu_texts:
            intent = self.agent._identify_intent(text)
            self.assertEqual(intent, "edu", f"Failed for text: {text}")
    
    def test_identify_emotion_intent(self):
        """测试情感意图识别"""
        emotion_texts = [
            "我今天很开心",
            "我感到很难过",
            "我有点生气",
            "我想找人聊天"
        ]
        
        for text in emotion_texts:
            intent = self.agent._identify_intent(text)
            self.assertEqual(intent, "emotion", f"Failed for text: {text}")
    
    def test_process_edu_request(self):
        """测试处理教育请求"""
        input_data = {
            "text": "什么是光合作用？",
            "user_id": "test_user"
        }
        
        result = self.agent.process(input_data)
        self.assertIn("response", result)
        self.assertIn("agent", result)
        self.assertEqual(result["agent"], "EduAgent")
    
    def test_process_emotion_request(self):
        """测试处理情感请求"""
        input_data = {
            "text": "我今天很难过",
            "user_id": "test_user",
            "emotion": "sad"
        }
        
        result = self.agent.process(input_data)
        self.assertIn("response", result)
        self.assertIn("agent", result)
        self.assertEqual(result["agent"], "EmotionAgent")


if __name__ == '__main__':
    unittest.main()