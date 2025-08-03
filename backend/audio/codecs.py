#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音频编解码
"""

from typing import Any, Dict
import numpy as np
import io
import wave


class AudioCodec:
    """
    音频编解码类，负责音频数据的编码和解码
    """
    
    def __init__(self):
        """初始化音频编解码器"""
        pass
    
    def encode_wav(self, audio_data: np.ndarray, sample_rate: int = 22050) -> bytes:
        """
        将音频数据编码为WAV格式
        
        Args:
            audio_data (np.ndarray): 音频数据
            sample_rate (int): 采样率
            
        Returns:
            bytes: WAV格式的音频数据
        """
        # 确保数据类型为16位整数
        if audio_data.dtype != np.int16:
            # 归一化到-1到1之间
            audio_data = audio_data / np.max(np.abs(audio_data))
            # 转换为16位整数
            audio_data = (audio_data * 32767).astype(np.int16)
        
        # 创建WAV文件
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # 单声道
            wav_file.setsampwidth(2)  # 16位
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        return buffer.getvalue()
    
    def decode_wav(self, wav_data: bytes) -> Dict[str, Any]:
        """
        解码WAV格式音频数据
        
        Args:
            wav_data (bytes): WAV格式的音频数据
            
        Returns:
            Dict[str, Any]: 解码结果，包括音频数据和元信息
        """
        buffer = io.BytesIO(wav_data)
        with wave.open(buffer, 'rb') as wav_file:
            # 获取音频参数
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            sample_rate = wav_file.getframerate()
            frames = wav_file.getnframes()
            
            # 读取音频数据
            raw_audio_data = wav_file.readframes(frames)
            
            # 转换为numpy数组
            if sample_width == 1:
                audio_data = np.frombuffer(raw_audio_data, dtype=np.uint8)
                audio_data = audio_data.astype(np.int16)
            elif sample_width == 2:
                audio_data = np.frombuffer(raw_audio_data, dtype=np.int16)
            elif sample_width == 4:
                audio_data = np.frombuffer(raw_audio_data, dtype=np.int32)
            else:
                raise ValueError(f"不支持的采样宽度: {sample_width}")
        
        return {
            'audio_data': audio_data,
            'sample_rate': sample_rate,
            'channels': channels,
            'sample_width': sample_width,
            'frames': frames
        }
    
    def convert_format(self, audio_data: np.ndarray, from_format: str, to_format: str) -> bytes:
        """
        转换音频格式
        
        Args:
            audio_data (np.ndarray): 音频数据
            from_format (str): 源格式
            to_format (str): 目标格式
            
        Returns:
            bytes: 转换后的音频数据
        """
        # 这里应该实现不同格式之间的转换
        # 目前只支持WAV格式
        if to_format.lower() == 'wav':
            return self.encode_wav(audio_data)
        else:
            raise NotImplementedError(f"不支持的目标格式: {to_format}")