#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统监控脚本
"""

import psutil
import time
import sys
import os
from datetime import datetime


def get_system_metrics():
    """获取系统指标"""
    # CPU使用率
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # 内存使用率
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    
    # 磁盘使用率
    disk = psutil.disk_usage('/')
    disk_percent = (disk.used / disk.total) * 100
    
    # 网络IO
    net_io = psutil.net_io_counters()
    
    return {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': cpu_percent,
        'memory_percent': memory_percent,
        'memory_available': memory.available,
        'memory_total': memory.total,
        'disk_percent': disk_percent,
        'disk_used': disk.used,
        'disk_total': disk.total,
        'network_bytes_sent': net_io.bytes_sent,
        'network_bytes_recv': net_io.bytes_recv
    }


def monitor_system(duration=60, interval=5):
    """监控系统"""
    print(f"开始监控系统 {duration} 秒，间隔 {interval} 秒")
    print("按 Ctrl+C 停止监控")
    print("-" * 80)
    
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            metrics = get_system_metrics()
            
            # 清屏并显示指标
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print(f"系统监控 - {metrics['timestamp']}")
            print("=" * 50)
            print(f"CPU 使用率:     {metrics['cpu_percent']:>6.2f}%")
            print(f"内存使用率:     {metrics['memory_percent']:>6.2f}%")
            print(f"可用内存:       {metrics['memory_available'] / (1024**3):>6.2f} GB")
            print(f"总内存:         {metrics['memory_total'] / (1024**3):>6.2f} GB")
            print(f"磁盘使用率:     {metrics['disk_percent']:>6.2f}%")
            print(f"已用磁盘空间:   {metrics['disk_used'] / (1024**3):>6.2f} GB")
            print(f"总磁盘空间:     {metrics['disk_total'] / (1024**3):>6.2f} GB")
            print(f"网络发送:       {metrics['network_bytes_sent'] / (1024**2):>6.2f} MB")
            print(f"网络接收:       {metrics['network_bytes_recv'] / (1024**2):>6.2f} MB")
            print("=" * 50)
            print("按 Ctrl+C 停止监控")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n监控已停止")


def log_system_metrics(log_file="system_metrics.log", duration=300, interval=10):
    """记录系统指标到日志文件"""
    print(f"开始记录系统指标到 {log_file}")
    print(f"记录时长: {duration} 秒，间隔: {interval} 秒")
    print("按 Ctrl+C 停止记录")
    
    start_time = time.time()
    
    try:
        with open(log_file, "w") as f:
            f.write("timestamp,cpu_percent,memory_percent,disk_percent\n")
            
            while time.time() - start_time < duration:
                metrics = get_system_metrics()
                
                # 写入日志
                log_line = f"{metrics['timestamp']},{metrics['cpu_percent']},{metrics['memory_percent']},{metrics['disk_percent']}\n"
                f.write(log_line)
                f.flush()  # 立即写入磁盘
                
                print(f"记录: {metrics['timestamp']} - CPU: {metrics['cpu_percent']:.2f}%, 内存: {metrics['memory_percent']:.2f}%")
                
                time.sleep(interval)
                
    except KeyboardInterrupt:
        print("\n记录已停止")
    
    print(f"指标已记录到 {log_file}")


def check_system_health():
    """检查系统健康状态"""
    print("检查系统健康状态...")
    
    metrics = get_system_metrics()
    
    # 定义阈值
    CPU_THRESHOLD = 80.0
    MEMORY_THRESHOLD = 85.0
    DISK_THRESHOLD = 90.0
    
    issues = []
    
    if metrics['cpu_percent'] > CPU_THRESHOLD:
        issues.append(f"CPU使用率过高: {metrics['cpu_percent']:.2f}%")
    
    if metrics['memory_percent'] > MEMORY_THRESHOLD:
        issues.append(f"内存使用率过高: {metrics['memory_percent']:.2f}%")
    
    if metrics['disk_percent'] > DISK_THRESHOLD:
        issues.append(f"磁盘使用率过高: {metrics['disk_percent']:.2f}%")
    
    if issues:
        print("发现以下问题:")
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("✅ 系统状态正常")
    
    # 显示详细信息
    print("\n详细系统信息:")
    print(f"  CPU 使用率:     {metrics['cpu_percent']:>6.2f}%")
    print(f"  内存使用率:     {metrics['memory_percent']:>6.2f}%")
    print(f"  磁盘使用率:     {metrics['disk_percent']:>6.2f}%")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='系统监控工具')
    parser.add_argument('--monitor', action='store_true', help='实时监控系统')
    parser.add_argument('--log', action='store_true', help='记录系统指标到日志文件')
    parser.add_argument('--health', action='store_true', help='检查系统健康状态')
    parser.add_argument('--duration', type=int, default=60, help='监控时长(秒)')
    parser.add_argument('--interval', type=int, default=5, help='监控间隔(秒)')
    
    args = parser.parse_args()
    
    if args.monitor:
        monitor_system(args.duration, args.interval)
    elif args.log:
        log_system_metrics(duration=args.duration, interval=args.interval)
    elif args.health:
        check_system_health()
    else:
        # 默认检查系统健康状态
        check_system_health()


if __name__ == '__main__':
    main()