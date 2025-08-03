#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
仪表板集成
"""

from typing import Dict, Any, List
import json
from datetime import datetime, timedelta


class DashboardIntegration:
    """
    仪表板集成类，用于向仪表板提供数据
    """
    
    def __init__(self, log_analyzer=None, system_monitor=None):
        """
        初始化仪表板集成
        
        Args:
            log_analyzer: 日志分析器实例
            system_monitor: 系统监控器实例
        """
        self.log_analyzer = log_analyzer
        self.system_monitor = system_monitor
    
    def get_realtime_metrics(self) -> Dict[str, Any]:
        """
        获取实时指标数据
        
        Returns:
            Dict[str, Any]: 实时指标数据
        """
        if not self.system_monitor:
            return {}
        
        return self.system_monitor.get_system_status()
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """
        获取用户统计信息
        
        Returns:
            Dict[str, Any]: 用户统计信息
        """
        if not self.log_analyzer:
            return {}
        
        return self.log_analyzer.get_user_interaction_stats()
    
    def get_system_performance(self, hours: int = 24) -> Dict[str, Any]:
        """
        获取系统性能数据
        
        Args:
            hours (int): 时间范围（小时）
            
        Returns:
            Dict[str, Any]: 系统性能数据
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        if not self.log_analyzer:
            return {}
        
        return self.log_analyzer.analyze_time_range(start_time, end_time)
    
    def get_top_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最常见的错误
        
        Args:
            limit (int): 返回错误数量限制
            
        Returns:
            List[Dict[str, Any]]: 错误列表
        """
        if not self.log_analyzer:
            return []
        
        error_summary = self.log_analyzer.get_error_summary()
        return error_summary[:limit]
    
    def get_agent_performance(self) -> Dict[str, Any]:
        """
        获取各Agent性能数据
        
        Returns:
            Dict[str, Any]: Agent性能数据
        """
        # 这里应该从日志中分析各Agent的性能
        # 目前返回模拟数据
        
        return {
            'edu_agent': {
                'response_time_avg': 1.2,
                'success_rate': 0.95,
                'total_requests': 1250
            },
            'emotion_agent': {
                'response_time_avg': 0.8,
                'success_rate': 0.98,
                'total_requests': 870
            },
            'meta_agent': {
                'response_time_avg': 0.1,
                'success_rate': 1.0,
                'total_requests': 2120
            },
            'safety_agent': {
                'response_time_avg': 0.05,
                'success_rate': 1.0,
                'total_requests': 2120
            }
        }
    
    def get_safety_report(self) -> Dict[str, Any]:
        """
        获取安全报告
        
        Returns:
            Dict[str, Any]: 安全报告
        """
        # 从日志中分析安全相关数据
        # 目前返回模拟数据
        
        return {
            'total_safety_checks': 2120,
            'approved_content': 2080,
            'rejected_content': 40,
            'rejection_rate': 0.019,
            'top_violations': [
                {'type': '隐私信息', 'count': 15},
                {'type': '不适当内容', 'count': 12},
                {'type': '暴力内容', 'count': 8},
                {'type': '危险行为', 'count': 5}
            ]
        }
    
    def get_all_dashboard_data(self) -> Dict[str, Any]:
        """
        获取所有仪表板数据
        
        Returns:
            Dict[str, Any]: 所有仪表板数据
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'realtime_metrics': self.get_realtime_metrics(),
            'user_statistics': self.get_user_statistics(),
            'system_performance': self.get_system_performance(),
            'top_errors': self.get_top_errors(),
            'agent_performance': self.get_agent_performance(),
            'safety_report': self.get_safety_report()
        }
    
    def export_dashboard_data(self, file_path: str):
        """
        导出仪表板数据到文件
        
        Args:
            file_path (str): 导出文件路径
        """
        data = self.get_all_dashboard_data()
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"导出仪表板数据时出错: {e}")