#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
辅助函数
"""

import re
import random
from typing import Any, List, Dict
from datetime import datetime


class Helper:
    """
    辅助函数类，提供各种通用工具函数
    """
    
    @staticmethod
    def is_valid_user_id(user_id: str) -> bool:
        """
        验证用户ID是否有效
        
        Args:
            user_id (str): 用户ID
            
        Returns:
            bool: 用户ID是否有效
        """
        if not user_id:
            return False
        # 用户ID应该只包含字母、数字、下划线和连字符，长度在3-50之间
        pattern = r'^[a-zA-Z0-9_-]{3,50}$'
        return bool(re.match(pattern, user_id))
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        清理用户输入，移除潜在的危险字符
        
        Args:
            text (str): 原始输入
            
        Returns:
            str: 清理后的输入
        """
        if not text:
            return ""
        
        # 移除或转义特殊字符
        # 这里只是一个基础实现，实际应用中可能需要更复杂的清理
        sanitized = text.strip()
        # 移除多余的空白字符
        sanitized = re.sub(r'\s+', ' ', sanitized)
        return sanitized
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 1000) -> str:
        """
        截断文本到指定长度
        
        Args:
            text (str): 原始文本
            max_length (int): 最大长度
            
        Returns:
            str: 截断后的文本
        """
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    @staticmethod
    def format_timestamp(timestamp: datetime) -> str:
        """
        格式化时间戳
        
        Args:
            timestamp (datetime): 时间戳
            
        Returns:
            str: 格式化后的时间戳
        """
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def generate_session_id() -> str:
        """
        生成会话ID
        
        Returns:
            str: 会话ID
        """
        timestamp = int(datetime.now().timestamp() * 1000000)
        random_part = random.randint(100000, 999999)
        return f"{timestamp}-{random_part}"
    
    @staticmethod
    def calculate_age(birth_date: datetime) -> int:
        """
        根据出生日期计算年龄
        
        Args:
            birth_date (datetime): 出生日期
            
        Returns:
            int: 年龄
        """
        today = datetime.today()
        age = today.year - birth_date.year
        # 检查是否还没过生日
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age
    
    @staticmethod
    def is_child_user(age: int) -> bool:
        """
        判断是否为儿童用户（12岁以下）
        
        Args:
            age (int): 年龄
            
        Returns:
            bool: 是否为儿童用户
        """
        return 3 <= age <= 12
    
    @staticmethod
    def get_age_group(age: int) -> str:
        """
        根据年龄获取年龄组
        
        Args:
            age (int): 年龄
            
        Returns:
            str: 年龄组
        """
        if 3 <= age <= 6:
            return "幼儿"
        elif 7 <= age <= 12:
            return "儿童"
        elif 13 <= age <= 17:
            return "青少年"
        else:
            return "其他"
    
    @staticmethod
    def filter_sensitive_content(text: str) -> str:
        """
        过滤敏感内容
        
        Args:
            text (str): 原始文本
            
        Returns:
            str: 过滤后的文本
        """
        # 这里应该实现实际的敏感内容过滤逻辑
        # 目前只是一个示例实现
        sensitive_patterns = [
            r'\d{11}',  # 手机号
            r'\d{18}|\d{17}[Xx]',  # 身份证号
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'  # 邮箱
        ]
        
        filtered_text = text
        for pattern in sensitive_patterns:
            filtered_text = re.sub(pattern, '*' * 6, filtered_text)
        
        return filtered_text
    
    @staticmethod
    def validate_grade(grade: str) -> bool:
        """
        验证年级是否有效
        
        Args:
            grade (str): 年级
            
        Returns:
            bool: 年级是否有效
        """
        valid_grades = [
            "幼儿园小班", "幼儿园中班", "幼儿园大班",
            "一年级", "二年级", "三年级", "四年级", "五年级", "六年级",
            "初一", "初二", "初三",
            "高一", "高二", "高三"
        ]
        return grade in valid_grades
    
    @staticmethod
    def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """
        扁平化嵌套字典
        
        Args:
            d (Dict[str, Any]): 嵌套字典
            parent_key (str): 父键
            sep (str): 分隔符
            
        Returns:
            Dict[str, Any]: 扁平化后的字典
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(Helper.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)