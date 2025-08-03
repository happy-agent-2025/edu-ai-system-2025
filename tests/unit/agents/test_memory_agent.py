#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MemoryAgent单元测试
"""

import unittest
import os
from backend.agents.memory_agent import MemoryAgent


class TestMemoryAgent(unittest.TestCase):
    """MemoryAgent测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.agent = MemoryAgent()
    
    def tearDown(self):
        """测试后清理"""
        # 删除测试产生的内存文件
        if os.path.exists(self.agent.memory_file):
            os.remove(self.agent.memory_file)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.agent.name, "MemoryAgent")
        self.assertIn("记忆", self.agent.description)
    
    def test_store_conversation(self):
        """测试存储对话"""
        input_data = {
            "action": "store",
            "user_id": "test_user",
            "conversation": {
                "user_input": "你好",
                "agent_response": "你好！有什么可以帮助你的吗？",
                "agent_name": "TestAgent"
            }
        }
        
        result = self.agent.process(input_data)
        self.assertEqual(result["status"], "stored")
    
    def test_retrieve_conversation(self):
        """测试检索对话"""
        # 先存储一些对话
        store_data = {
            "action": "store",
            "user_id": "test_user",
            "conversation": {
                "user_input": "你好",
                "agent_response": "你好！有什么可以帮助你的吗？",
                "agent_name": "TestAgent"
            }
        }
        self.agent.process(store_data)
        
        # 然后检索对话
        retrieve_data = {
            "action": "retrieve",
            "user_id": "test_user"
        }
        
        result = self.agent.process(retrieve_data)
        self.assertEqual(result["status"], "retrieved")
        self.assertIn("history", result)
        self.assertGreater(len(result["history"]), 0)
    
    def test_memory_persistence(self):
        """测试记忆持久化"""
        # 存储一些数据
        conversation = {
            "user_input": "测试持久化",
            "agent_response": "响应内容",
            "agent_name": "TestAgent"
        }
        self.agent._store_conversation("persistence_test_user", conversation)
        
        # 创建新实例
        new_agent = MemoryAgent()
        
        # 检查数据是否被正确加载
        history = new_agent._retrieve_conversation_history("persistence_test_user")
        self.assertGreater(len(history), 0)
        self.assertEqual(history[0]["user_input"], "测试持久化")


if __name__ == '__main__':
    unittest.main()