#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库初始化脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.database.manager import DatabaseManager


def setup_database():
    """设置数据库"""
    print("开始初始化数据库...")
    
    try:
        # 创建数据库管理器实例
        db_manager = DatabaseManager()
        
        # 初始化数据库表
        db_manager._initialize_database()
        
        print("数据库初始化完成!")
        print(f"数据库文件位置: {os.path.abspath(db_manager.db_path)}")
        
        # 显示数据库统计信息
        stats = db_manager.get_database_stats()
        print("\n数据库统计信息:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        sys.exit(1)


def reset_database():
    """重置数据库"""
    print("警告: 此操作将删除所有数据!")
    confirm = input("确认要重置数据库吗? (输入 'yes' 确认): ")
    
    if confirm.lower() != 'yes':
        print("操作已取消")
        return
    
    try:
        # 创建数据库管理器实例
        db_manager = DatabaseManager()
        
        # 删除数据库文件
        if os.path.exists(db_manager.db_path):
            os.remove(db_manager.db_path)
            print("旧数据库文件已删除")
        
        # 重新初始化数据库
        db_manager._initialize_database()
        print("数据库已重置!")
        
    except Exception as e:
        print(f"数据库重置失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库管理工具')
    parser.add_argument('--reset', action='store_true', help='重置数据库')
    parser.add_argument('--setup', action='store_true', help='初始化数据库')
    
    args = parser.parse_args()
    
    if args.reset:
        reset_database()
    elif args.setup:
        setup_database()
    else:
        # 默认初始化数据库
        setup_database()


if __name__ == '__main__':
    main()