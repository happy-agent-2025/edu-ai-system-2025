#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音频处理单元测试
"""

import unittest
import numpy as np
from backend.audio.processing import AudioProcessor


class TestAudioProcessor(unittest.TestCase):
    """AudioProcessor测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.processor = AudioProcessor()
    
    def test_normalize(self):
        """测试音频归一化"""
        # 创建测试音频数据
        audio_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        normalized = self.processor.normalize(audio_data)
        
        # 检查归一化结果
        self.assertAlmostEqual(np.max(np.abs(normalized)), 1.0)
        self.assertEqual(len(normalized), len(audio_data))
    
    def test_remove_silence(self):
        """测试移除静音"""
        # 创建包含静音的音频数据
        audio_data = np.array([0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 0.0, 0.0])
        processed = self.processor.remove_silence(audio_data, threshold=0.5)
        
        # 检查静音是否被移除
        self.assertGreater(len(processed), 0)
        self.assertLess(len(processed), len(audio_data))
    
    def test_resample(self):
        """测试重采样"""
        # 创建测试音频数据
        audio_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        original_rate = 1000
        target_rate = 2000
        
        resampled = self.processor.resample(audio_data, original_rate, target_rate)
        
        # 检查重采样结果
        self.assertEqual(len(resampled), len(audio_data) * 2)
    
    def test_resample_same_rate(self):
        """测试相同采样率的重采样"""
        audio_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        rate = 1000
        
        resampled = self.processor.resample(audio_data, rate, rate)
        
        # 检查结果是否相同
        np.testing.assert_array_equal(resampled, audio_data)


if __name__ == '__main__':
    unittest.main()