#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
安全Agent
"""

import re
from typing import Dict, Any, Tuple
from backend.agents.base_agent import BaseAgent


class SafetyAgent(BaseAgent):
    """
    安全Agent负责审查所有输出内容，确保符合儿童安全规范
    """
    
    def __init__(self):
        """初始化安全Agent"""
        super().__init__("SafetyAgent")
        self.set_description("负责审查内容安全性的Agent")
        
        # 不安全内容关键词列表
        self.unsafe_keywords = [
            # 暴力相关内容
            '暴力', '打架', '杀人', '死亡', '流血', '武器', '刀', '枪',
            
            # 不适当内容
            '成人', '色情', '性', '恋爱', '约会',
            
            # 危险行为
            '自杀', '自残', '毒品', '酒精', '吸烟',
            
            # 隐私信息
            '密码', '身份证', '银行卡', '家庭地址', '电话号码',
            
            # 负面情绪引导
            '绝望', '无意义', '恨', '报复'
        ]
        
        # 不安全模式（正则表达式）
        self.unsafe_patterns = [
            r'(\d{11})',  # 可能的手机号码
            r'(\d{18}|\d{17}[Xx])',  # 可能的身份证号
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # 可能的邮箱
        ]
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        审查输入内容的安全性
        
        Args:
            input_data (Dict[str, Any]): 待审查的输入数据
            
        Returns:
            Dict[str, Any]: 审查结果，包括是否安全和原因
        """
        response_text = input_data.get('response', '')
        agent_name = input_data.get('agent', 'Unknown')
        
        # 检查内容安全性
        is_safe, reason = self._check_content_safety(response_text)
        
        if is_safe:
            return {
                'agent': self.name,
                'status': 'approved',
                'message': f'Content from {agent_name} approved',
                'original_response': response_text
            }
        else:
            return {
                'agent': self.name,
                'status': 'rejected',
                'message': f'Content from {agent_name} rejected',
                'reason': reason,
                'original_response': response_text
            }
    
    def _check_content_safety(self, text: str) -> Tuple[bool, str]:
        """
        检查内容安全性
        
        Args:
            text (str): 待检查的文本
            
        Returns:
            Tuple[bool, str]: (是否安全, 原因)
        """
        # 检查关键词
        for keyword in self.unsafe_keywords:
            if keyword in text:
                return False, f"包含不安全关键词: {keyword}"
        
        # 检查模式
        for pattern in self.unsafe_patterns:
            if re.search(pattern, text):
                return False, f"包含不安全模式: {pattern}"
        
        # 检查长度（过长的内容可能包含不适宜信息）
        if len(text) > 1000:
            return False, "内容过长"
        
        # 如果没有发现问题，则认为是安全的
        return True, "内容安全"
    
    def generate_safe_response(self, original_request: str) -> str:
        """
        生成安全的响应内容
        
        Args:
            original_request (str): 原始请求
            
        Returns:
            str: 安全的响应内容
        """
        return "为了保护你的安全，我无法提供相关回答。如果你有其他问题，我很乐意帮助你。"