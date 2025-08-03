#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库查询
"""

from typing import List, Dict, Any, Optional
from backend.database.manager import DatabaseManager
from backend.database.models import User, Conversation, SafetyLog


class DatabaseQueries:
    """
    数据库查询类，封装常用的数据库查询操作
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        初始化数据库查询类
        
        Args:
            db_manager (DatabaseManager): 数据库管理器实例
        """
        self.db = db_manager
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        根据用户ID获取用户信息
        
        Args:
            user_id (str): 用户ID
            
        Returns:
            Optional[User]: 用户对象，如果未找到则返回None
        """
        user_data = self.db.get_user(user_id)
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def get_user_conversation_history(self, user_id: str, limit: int = 10) -> List[Conversation]:
        """
        获取用户对话历史
        
        Args:
            user_id (str): 用户ID
            limit (int): 返回记录数量限制
            
        Returns:
            List[Conversation]: 对话历史记录列表
        """
        conversation_data_list = self.db.get_conversation_history(user_id, limit)
        return [Conversation.from_dict(data) for data in conversation_data_list]
    
    def get_recent_safety_violations(self, limit: int = 50) -> List[SafetyLog]:
        """
        获取最近的安全违规记录
        
        Args:
            limit (int): 返回记录数量限制
            
        Returns:
            List[SafetyLog]: 安全违规记录列表
        """
        safety_data_list = self.db.get_safety_violations(limit)
        return [SafetyLog.from_dict(data) for data in safety_data_list]
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """
        获取用户统计信息
        
        Returns:
            Dict[str, Any]: 用户统计信息
        """
        # 获取用户总数
        result = self.db.execute_query("SELECT COUNT(*) as total FROM users")
        total_users = result[0]['total'] if result else 0
        
        # 获取活跃用户数（最近30天有对话的用户）
        result = self.db.execute_query('''
            SELECT COUNT(DISTINCT user_id) as active_users 
            FROM conversations 
            WHERE timestamp > datetime('now', '-30 days')
        ''')
        active_users = result[0]['active_users'] if result else 0
        
        # 获取各年级用户分布
        result = self.db.execute_query('''
            SELECT grade, COUNT(*) as count 
            FROM users 
            WHERE grade IS NOT NULL 
            GROUP BY grade 
            ORDER BY count DESC
        ''')
        grade_distribution = {row['grade']: row['count'] for row in result}
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'active_user_rate': round(active_users / total_users, 2) if total_users > 0 else 0,
            'grade_distribution': grade_distribution
        }
    
    def get_conversation_statistics(self) -> Dict[str, Any]:
        """
        获取对话统计信息
        
        Returns:
            Dict[str, Any]: 对话统计信息
        """
        # 获取总对话数
        result = self.db.execute_query("SELECT COUNT(*) as total FROM conversations")
        total_conversations = result[0]['total'] if result else 0
        
        # 获取各Agent处理的对话数
        result = self.db.execute_query('''
            SELECT agent_name, COUNT(*) as count 
            FROM conversations 
            GROUP BY agent_name 
            ORDER BY count DESC
        ''')
        agent_distribution = {row['agent_name']: row['count'] for row in result}
        
        # 获取最近7天每日对话数
        result = self.db.execute_query('''
            SELECT DATE(timestamp) as date, COUNT(*) as count 
            FROM conversations 
            WHERE timestamp > datetime('now', '-7 days') 
            GROUP BY DATE(timestamp) 
            ORDER BY date
        ''')
        daily_conversations = {row['date']: row['count'] for row in result}
        
        return {
            'total_conversations': total_conversations,
            'agent_distribution': agent_distribution,
            'daily_conversations': daily_conversations
        }
    
    def get_safety_statistics(self) -> Dict[str, Any]:
        """
        获取安全统计信息
        
        Returns:
            Dict[str, Any]: 安全统计信息
        """
        # 获取总安全检查数和违规数
        result = self.db.execute_query("SELECT COUNT(*) as total FROM safety_logs")
        total_violations = result[0]['total'] if result else 0
        
        # 获取违规类型分布
        result = self.db.execute_query('''
            SELECT violation_reason, COUNT(*) as count 
            FROM safety_logs 
            GROUP BY violation_reason 
            ORDER BY count DESC
        ''')
        violation_distribution = {row['violation_reason']: row['count'] for row in result}
        
        # 获取各Agent的安全违规数
        result = self.db.execute_query('''
            SELECT agent_name, COUNT(*) as count 
            FROM safety_logs 
            GROUP BY agent_name 
            ORDER BY count DESC
        ''')
        agent_violations = {row['agent_name']: row['count'] for row in result}
        
        return {
            'total_violations': total_violations,
            'violation_distribution': violation_distribution,
            'agent_violations': agent_violations
        }
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """
        获取系统统计信息
        
        Returns:
            Dict[str, Any]: 系统统计信息
        """
        user_stats = self.get_user_statistics()
        conversation_stats = self.get_conversation_statistics()
        safety_stats = self.get_safety_statistics()
        
        return {
            'users': user_stats,
            'conversations': conversation_stats,
            'safety': safety_stats,
            'timestamp': self.db.execute_query("SELECT CURRENT_TIMESTAMP as now")[0]['now']
        }
    
    def search_conversations(self, keyword: str, limit: int = 50) -> List[Conversation]:
        """
        搜索包含关键词的对话记录
        
        Args:
            keyword (str): 搜索关键词
            limit (int): 返回记录数量限制
            
        Returns:
            List[Conversation]: 匹配的对话记录列表
        """
        query = '''
            SELECT * FROM conversations 
            WHERE user_input LIKE ? OR agent_response LIKE ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        '''
        params = (f'%{keyword}%', f'%{keyword}%', limit)
        
        conversation_data_list = self.db.execute_query(query, params)
        return [Conversation.from_dict(data) for data in conversation_data_list]
    
    def get_conversations_by_date_range(self, start_date: str, end_date: str) -> List[Conversation]:
        """
        获取指定日期范围内的对话记录
        
        Args:
            start_date (str): 开始日期 (YYYY-MM-DD)
            end_date (str): 结束日期 (YYYY-MM-DD)
            
        Returns:
            List[Conversation]: 对话记录列表
        """
        query = '''
            SELECT * FROM conversations 
            WHERE DATE(timestamp) BETWEEN ? AND ? 
            ORDER BY timestamp DESC
        '''
        params = (start_date, end_date)
        
        conversation_data_list = self.db.execute_query(query, params)
        return [Conversation.from_dict(data) for data in conversation_data_list]