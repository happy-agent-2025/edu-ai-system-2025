#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置加载工具
"""

import yaml
import json
import os
from typing import Dict, Any, Optional


class ConfigLoader:
    """
    配置加载器类，支持YAML和JSON格式配置文件
    """
    
    @staticmethod
    def load_yaml_config(file_path: str) -> Dict[str, Any]:
        """
        加载YAML格式配置文件
        
        Args:
            file_path (str): 配置文件路径
            
        Returns:
            Dict[str, Any]: 配置数据
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"配置文件未找到: {file_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"解析YAML配置文件出错: {e}")
            return {}
        except Exception as e:
            print(f"加载YAML配置文件时出错: {e}")
            return {}
    
    @staticmethod
    def load_json_config(file_path: str) -> Dict[str, Any]:
        """
        加载JSON格式配置文件
        
        Args:
            file_path (str): 配置文件路径
            
        Returns:
            Dict[str, Any]: 配置数据
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件未找到: {file_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"解析JSON配置文件出错: {e}")
            return {}
        except Exception as e:
            print(f"加载JSON配置文件时出错: {e}")
            return {}
    
    @staticmethod
    def load_config(file_path: str) -> Dict[str, Any]:
        """
        自动识别格式并加载配置文件
        
        Args:
            file_path (str): 配置文件路径
            
        Returns:
            Dict[str, Any]: 配置数据
        """
        if not os.path.exists(file_path):
            print(f"配置文件不存在: {file_path}")
            return {}
        
        _, ext = os.path.splitext(file_path)
        
        if ext.lower() in ['.yaml', '.yml']:
            return ConfigLoader.load_yaml_config(file_path)
        elif ext.lower() == '.json':
            return ConfigLoader.load_json_config(file_path)
        else:
            print(f"不支持的配置文件格式: {ext}")
            return {}
    
    @staticmethod
    def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
        """
        从配置字典中获取指定路径的值
        
        Args:
            config (Dict[str, Any]): 配置字典
            key_path (str): 键路径，使用点号分隔，如 'database.host'
            default (Any): 默认值
            
        Returns:
            Any: 配置值
        """
        keys = key_path.split('.')
        current = config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    @staticmethod
    def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并多个配置字典
        
        Args:
            *configs (Dict[str, Any]): 配置字典列表
            
        Returns:
            Dict[str, Any]: 合并后的配置字典
        """
        merged = {}
        for config in configs:
            merged.update(config)
        return merged


# 全局配置实例
config_loader = ConfigLoader()