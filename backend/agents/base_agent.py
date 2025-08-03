#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Agent基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseAgent(ABC):
    """
    所有Agent的基类，定义了Agent的基本接口和通用功能
    """
    
    def __init__(self, name: str):
        """
        初始化Agent
        
        Args:
            name (str): Agent名称
        """
        self.name = name
        self.description = ""
        
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理输入数据的核心方法，每个子类必须实现
        
        Args:
            input_data (Dict[str, Any]): 输入数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        pass
        
    def get_name(self) -> str:
        """
        获取Agent名称
        
        Returns:
            str: Agent名称
        """
        return self.name
        
    def get_description(self) -> str:
        """
        获取Agent描述
        
        Returns:
            str: Agent描述
        """
        return self.description
        
    def set_description(self, description: str):
        """
        设置Agent描述
        
        Args:
            description (str): 描述信息
        """
        self.description = description