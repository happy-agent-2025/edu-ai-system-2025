#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
安全Agent
支持qwen:0.5b模型
"""

import re
from typing import Dict, Any, Tuple
from backend.agents.base_agent import BaseAgent
from backend.utils.config_loader import config_loader
from backend.utils.model_manager import model_manager
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


class SafetyAgent(BaseAgent):
    """
    安全Agent负责审查所有输出内容，确保符合儿童安全规范
    """
    
    def __init__(self):
        """初始化安全Agent"""
        super().__init__("SafetyAgent")
        self.set_description("负责审查内容安全性的Agent")
        
        # 获取模型配置（支持A/B测试）
        self.model_config = model_manager.get_agent_model_config("safety_agent")
        model_name = self.model_config.get("model_name", "qwen:0.5b")
        temperature = self.model_config.get("temperature", 0.0)
        
        # 初始化Ollama模型用于内容安全检查
        self.llm = Ollama(model=model_name, temperature=temperature)
        
        # 创建安全检查提示模板
        safety_template = """
        你是一个儿童内容安全审查专家。你的任务是检查以下内容是否适合儿童，
        是否包含任何不适当的内容，如暴力、色情、危险行为、个人隐私信息等。
        
        待检查的内容: {content}
        
        请分析以上内容，如果内容安全且适合儿童，请回答"SAFE"；
        如果内容包含不适当信息，请回答"UNSAFE: "并简要说明原因。
        你的回答只能是"SAFE"或"UNSAFE: [原因]"格式。
        """
        
        self.safety_prompt = PromptTemplate(
            input_variables=["content"],
            template=safety_template
        )
        
        # 创建安全链条
        self.safety_chain = LLMChain(llm=self.llm, prompt=self.safety_prompt)
        self.set_chain(self.safety_chain)
        
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
        user_id = input_data.get('user_id', 'default_user')
        response_text = input_data.get('response', '')
        agent_name = input_data.get('agent', 'Unknown')
        
        # 获取用户特定的模型配置（支持A/B测试）
        model_config = model_manager.get_agent_model_config("safety_agent", user_id)
        model_name = model_config.get("model_name")
        
        # 如果模型配置发生变化，重新初始化模型
        if model_name != self.llm.model:
            self.llm = Ollama(model=model_name, temperature=self.model_config.get("temperature", 0.0))
            self.safety_chain = LLMChain(llm=self.llm, prompt=self.safety_prompt)
            self.set_chain(self.safety_chain)
        
        # 首先进行关键词和模式检查
        keyword_safe, keyword_reason = self._check_keywords_and_patterns(response_text)
        if not keyword_safe:
            return {
                'agent': self.name,
                'status': 'rejected',
                'message': f'Content from {agent_name} rejected',
                'reason': keyword_reason,
                'original_response': response_text
            }
        
        # 然后使用LLM进行语义安全检查
        try:
            is_safe, reason = self._check_content_safety_with_llm(response_text)
        except Exception as e:
            # 如果LLM检查失败，回退到基础检查
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
    
    def _check_keywords_and_patterns(self, text: str) -> Tuple[bool, str]:
        """
        检查关键词和模式
        
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
        
        return True, "关键词检查通过"
    
    def _check_content_safety_with_llm(self, text: str) -> Tuple[bool, str]:
        """
        使用LLM检查内容安全性
        
        Args:
            text (str): 待检查的文本
            
        Returns:
            Tuple[bool, str]: (是否安全, 原因)
        """
        # 使用LLM进行语义安全检查
        llm_response = self.safety_chain.run({"content": text})
        
        # 解析LLM响应
        if llm_response.startswith("SAFE"):
            return True, "LLM检查通过"
        elif llm_response.startswith("UNSAFE:"):
            reason = llm_response[8:]  # 移除"UNSAFE: "前缀
            return False, f"LLM检测到不安全内容: {reason}"
        else:
            # 如果LLM响应格式不正确，认为内容安全
            return True, "LLM检查通过"
    
    def _check_content_safety(self, text: str) -> Tuple[bool, str]:
        """
        基础内容安全检查（备用方法）
        
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