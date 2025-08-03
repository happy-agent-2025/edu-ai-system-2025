#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
实时监控
"""

import time
import threading
from typing import Dict, Any, Callable
from collections import defaultdict, deque
from datetime import datetime, timedelta


class SystemMonitor:
    """
    系统实时监控类
    """
    
    def __init__(self):
        """初始化系统监控器"""
        self.metrics = defaultdict(lambda: deque(maxlen=1000))  # 限制存储1000个数据点
        self.is_monitoring = False
        self.monitoring_thread = None
        self.alert_callbacks = []
        
    def start_monitoring(self):
        """开始监控"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitor_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
    
    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            # 检查各项指标是否超过阈值
            self._check_alerts()
            time.sleep(1)  # 每秒检查一次
    
    def record_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """
        记录指标数据
        
        Args:
            metric_name (str): 指标名称
            value (float): 指标值
            tags (Dict[str, str], optional): 标签
        """
        timestamp = datetime.now()
        data_point = {
            'timestamp': timestamp,
            'value': value,
            'tags': tags or {}
        }
        self.metrics[metric_name].append(data_point)
    
    def get_metric_stats(self, metric_name: str, time_window_minutes: int = 5) -> Dict[str, Any]:
        """
        获取指标统计信息
        
        Args:
            metric_name (str): 指标名称
            time_window_minutes (int): 时间窗口（分钟）
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        if metric_name not in self.metrics:
            return {}
        
        # 计算时间窗口的开始时间
        window_start = datetime.now() - timedelta(minutes=time_window_minutes)
        
        # 筛选时间窗口内的数据
        recent_data = [
            point for point in self.metrics[metric_name] 
            if point['timestamp'] >= window_start
        ]
        
        if not recent_data:
            return {}
        
        values = [point['value'] for point in recent_data]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'latest': values[-1]
        }
    
    def add_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        添加告警回调函数
        
        Args:
            callback (Callable): 告警回调函数
        """
        self.alert_callbacks.append(callback)
    
    def _check_alerts(self):
        """检查并触发告警"""
        # 检查响应时间是否过长
        response_time_stats = self.get_metric_stats('response_time')
        if response_time_stats and response_time_stats.get('avg', 0) > 5.0:
            alert_info = {
                'metric': 'response_time',
                'value': response_time_stats['avg'],
                'threshold': 5.0,
                'message': '平均响应时间过长'
            }
            self._trigger_alert('performance', alert_info)
        
        # 检查错误率是否过高
        error_rate_stats = self.get_metric_stats('error_rate')
        if error_rate_stats and error_rate_stats.get('avg', 0) > 0.05:
            alert_info = {
                'metric': 'error_rate',
                'value': error_rate_stats['avg'],
                'threshold': 0.05,
                'message': '错误率过高'
            }
            self._trigger_alert('performance', alert_info)
    
    def _trigger_alert(self, alert_type: str, alert_info: Dict[str, Any]):
        """
        触发告警
        
        Args:
            alert_type (str): 告警类型
            alert_info (Dict[str, Any]): 告警信息
        """
        for callback in self.alert_callbacks:
            try:
                callback(alert_type, alert_info)
            except Exception as e:
                print(f"告警回调执行出错: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        获取系统状态概览
        
        Returns:
            Dict[str, Any]: 系统状态信息
        """
        return {
            'is_monitoring': self.is_monitoring,
            'metrics_count': len(self.metrics),
            'response_time_stats': self.get_metric_stats('response_time'),
            'error_rate_stats': self.get_metric_stats('error_rate'),
            'timestamp': datetime.now().isoformat()
        }