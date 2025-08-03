#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BaseAgent单元测试
"""

import unittest
from backend.agents.base_agent import BaseAgent


class TestBaseAgent(unittest.TestCase):
    """BaseAgent测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.agent = BaseAgent("TestAgent")
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.agent.name, "TestAgent")
        self.assertEqual(self.agent.description, "")
    
    def test_get_name(self):
        """测试获取名称"""
        self.assertEqual(self.agent.get_name(), "TestAgent")
    
    def test_get_description(self):
        """测试获取描述"""
        self.assertEqual(self.agent.get_description(), "")
    
    def test_set_description(self):
        """测试设置描述"""
        description = "This is a test agent"
        self.agent.set_description(description)
        self.assertEqual(self.agent.get_description(), description)
    
    def test_abstract_process_method(self):
        """测试抽象方法"""
        with self.assertRaises(NotImplementedError):
            self.agent.process({})


if __name__ == '__main__':
    unittest.main()