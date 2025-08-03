#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音频预处理
"""

import numpy as np
from typing import Any


class AudioProcessor:
    """
    音频预处理类，负责对原始音频进行预处理操作
    """
    
    def __init__(self):
        """初始化音频处理器"""
        pass
    
    def normalize(self, audio_data: np.ndarray) -> np.ndarray:
        """
        归一化音频数据
        
        Args:
            audio_data (np.ndarray): 原始音频数据
            
        Returns:
            np.ndarray: 归一化后的音频数据
        """
        # 确保数据类型为浮点型
        audio_data = audio_data.astype(np.float32)
        
        # 计算最大值
        max_val = np.max(np.abs(audio_data))
        
        # 避免除零错误
        if max_val > 0:
            audio_data = audio_data / max_val
            
        return audio_data
    
    def remove_silence(self, audio_data: np.ndarray, threshold: float = 0.01) -> np.ndarray:
        """
        移除音频中的静音部分
        
        Args:
            audio_data (np.ndarray): 音频数据
            threshold (float): 静音阈值
            
        Returns:
            np.ndarray: 移除静音后的音频数据
        """
        # 计算音频的绝对值
        abs_audio = np.abs(audio_data)
        
        # 找到非静音部分
        non_silent_indices = np.where(abs_audio > threshold)[0]
        
        if len(non_silent_indices) > 0:
            # 提取非静音部分
            start_idx = non_silent_indices[0]
            end_idx = non_silent_indices[-1]
            return audio_data[start_idx:end_idx+1]
        else:
            # 如果全部是静音，返回空数组
            return np.array([])
    
    def resample(self, audio_data: np.ndarray, original_rate: int, target_rate: int) -> np.ndarray:
        """
        重采样音频数据
        
        Args:
            audio_data (np.ndarray): 原始音频数据
            original_rate (int): 原始采样率
            target_rate (int): 目标采样率
            
        Returns:
            np.ndarray: 重采样后的音频数据
        """
        if original_rate == target_rate:
            return audio_data
        
        # 计算重采样比例
        ratio = target_rate / original_rate
        
        # 计算新长度
        new_length = int(len(audio_data) * ratio)
        
        # 简单的重采样实现（实际应用中应使用专业库如scipy）
        indices = np.linspace(0, len(audio_data) - 1, new_length)
        resampled = np.interp(indices, np.arange(len(audio_data)), audio_data)
        
        return resampled