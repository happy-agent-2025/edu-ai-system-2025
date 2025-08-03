#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STT服务单元测试
"""

import unittest
import numpy as np
from backend.audio.stt_service import STTService


class TestSTTService(unittest.TestCase):
    """STTService测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.stt_service = STTService()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.stt_service, STTService)
    
    def test_transcribe(self):
        """测试语音转文本"""
        # 创建模拟音频数据
        audio_data = np.random.randn(1000).astype(np.float32)
        
        result = self.stt_service.transcribe(audio_data)
        
        # 检查返回结果
        self.assertIn("text", result)
        self.assertIn("confidence", result)
        self.assertIn("language", result)
        self.assertIsInstance(result["text"], str)
        self.assertIsInstance(result["confidence"], float)
        self.assertIsInstance(result["language"], str)
    
    def test_transcribe_with_timestamps(self):
        """测试带时间戳的语音转文本"""
        # 创建模拟音频数据
        audio_data = np.random.randn(1000).astype(np.float32)
        
        result = self.stt_service.transcribe_with_timestamps(audio_data)
        
        # 检查返回结果
        self.assertIn("text", result)
        self.assertIn("confidence", result)
        self.assertIn("language", result)
        self.assertIn("timestamps", result)
        self.assertIsInstance(result["timestamps"], list)


if __name__ == '__main__':
    unittest.main()