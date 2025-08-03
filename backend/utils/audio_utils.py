#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音频工具
"""

import numpy as np
from typing import Any, Dict
import base64


class AudioUtils:
    """
    音频工具类，提供常用的音频处理功能
    """
    
    @staticmethod
    def calculate_volume(audio_data: np.ndarray) -> float:
        """
        计算音频数据的音量（RMS）
        
        Args:
            audio_data (np.ndarray): 音频数据
            
        Returns:
            float: 音量值（0-1）
        """
        if len(audio_data) == 0:
            return 0.0
        
        # 计算均方根
        rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
        return float(rms)
    
    @staticmethod
    def detect_silence(audio_data: np.ndarray, threshold: float = 0.01, 
                      min_silence_duration: float = 0.5, sample_rate: int = 22050) -> bool:
        """
        检测音频是否为静音
        
        Args:
            audio_data (np.ndarray): 音频数据
            threshold (float): 静音阈值（0-1）
            min_silence_duration (float): 最小静音持续时间（秒）
            sample_rate (int): 采样率
            
        Returns:
            bool: 是否为静音
        """
        volume = AudioUtils.calculate_volume(audio_data)
        duration = len(audio_data) / sample_rate if sample_rate > 0 else 0
        
        return volume < threshold and duration >= min_silence_duration
    
    @staticmethod
    def normalize_audio(audio_data: np.ndarray) -> np.ndarray:
        """
        归一化音频数据
        
        Args:
            audio_data (np.ndarray): 音频数据
            
        Returns:
            np.ndarray: 归一化后的音频数据
        """
        if len(audio_data) == 0:
            return audio_data
        
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val
        return audio_data
    
    @staticmethod
    def convert_to_mono(audio_data: np.ndarray, channels: int = 1) -> np.ndarray:
        """
        转换为单声道音频
        
        Args:
            audio_data (np.ndarray): 音频数据
            channels (int): 原始声道数
            
        Returns:
            np.ndarray: 单声道音频数据
        """
        if channels == 1:
            return audio_data
        
        # 如果是多声道，转换为单声道
        if len(audio_data.shape) > 1 and audio_data.shape[1] == channels:
            return np.mean(audio_data, axis=1)
        elif len(audio_data) % channels == 0:
            # 重构成多声道然后取平均
            reshaped = audio_data.reshape(-1, channels)
            return np.mean(reshaped, axis=1)
        else:
            return audio_data
    
    @staticmethod
    def apply_gain(audio_data: np.ndarray, gain: float) -> np.ndarray:
        """
        应用增益到音频数据
        
        Args:
            audio_data (np.ndarray): 音频数据
            gain (float): 增益值（线性，1.0为原始音量）
            
        Returns:
            np.ndarray: 应用增益后的音频数据
        """
        return audio_data * gain
    
    @staticmethod
    def audio_to_base64(audio_data: np.ndarray) -> str:
        """
        将音频数据转换为base64编码
        
        Args:
            audio_data (np.ndarray): 音频数据
            
        Returns:
            str: base64编码的音频数据
        """
        # 转换为bytes
        audio_bytes = audio_data.tobytes()
        # 编码为base64
        return base64.b64encode(audio_bytes).decode('utf-8')
    
    @staticmethod
    def base64_to_audio(base64_data: str, dtype: np.dtype = np.float32) -> np.ndarray:
        """
        将base64编码的音频数据转换为numpy数组
        
        Args:
            base64_data (str): base64编码的音频数据
            dtype (np.dtype): 数据类型
            
        Returns:
            np.ndarray: 音频数据
        """
        # 解码base64
        audio_bytes = base64.b64decode(base64_data)
        # 转换为numpy数组
        return np.frombuffer(audio_bytes, dtype=dtype)
    
    @staticmethod
    def get_audio_duration(audio_data: np.ndarray, sample_rate: int) -> float:
        """
        计算音频时长
        
        Args:
            audio_data (np.ndarray): 音频数据
            sample_rate (int): 采样率
            
        Returns:
            float: 音频时长（秒）
        """
        if sample_rate <= 0:
            return 0.0
        return len(audio_data) / sample_rate