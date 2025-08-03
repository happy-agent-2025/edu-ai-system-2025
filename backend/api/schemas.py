#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API数据模型
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """聊天请求数据模型"""
    text: str
    user_id: str = "default_user"
    emotion: Optional[str] = None


class ChatResponse(BaseModel):
    """聊天响应数据模型"""
    status: str
    response: str
    agent: str


class ConversationHistoryItem(BaseModel):
    """对话历史项数据模型"""
    id: Optional[int] = None
    user_id: str
    user_input: str
    agent_response: str
    agent_name: str
    safety_check: Optional[str] = None
    timestamp: Optional[datetime] = None


class UserHistoryResponse(BaseModel):
    """用户历史响应数据模型"""
    status: str
    history: List[ConversationHistoryItem]


class SafetyViolationItem(BaseModel):
    """安全违规项数据模型"""
    id: Optional[int] = None
    user_id: Optional[str] = None
    user_input: str
    agent_response: str
    violation_reason: str
    agent_name: str
    timestamp: Optional[datetime] = None


class SafetyViolationsResponse(BaseModel):
    """安全违规响应数据模型"""
    status: str
    violations: List[SafetyViolationItem]


class SystemStatsResponse(BaseModel):
    """系统统计响应数据模型"""
    status: str
    stats: Dict[str, Any]


class SearchRequest(BaseModel):
    """搜索请求数据模型"""
    query: str
    limit: int = 50


class SearchResultItem(BaseModel):
    """搜索结果项数据模型"""
    id: Optional[int] = None
    user_id: str
    user_input: str
    agent_response: str
    agent_name: str
    safety_check: Optional[str] = None
    timestamp: Optional[datetime] = None


class SearchResponse(BaseModel):
    """搜索响应数据模型"""
    status: str
    results: List[SearchResultItem]
    count: int


class HealthCheckResponse(BaseModel):
    """健康检查响应数据模型"""
    status: str
    message: str


class UserStatistics(BaseModel):
    """用户统计数据模型"""
    total_users: int
    active_users: int
    active_user_rate: float
    grade_distribution: Dict[str, int]


class ConversationStatistics(BaseModel):
    """对话统计数据模型"""
    total_conversations: int
    agent_distribution: Dict[str, int]
    daily_conversations: Dict[str, int]


class SafetyStatistics(BaseModel):
    """安全统计数据模型"""
    total_violations: int
    violation_distribution: Dict[str, int]
    agent_violations: Dict[str, int]