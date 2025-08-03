#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据模型
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class User:
    """用户数据模型"""
    id: Optional[int] = None
    user_id: str = ""
    name: Optional[str] = None
    age: Optional[int] = None
    grade: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """从字典创建User实例"""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id', ''),
            name=data.get('name'),
            age=data.get('age'),
            grade=data.get('grade'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """将User实例转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'age': self.age,
            'grade': self.grade,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class Conversation:
    """对话记录数据模型"""
    id: Optional[int] = None
    user_id: str = ""
    user_input: str = ""
    agent_response: str = ""
    agent_name: str = ""
    safety_check: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """从字典创建Conversation实例"""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id', ''),
            user_input=data.get('user_input', ''),
            agent_response=data.get('agent_response', ''),
            agent_name=data.get('agent_name', ''),
            safety_check=data.get('safety_check'),
            timestamp=data.get('timestamp')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """将Conversation实例转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_input': self.user_input,
            'agent_response': self.agent_response,
            'agent_name': self.agent_name,
            'safety_check': self.safety_check,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


@dataclass
class SafetyLog:
    """安全日志数据模型"""
    id: Optional[int] = None
    user_id: Optional[str] = None
    user_input: str = ""
    agent_response: str = ""
    violation_reason: str = ""
    agent_name: str = ""
    timestamp: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SafetyLog':
        """从字典创建SafetyLog实例"""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            user_input=data.get('user_input', ''),
            agent_response=data.get('agent_response', ''),
            violation_reason=data.get('violation_reason', ''),
            agent_name=data.get('agent_name', ''),
            timestamp=data.get('timestamp')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """将SafetyLog实例转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_input': self.user_input,
            'agent_response': self.agent_response,
            'violation_reason': self.violation_reason,
            'agent_name': self.agent_name,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


@dataclass
class SystemLog:
    """系统日志数据模型"""
    id: Optional[int] = None
    log_level: str = ""
    message: str = ""
    timestamp: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemLog':
        """从字典创建SystemLog实例"""
        return cls(
            id=data.get('id'),
            log_level=data.get('log_level', ''),
            message=data.get('message', ''),
            timestamp=data.get('timestamp')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """将SystemLog实例转换为字典"""
        return {
            'id': self.id,
            'log_level': self.log_level,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }