#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
记忆Agent
"""

from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent
import json
import os
from datetime import datetime


class MemoryAgent(BaseAgent):
    """
    记忆Agent负责存储和检索对话历史与用户信息
    """
    
    def __init__(self):
        """初始化记忆Agent"""
        super().__init__("MemoryAgent")
        self.set_description("负责存储和检索对话历史的Agent")
        
        # 内存存储
        self.conversations = {}
        self.user_profiles = {}
        
        # 持久化文件路径
        self.memory_file = "memory_data.json"
        
        # 加载历史数据
        self._load_memory()
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理记忆相关请求
        
        Args:
            input_data (Dict[str, Any]): 输入数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        action = input_data.get('action', 'retrieve')
        user_id = input_data.get('user_id', 'default_user')
        
        if action == 'store':
            # 存储对话
            conversation = input_data.get('conversation', {})
            self._store_conversation(user_id, conversation)
            return {
                'agent': self.name,
                'status': 'stored',
                'message': '对话已存储'
            }
        elif action == 'retrieve':
            # 检索对话历史
            history = self._retrieve_conversation_history(user_id)
            return {
                'agent': self.name,
                'status': 'retrieved',
                'history': history
            }
        else:
            return {
                'agent': self.name,
                'status': 'error',
                'message': '未知的操作类型'
            }
    
    def _store_conversation(self, user_id: str, conversation: Dict[str, Any]):
        """
        存储对话
        
        Args:
            user_id (str): 用户ID
            conversation (Dict[str, Any]): 对话内容
        """
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        # 添加时间戳
        conversation['timestamp'] = datetime.now().isoformat()
        self.conversations[user_id].append(conversation)
        
        # 限制历史记录数量，避免内存过大
        if len(self.conversations[user_id]) > 100:
            self.conversations[user_id] = self.conversations[user_id][-50:]
        
        # 保存到文件
        self._save_memory()
    
    def _retrieve_conversation_history(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        检索对话历史
        
        Args:
            user_id (str): 用户ID
            limit (int): 返回的历史记录数量限制
            
        Returns:
            List[Dict[str, Any]]: 对话历史
        """
        if user_id in self.conversations:
            # 返回最近的几条记录
            return self.conversations[user_id][-limit:]
        else:
            return []
    
    def _save_memory(self):
        """将记忆数据保存到文件"""
        try:
            data = {
                'conversations': self.conversations,
                'user_profiles': self.user_profiles
            }
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存记忆数据时出错: {e}")
    
    def _load_memory(self):
        """从文件加载记忆数据"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversations = data.get('conversations', {})
                    self.user_profiles = data.get('user_profiles', {})
            except Exception as e:
                print(f"加载记忆数据时出错: {e}")
                # 初始化为空字典
                self.conversations = {}
                self.user_profiles = {}