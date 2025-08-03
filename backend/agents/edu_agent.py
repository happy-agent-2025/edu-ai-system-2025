#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
教育Agent
"""

from typing import Dict, Any
from backend.agents.base_agent import BaseAgent
from backend.utils.config_loader import config_loader
from backend.utils.model_manager import model_manager
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


class EduAgent(BaseAgent):
    """
    教育Agent负责处理与教育相关的问题
    """
    
    def __init__(self):
        """初始化教育Agent"""
        super().__init__("EduAgent")
        self.set_description("负责处理教育相关问题的Agent")
        
        # 获取模型配置（支持A/B测试）
        self.model_config = model_manager.get_agent_model_config("edu_agent")
        model_name = self.model_config.get("model_name", "qwen:0.5b")
        temperature = self.model_config.get("temperature", 0.7)
        
        # 初始化Ollama模型
        self.llm = Ollama(model=model_name, temperature=temperature)
        
        # 创建教育助手提示模板
        edu_template = """
        你是一个专门为儿童设计的教育助手AI。你的任务是帮助孩子们学习各种学科知识。
        请用简单易懂的语言回答问题，适合儿童理解。
        
        用户的年级是: {grade}
        用户的问题是: {question}
        
        请提供一个清晰、准确且适合儿童理解的回答:
        """
        
        self.prompt = PromptTemplate(
            input_variables=["grade", "question"],
            template=edu_template
        )
        
        # 创建链条
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        self.set_chain(self.chain)
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理教育相关请求
        
        Args:
            input_data (Dict[str, Any]): 输入数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        user_text = input_data.get('text', '')
        user_grade = input_data.get('grade', '小学')
        user_id = input_data.get('user_id', 'default_user')
        
        # 获取用户特定的模型配置（支持A/B测试）
        model_config = model_manager.get_agent_model_config("edu_agent", user_id)
        model_name = model_config.get("model_name")
        
        # 如果模型配置发生变化，重新初始化模型
        if model_name != self.llm.model:
            self.llm = Ollama(model=model_name, temperature=self.model_config.get("temperature", 0.7))
            self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
            self.set_chain(self.chain)
        
        # 使用LangChain生成响应
        try:
            response_text = self.chain.run({
                "grade": user_grade,
                "question": user_text
            })
        except Exception as e:
            # 如果LangChain调用失败，使用备用响应
            response_text = self._generate_educational_response(user_text)
        
        return {
            'agent': self.name,
            'response': response_text,
            'status': 'success'
        }
    
    def _generate_educational_response(self, user_text: str) -> str:
        """
        生成教育相关响应（备用方法）
        
        Args:
            user_text (str): 用户输入文本
            
        Returns:
            str: 生成的响应文本
        """
        # 这里应该调用实际的AI模型来生成响应
        # 目前只是一个模拟实现
        
        if '你好' in user_text or '你好' in user_text:
            return '你好！我是你的学习助手，有什么我可以帮你的吗？'
        elif '数学' in user_text:
            return '数学是一门研究数量、结构、空间以及变化等概念的学科。你想了解数学的哪个方面呢？'
        elif '语文' in user_text:
            return '语文是学习语言文字运用的课程，包括听说读写各个方面。你想练习哪一部分呢？'
        elif '英语' in user_text:
            return '英语是世界上使用最广泛的语言之一。学习英语可以帮助你与世界各地的人交流。'
        else:
            return '我是你的教育助手，我可以帮助你解答学习中的问题。请问你想了解什么内容呢？'