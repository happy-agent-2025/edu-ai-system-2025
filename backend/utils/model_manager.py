#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模型管理工具
支持热更新、A/B测试和版本回滚功能
"""

import os
import yaml
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ModelVersion:
    """模型版本信息"""
    version: str
    model_name: str
    path: str
    created_at: datetime
    metrics: Dict[str, float]
    is_active: bool = False


class ModelManager:
    """模型管理器"""
    
    def __init__(self, config_path: str = "configs/"):
        """初始化模型管理器"""
        self.config_path = config_path
        self.models = {}
        self.ab_tests = {}
        self.versions = {}
        self._load_configs()
    
    def _load_configs(self):
        """加载配置文件"""
        # 加载Agent配置
        agent_config_path = os.path.join(self.config_path, "agent.yaml")
        if os.path.exists(agent_config_path):
            with open(agent_config_path, 'r', encoding='utf-8') as f:
                self.agent_config = yaml.safe_load(f)
        
        # 加载音频配置
        audio_config_path = os.path.join(self.config_path, "audio.yaml")
        if os.path.exists(audio_config_path):
            with open(audio_config_path, 'r', encoding='utf-8') as f:
                self.audio_config = yaml.safe_load(f)
    
    def register_model(self, model_name: str, model_path: str, 
                      metrics: Dict[str, float] = None) -> str:
        """
        注册新模型版本
        
        Args:
            model_name: 模型名称
            model_path: 模型路径
            metrics: 模型评估指标
            
        Returns:
            str: 版本号
        """
        # 生成版本号
        version_content = f"{model_name}_{model_path}_{datetime.now().isoformat()}"
        version = hashlib.md5(version_content.encode()).hexdigest()[:8]
        
        # 创建模型版本
        model_version = ModelVersion(
            version=version,
            model_name=model_name,
            path=model_path,
            created_at=datetime.now(),
            metrics=metrics or {}
        )
        
        # 存储版本信息
        if model_name not in self.versions:
            self.versions[model_name] = []
        self.versions[model_name].append(model_version)
        
        return version
    
    def get_model_version(self, model_name: str, version: str = None) -> Optional[ModelVersion]:
        """
        获取模型版本
        
        Args:
            model_name: 模型名称
            version: 版本号，如果为None则返回当前活跃版本
            
        Returns:
            ModelVersion: 模型版本信息
        """
        if model_name not in self.versions:
            return None
            
        versions = self.versions[model_name]
        if not versions:
            return None
            
        if version:
            # 查找指定版本
            for mv in versions:
                if mv.version == version:
                    return mv
        else:
            # 返回活跃版本
            for mv in versions:
                if mv.is_active:
                    return mv
            # 如果没有活跃版本，返回最新版本
            return versions[-1]
            
        return None
    
    def activate_version(self, model_name: str, version: str) -> bool:
        """
        激活指定版本
        
        Args:
            model_name: 模型名称
            version: 版本号
            
        Returns:
            bool: 是否成功激活
        """
        model_version = self.get_model_version(model_name, version)
        if not model_version:
            return False
            
        # 取消其他版本的激活状态
        if model_name in self.versions:
            for mv in self.versions[model_name]:
                mv.is_active = False
                
        # 激活指定版本
        model_version.is_active = True
        return True
    
    def rollback_version(self, model_name: str, steps: int = 1) -> bool:
        """
        回滚到之前的版本
        
        Args:
            model_name: 模型名称
            steps: 回滚步数
            
        Returns:
            bool: 是否成功回滚
        """
        if model_name not in self.versions:
            return False
            
        versions = self.versions[model_name]
        if len(versions) <= steps:
            return False
            
        # 找到当前活跃版本的索引
        current_index = -1
        for i, mv in enumerate(versions):
            if mv.is_active:
                current_index = i
                break
                
        # 如果没有活跃版本，使用最新版本
        if current_index == -1:
            current_index = len(versions) - 1
            
        # 计算回滚到的版本索引
        rollback_index = max(0, current_index - steps)
        
        # 激活回滚版本
        versions[rollback_index].is_active = True
        for i, mv in enumerate(versions):
            if i != rollback_index:
                mv.is_active = False
                
        return True
    
    def start_ab_test(self, test_name: str, model_variants: List[Dict[str, Any]]) -> bool:
        """
        启动A/B测试
        
        Args:
            test_name: 测试名称
            model_variants: 模型变体列表，每个包含name和traffic_percentage
            
        Returns:
            bool: 是否成功启动
        """
        # 验证流量分配
        total_percentage = sum(variant.get('traffic_percentage', 0) for variant in model_variants)
        if abs(total_percentage - 100) > 1:  # 允许1%的误差
            return False
            
        self.ab_tests[test_name] = {
            'variants': model_variants,
            'start_time': datetime.now(),
            'active': True
        }
        
        return True
    
    def get_ab_test_variant(self, test_name: str, user_id: str) -> Optional[str]:
        """
        根据用户ID获取A/B测试变体
        
        Args:
            test_name: 测试名称
            user_id: 用户ID
            
        Returns:
            str: 模型变体名称
        """
        if test_name not in self.ab_tests:
            return None
            
        test_config = self.ab_tests[test_name]
        if not test_config['active']:
            return None
            
        # 使用用户ID哈希值进行流量分配
        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        traffic_position = user_hash % 100
        
        # 根据流量分配确定变体
        cumulative_percentage = 0
        for variant in test_config['variants']:
            cumulative_percentage += variant.get('traffic_percentage', 0)
            if traffic_position <= cumulative_percentage:
                return variant.get('name')
                
        # 默认返回第一个变体
        return test_config['variants'][0].get('name') if test_config['variants'] else None
    
    def stop_ab_test(self, test_name: str) -> bool:
        """
        停止A/B测试
        
        Args:
            test_name: 测试名称
            
        Returns:
            bool: 是否成功停止
        """
        if test_name not in self.ab_tests:
            return False
            
        self.ab_tests[test_name]['active'] = False
        return True
    
    def get_agent_model_config(self, agent_type: str, user_id: str = None) -> Dict[str, Any]:
        """
        获取Agent模型配置，支持A/B测试
        
        Args:
            agent_type: Agent类型 (edu_agent, emotion_agent, safety_agent)
            user_id: 用户ID，用于A/B测试
            
        Returns:
            Dict[str, Any]: 模型配置
        """
        # 获取基础配置
        agent_config = self.agent_config.get(agent_type, {})
        model_name = agent_config.get('ollama_model', 'qwen:0.5b')
        temperature = agent_config.get('temperature', 0.7)
        
        # 检查是否有相关的A/B测试
        if user_id:
            for test_name, test_config in self.ab_tests.items():
                if test_config['active'] and agent_type in test_name:
                    variant = self.get_ab_test_variant(test_name, user_id)
                    if variant:
                        # 查找变体对应的模型
                        for v in test_config['variants']:
                            if v.get('name') == variant:
                                model_name = v.get('model', model_name)
                                break
                        break
        
        return {
            'model_name': model_name,
            'temperature': temperature
        }
    
    def get_audio_model_config(self, service_type: str) -> Dict[str, Any]:
        """
        获取音频服务模型配置
        
        Args:
            service_type: 服务类型 (stt, tts, verification)
            
        Returns:
            Dict[str, Any]: 模型配置
        """
        audio_config = self.audio_config.get('speech_recognition', {}) if service_type == 'stt' \
                      else self.audio_config.get('speech_synthesis', {}) if service_type == 'tts' \
                      else self.audio_config.get('voice_verification', {})
                      
        return {
            'model': audio_config.get('model'),
            'model_path': self.audio_config.get('model_paths', {}).get(
                audio_config.get('model', '').replace('-', '_'), ''
            )
        }


# 全局模型管理器实例
model_manager = ModelManager()