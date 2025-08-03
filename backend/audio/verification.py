#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
声纹验证
"""

from typing import Any, Dict, List
import hashlib


class VoiceVerification:
    """
    声纹验证类，用于验证用户身份
    """
    
    def __init__(self):
        """初始化声纹验证服务"""
        # 存储用户声纹特征（实际应用中应该存储更复杂的特征向量）
        self.user_voiceprints = {}
    
    def register_user(self, user_id: str, voice_sample: Any) -> bool:
        """
        注册用户声纹
        
        Args:
            user_id (str): 用户ID
            voice_sample (Any): 声音样本
            
        Returns:
            bool: 注册是否成功
        """
        try:
            # 提取声纹特征（这里简化为哈希值）
            voiceprint = self._extract_voiceprint(voice_sample)
            self.user_voiceprints[user_id] = voiceprint
            return True
        except Exception as e:
            print(f"注册用户声纹时出错: {e}")
            return False
    
    def verify_user(self, user_id: str, voice_sample: Any) -> Dict[str, Any]:
        """
        验证用户身份
        
        Args:
            user_id (str): 用户ID
            voice_sample (Any): 待验证的声音样本
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        if user_id not in self.user_voiceprints:
            return {
                'verified': False,
                'message': '用户未注册'
            }
        
        try:
            # 提取待验证声音的声纹特征
            voiceprint = self._extract_voiceprint(voice_sample)
            
            # 比较声纹特征
            registered_voiceprint = self.user_voiceprints[user_id]
            similarity = self._calculate_similarity(voiceprint, registered_voiceprint)
            
            # 设定阈值
            threshold = 0.8
            verified = similarity >= threshold
            
            return {
                'verified': verified,
                'similarity': similarity,
                'threshold': threshold,
                'message': '验证通过' if verified else '验证失败'
            }
        except Exception as e:
            return {
                'verified': False,
                'message': f'验证过程中出错: {e}'
            }
    
    def _extract_voiceprint(self, voice_sample: Any) -> str:
        """
        从声音样本中提取声纹特征
        
        Args:
            voice_sample (Any): 声音样本
            
        Returns:
            str: 声纹特征（简化为哈希值）
        """
        # 实际应用中应该使用专业的声纹识别算法
        # 这里简化为对样本数据的哈希处理
        sample_str = str(voice_sample).encode('utf-8')
        return hashlib.md5(sample_str).hexdigest()
    
    def _calculate_similarity(self, voiceprint1: str, voiceprint2: str) -> float:
        """
        计算两个声纹特征的相似度
        
        Args:
            voiceprint1 (str): 声纹特征1
            voiceprint2 (str): 声纹特征2
            
        Returns:
            float: 相似度 (0-1)
        """
        # 实际应用中应该使用更复杂的相似度计算方法
        # 这里简化为比较相同字符的比例
        if len(voiceprint1) != len(voiceprint2):
            return 0.0
        
        matches = sum(c1 == c2 for c1, c2 in zip(voiceprint1, voiceprint2))
        return matches / len(voiceprint1)