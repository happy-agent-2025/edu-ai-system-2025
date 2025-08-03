#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志分析
"""

import re
from typing import Dict, List, Any
from collections import defaultdict, Counter
from datetime import datetime, timedelta


class LogAnalyzer:
    """
    日志分析类，用于分析系统日志并生成报告
    """
    
    def __init__(self, log_file_path: str = None):
        """初始化日志分析器"""
        self.log_file_path = log_file_path
        self.logs = []
    
    def load_logs(self, log_file_path: str = None):
        """
        加载日志文件
        
        Args:
            log_file_path (str, optional): 日志文件路径
        """
        if log_file_path:
            self.log_file_path = log_file_path
        
        if not self.log_file_path:
            raise ValueError("未指定日志文件路径")
        
        self.logs = []
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parsed_log = self._parse_log_line(line.strip())
                    if parsed_log:
                        self.logs.append(parsed_log)
        except FileNotFoundError:
            print(f"日志文件未找到: {self.log_file_path}")
        except Exception as e:
            print(f"读取日志文件时出错: {e}")
    
    def _parse_log_line(self, line: str) -> Dict[str, Any]:
        """
        解析单行日志
        
        Args:
            line (str): 日志行
            
        Returns:
            Dict[str, Any]: 解析后的日志数据
        """
        # 日志格式: 2023-01-01 12:00:00 - EduAI - INFO - message
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - ([^-]+) - ([^-]+) - (.+)'
        match = re.match(pattern, line)
        
        if match:
            timestamp_str, logger_name, level, message = match.groups()
            try:
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                timestamp = datetime.now()
            
            return {
                'timestamp': timestamp,
                'logger_name': logger_name.strip(),
                'level': level.strip(),
                'message': message.strip()
            }
        
        return None
    
    def analyze_time_range(self, start_time: datetime = None, end_time: datetime = None) -> Dict[str, Any]:
        """
        分析指定时间范围内的日志
        
        Args:
            start_time (datetime, optional): 开始时间
            end_time (datetime, optional): 结束时间
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        if not self.logs:
            return {}
        
        # 筛选时间范围内的日志
        filtered_logs = self.logs
        if start_time:
            filtered_logs = [log for log in filtered_logs if log['timestamp'] >= start_time]
        if end_time:
            filtered_logs = [log for log in filtered_logs if log['timestamp'] <= end_time]
        
        if not filtered_logs:
            return {}
        
        # 统计日志级别分布
        level_counts = Counter(log['level'] for log in filtered_logs)
        
        # 统计日志来源分布
        logger_counts = Counter(log['logger_name'] for log in filtered_logs)
        
        # 分析错误日志
        error_logs = [log for log in filtered_logs if log['level'] in ['ERROR', 'CRITICAL']]
        
        # 分析用户交互日志
        interaction_logs = [log for log in filtered_logs if '用户交互' in log['message']]
        
        return {
            'total_logs': len(filtered_logs),
            'level_distribution': dict(level_counts),
            'logger_distribution': dict(logger_counts),
            'error_count': len(error_logs),
            'interaction_count': len(interaction_logs),
            'time_range': {
                'start': min(log['timestamp'] for log in filtered_logs).isoformat(),
                'end': max(log['timestamp'] for log in filtered_logs).isoformat()
            }
        }
    
    def get_user_interaction_stats(self) -> Dict[str, Any]:
        """
        获取用户交互统计信息
        
        Returns:
            Dict[str, Any]: 用户交互统计
        """
        interaction_logs = [log for log in self.logs if '用户交互' in log['message']]
        
        if not interaction_logs:
            return {}
        
        # 解析交互日志
        interactions = []
        for log in interaction_logs:
            # 提取交互信息
            try:
                # 简化处理，实际应该用json解析
                interaction_info = log['message'].split(':', 1)[1].strip()
                interactions.append({
                    'timestamp': log['timestamp'],
                    'info': interaction_info
                })
            except:
                continue
        
        # 按小时统计交互次数
        hourly_interactions = defaultdict(int)
        for interaction in interactions:
            hour_key = interaction['timestamp'].strftime('%Y-%m-%d %H')
            hourly_interactions[hour_key] += 1
        
        # 最活跃时段
        busiest_hour = max(hourly_interactions.items(), key=lambda x: x[1]) if hourly_interactions else (None, 0)
        
        return {
            'total_interactions': len(interactions),
            'hourly_interactions': dict(hourly_interactions),
            'busiest_hour': {
                'hour': busiest_hour[0],
                'count': busiest_hour[1]
            }
        }
    
    def get_error_summary(self) -> List[Dict[str, Any]]:
        """
        获取错误摘要
        
        Returns:
            List[Dict[str, Any]]: 错误摘要列表
        """
        error_logs = [log for log in self.logs if log['level'] in ['ERROR', 'CRITICAL']]
        
        # 统计相同错误信息
        error_messages = Counter(log['message'] for log in error_logs)
        
        # 构造错误摘要
        error_summary = []
        for message, count in error_messages.most_common(10):
            # 找到该错误信息的最新时间
            latest_time = max(
                log['timestamp'] for log in error_logs 
                if log['message'] == message
            )
            
            error_summary.append({
                'message': message,
                'count': count,
                'latest_occurrence': latest_time.isoformat()
            })
        
        return error_summary
    
    def generate_daily_report(self, date: datetime = None) -> Dict[str, Any]:
        """
        生成日报
        
        Args:
            date (datetime, optional): 报告日期，默认为今天
            
        Returns:
            Dict[str, Any]: 日报内容
        """
        if date is None:
            date = datetime.now()
        
        # 设置时间范围为指定日期的0点到24点
        start_time = datetime(date.year, date.month, date.day)
        end_time = start_time + timedelta(days=1)
        
        # 分析该时间段的日志
        analysis = self.analyze_time_range(start_time, end_time)
        
        # 获取用户交互统计
        interaction_stats = self.get_user_interaction_stats()
        
        # 获取错误摘要
        error_summary = self.get_error_summary()
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'analysis': analysis,
            'interaction_stats': interaction_stats,
            'top_errors': error_summary[:5],
            'generated_at': datetime.now().isoformat()
        }