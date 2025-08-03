#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TTS服务单元测试
"""

import unittest
import numpy as np
from backend.audio.tts_service import TTSService


class TestTTSService(unittest.TestCase):
    """TTSService测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.tts_service = TTSService()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.tts_service, TTSService)
    
    def test_synthesize(self):
        """测试文本转语音"""
        text = "你好，世界！"
        
        result = self.tts_service.synthesize(text)
        
        # 检查返回结果
        self.assertIn("audio_data", result)
        self.assertIn("sample_rate", result)
        self.assertIn("duration", result)
        self.assertIn("text", result)
        self.assertIsInstance(result["audio_data"], np.ndarray)
        self.assertIsInstance(result["sample_rate"], int)
        self.assertIsInstance(result["duration"], float)
        self.assertEqual(result["text"], text)
    
    def test_synthesize_with_emotion(self):
        """测试带情感的文本转语音"""
        text = "你好，世界！"
        emotion = "happy"
        
        result = self.tts_service.synthesize_with_emotion(text, emotion)
        
        # 检查返回结果
        self.assertIn("audio_data", result)
        self.assertIn("sample_rate", result)
        self.assertIn("duration", result)
        self.assertIn("text", result)
        self.assertIn("emotion", result)
        self.assertIsInstance(result["audio_data"], np.ndarray)
        self.assertIsInstance(result["sample_rate"], int)
        self.assertIsInstance(result["duration"], float)
        self.assertEqual(result["text"], text)
        self.assertEqual(result["emotion"], emotion)
    
    def test_get_emotion_voice_params(self):
        """测试获取情感语音参数"""
        emotions = ["happy", "sad", "neutral", "angry"]
        
        for emotion in emotions:
            params = self.tts_service._get_emotion_voice_params(emotion)
            self.assertIn("pitch", params)
            self.assertIn("speed", params)
            self.assertIn("energy", params)
            self.assertIsInstance(params["pitch"], float)
            self.assertIsInstance(params["speed"], float)
            self.assertIsInstance(params["energy"], float)


if __name__ == '__main__':
    unittest.main()