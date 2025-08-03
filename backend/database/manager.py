#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库管理器
"""

import sqlite3
import os
from typing import Dict, Any, List
from contextlib import contextmanager


class DatabaseManager:
    """
    数据库管理器类，负责数据库连接和基本操作
    """
    
    def __init__(self, db_path: str = "edu_ai.db"):
        """
        初始化数据库管理器
        
        Args:
            db_path (str): 数据库文件路径
        """
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    name TEXT,
                    age INTEGER,
                    grade TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建对话记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    user_input TEXT,
                    agent_response TEXT,
                    agent_name TEXT,
                    safety_check TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建安全日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS safety_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    user_input TEXT,
                    agent_response TEXT,
                    violation_reason TEXT,
                    agent_name TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建系统日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    log_level TEXT,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """
        获取数据库连接的上下文管理器
        
        Yields:
            sqlite3.Connection: 数据库连接
        """
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            raise e
        else:
            conn.commit()
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        执行查询语句
        
        Args:
            query (str): SQL查询语句
            params (tuple): 查询参数
            
        Returns:
            List[Dict[str, Any]]: 查询结果
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # 将Row对象转换为字典
            return [dict(row) for row in rows]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        执行更新语句（INSERT, UPDATE, DELETE）
        
        Args:
            query (str): SQL更新语句
            params (tuple): 更新参数
            
        Returns:
            int: 受影响的行数
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount
    
    def insert_user(self, user_data: Dict[str, Any]) -> bool:
        """
        插入用户数据
        
        Args:
            user_data (Dict[str, Any]): 用户数据
            
        Returns:
            bool: 插入是否成功
        """
        query = '''
            INSERT OR REPLACE INTO users 
            (user_id, name, age, grade) 
            VALUES (?, ?, ?, ?)
        '''
        params = (
            user_data.get('user_id'),
            user_data.get('name'),
            user_data.get('age'),
            user_data.get('grade')
        )
        
        try:
            self.execute_update(query, params)
            return True
        except Exception as e:
            print(f"插入用户数据时出错: {e}")
            return False
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户信息
        
        Args:
            user_id (str): 用户ID
            
        Returns:
            Dict[str, Any]: 用户信息
        """
        query = "SELECT * FROM users WHERE user_id = ?"
        result = self.execute_query(query, (user_id,))
        return result[0] if result else {}
    
    def insert_conversation(self, conversation_data: Dict[str, Any]) -> bool:
        """
        插入对话记录
        
        Args:
            conversation_data (Dict[str, Any]): 对话数据
            
        Returns:
            bool: 插入是否成功
        """
        query = '''
            INSERT INTO conversations 
            (user_id, user_input, agent_response, agent_name, safety_check) 
            VALUES (?, ?, ?, ?, ?)
        '''
        params = (
            conversation_data.get('user_id'),
            conversation_data.get('user_input'),
            conversation_data.get('agent_response'),
            conversation_data.get('agent_name'),
            conversation_data.get('safety_check')
        )
        
        try:
            self.execute_update(query, params)
            return True
        except Exception as e:
            print(f"插入对话记录时出错: {e}")
            return False
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取用户对话历史
        
        Args:
            user_id (str): 用户ID
            limit (int): 返回记录数量限制
            
        Returns:
            List[Dict[str, Any]]: 对话历史记录
        """
        query = '''
            SELECT * FROM conversations 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        '''
        return self.execute_query(query, (user_id, limit))
    
    def insert_safety_log(self, safety_data: Dict[str, Any]) -> bool:
        """
        插入安全日志
        
        Args:
            safety_data (Dict[str, Any]): 安全日志数据
            
        Returns:
            bool: 插入是否成功
        """
        query = '''
            INSERT INTO safety_logs 
            (user_id, user_input, agent_response, violation_reason, agent_name) 
            VALUES (?, ?, ?, ?, ?)
        '''
        params = (
            safety_data.get('user_id'),
            safety_data.get('user_input'),
            safety_data.get('agent_response'),
            safety_data.get('violation_reason'),
            safety_data.get('agent_name')
        )
        
        try:
            self.execute_update(query, params)
            return True
        except Exception as e:
            print(f"插入安全日志时出错: {e}")
            return False
    
    def get_safety_violations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取安全违规记录
        
        Args:
            limit (int): 返回记录数量限制
            
        Returns:
            List[Dict[str, Any]]: 安全违规记录
        """
        query = '''
            SELECT * FROM safety_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        '''
        return self.execute_query(query, (limit,))
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        获取数据库统计信息
        
        Returns:
            Dict[str, Any]: 数据库统计信息
        """
        stats = {}
        
        # 用户总数
        result = self.execute_query("SELECT COUNT(*) as count FROM users")
        stats['total_users'] = result[0]['count'] if result else 0
        
        # 对话记录总数
        result = self.execute_query("SELECT COUNT(*) as count FROM conversations")
        stats['total_conversations'] = result[0]['count'] if result else 0
        
        # 安全违规总数
        result = self.execute_query("SELECT COUNT(*) as count FROM safety_logs")
        stats['total_safety_violations'] = result[0]['count'] if result else 0
        
        return stats