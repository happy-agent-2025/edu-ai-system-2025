#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
元Agent - 意图识别和路由
"""

import re
from typing import Dict, Any
from backend.agents.base_agent import BaseAgent
from backend.agents.edu_agent import EduAgent
from backend.agents.emotion_agent import EmotionAgent


class MetaAgent(BaseAgent):
    """
    元Agent负责识别用户输入的意图，并将请求路由到相应的处理Agent
    """
    
    def __init__(self):
        """初始化元Agent"""
        super().__init__("MetaAgent")
        self.set_description("负责意图识别和路由的核心Agent")
        
        # 初始化各个目标Agent
        self.edu_agent = EduAgent()
        self.emotion_agent = EmotionAgent()
        
        # 定义教育相关关键词
        self.edu_keywords = [
            '学习', '知识', '问题', '数学', '语文', '英语', '科学', '历史', '地理',
            '物理', '化学', '生物', '计算', '怎么', '为什么', '什么', '解释',
            '教学', '课程', '作业', '练习', '考试', '成绩', '技能'
        ]
        
        # 定义情感相关关键词
        self.emotion_keywords = [
            '心情', '开心', '难过', '生气', '害怕', '紧张', '孤独', '无聊', 
            '兴奋', '沮丧', '焦虑', '朋友', '家人', '父母', '老师', '同学',
            '玩耍', '游戏', '娱乐', '有趣', '快乐', '伤心', '郁闷'
        ]
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理输入数据，识别意图并路由到相应Agent
        
        Args:
            input_data (Dict[str, Any]): 输入数据，包含用户文本等信息
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        user_text = input_data.get('text', '').lower()
        
        # 识别意图
        intent = self._identify_intent(user_text)
        
        # 根据意图路由到相应Agent
        if intent == 'edu':
            return self.edu_agent.process(input_data)
        elif intent == 'emotion':
            return self.emotion_agent.process(input_data)
        else:
            # 默认路由到教育Agent
            return self.edu_agent.process(input_data)
    
    def _identify_intent(self, text: str) -> str:
        """
        识别用户输入的意图
        
        Args:
            text (str): 用户输入文本
            
        Returns:
            str: 意图类型 ('edu', 'emotion', 'unknown')
        """
        edu_score = 0
        emotion_score = 0
        
        # 计算教育相关关键词匹配数
        for keyword in self.edu_keywords:
            if keyword in text:
                edu_score += 1
                
        # 计算情感相关关键词匹配数
        for keyword in self.emotion_keywords:
            if keyword in text:
                emotion_score += 1
        
        # 根据匹配分数判断意图
        if edu_score > emotion_score and edu_score > 0:
            return 'edu'
        elif emotion_score > edu_score and emotion_score > 0:
            return 'emotion'
        else:
            # 如果无法明确判断，优先教育意图
            return 'edu' if edu_score > 0 else 'unknown'