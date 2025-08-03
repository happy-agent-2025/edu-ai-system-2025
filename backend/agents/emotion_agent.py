#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
情感陪伴Agent
"""

from typing import Dict, Any
from backend.agents.base_agent import BaseAgent


class EmotionAgent(BaseAgent):
    """
    情感陪伴Agent负责处理与情感相关的问题，提供情感支持
    """
    
    def __init__(self):
        """初始化情感陪伴Agent"""
        super().__init__("EmotionAgent")
        self.set_description("负责处理情感相关问题的Agent")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理情感相关请求
        
        Args:
            input_data (Dict[str, Any]): 输入数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        user_text = input_data.get('text', '')
        user_emotion = input_data.get('emotion', 'neutral')
        
        # 生成情感响应
        response_text = self._generate_emotional_response(user_text, user_emotion)
        
        return {
            'agent': self.name,
            'response': response_text,
            'status': 'success'
        }
    
    def _generate_emotional_response(self, user_text: str, user_emotion: str) -> str:
        """
        根据用户情感状态生成响应
        
        Args:
            user_text (str): 用户输入文本
            user_emotion (str): 用户情感状态
            
        Returns:
            str: 生成的响应文本
        """
        # 这里应该调用实际的情感AI模型来生成响应
        # 目前只是一个模拟实现
        
        if user_emotion == 'sad' or '难过' in user_text or '伤心' in user_text:
            return '我理解你现在感到难过。每个人都会有这样的时刻，这很正常。你想和我聊聊是什么让你感到难过吗？'
        elif user_emotion == 'happy' or '开心' in user_text or '高兴' in user_text:
            return '很高兴听到你很开心！开心的时候可以和我分享你的快乐，让快乐加倍哦！'
        elif user_emotion == 'angry' or '生气' in user_text or '愤怒' in user_text:
            return '生气是很正常的情绪，但我们要学会管理它。深呼吸几次，告诉我发生了什么吧。'
        elif '孤独' in user_text or '孤单' in user_text:
            return '我在这里陪伴你，你并不孤单。我们可以一起聊天，一起玩游戏，让孤单的感觉消失。'
        elif '害怕' in user_text or '恐惧' in user_text:
            return '害怕是人类的本能反应，这说明你有保护自己的意识。告诉我你害怕什么，我们一起想办法克服它。'
        else:
            return '我在这里陪伴你，你可以和我分享你的任何感受。无论开心还是难过，我都会认真倾听。'