#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志工具
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict


class EduAILogger:
    """
    教育AI系统日志工具类
    """
    
    def __init__(self, log_dir: str = "logs"):
        """初始化日志工具"""
        self.log_dir = log_dir
        self._ensure_log_dir()
        
        # 创建日志记录器
        self.logger = logging.getLogger('EduAI')
        self.logger.setLevel(logging.DEBUG)
        
        # 创建文件处理器
        log_file = os.path.join(self.log_dir, f"edu_ai_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器到记录器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _ensure_log_dir(self):
        """确保日志目录存在"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def debug(self, message: str):
        """记录调试信息"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """记录一般信息"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录警告信息"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录错误信息"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """记录严重错误信息"""
        self.logger.critical(message)
    
    def log_interaction(self, user_id: str, user_input: str, agent_response: str, 
                       agent_name: str, safety_check: str = None):
        """
        记录用户交互日志
        
        Args:
            user_id (str): 用户ID
            user_input (str): 用户输入
            agent_response (str): Agent响应
            agent_name (str): 处理的Agent名称
            safety_check (str): 安全检查结果
        """
        interaction_log = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'user_input': user_input,
            'agent_response': agent_response,
            'agent_name': agent_name,
            'safety_check': safety_check
        }
        
        self.info(f"用户交互: {interaction_log}")
    
    def log_safety_violation(self, user_id: str, user_input: str, agent_response: str,
                           violation_reason: str, agent_name: str):
        """
        记录安全违规日志
        
        Args:
            user_id (str): 用户ID
            user_input (str): 用户输入
            agent_response (str): Agent响应
            violation_reason (str): 违规原因
            agent_name (str): 处理的Agent名称
        """
        violation_log = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'user_input': user_input,
            'agent_response': agent_response,
            'violation_reason': violation_reason,
            'agent_name': agent_name
        }
        
        self.warning(f"安全违规: {violation_log}")
    
    def log_system_event(self, event_type: str, details: Dict[str, Any]):
        """
        记录系统事件日志
        
        Args:
            event_type (str): 事件类型
            details (Dict[str, Any]): 事件详情
        """
        event_log = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details
        }
        
        self.info(f"系统事件: {event_log}")