#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
教育AI系统启动脚本
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.app import create_app
from backend.api.websockets import init_socketio

def run_backend():
    """运行后端服务"""
    print("启动后端服务...")
    app = create_app()
    socketio = init_socketio(app)
    
    # 从环境变量获取配置，如果没有则使用默认值
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)

def run_frontend():
    """运行前端服务"""
    print("启动前端服务...")
    try:
        # 使用subprocess运行Streamlit
        subprocess.run([
            'streamlit', 'run', 
            'streamlit_ui/main_app.py',
            '--server.port=8501',
            '--server.address=0.0.0.0'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"启动前端服务失败: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("错误: 未找到streamlit命令，请确保已安装streamlit")
        print("可以通过以下命令安装: pip install streamlit")
        sys.exit(1)

def setup_database():
    """初始化数据库"""
    print("初始化数据库...")
    try:
        # 运行数据库初始化脚本
        subprocess.run([
            'python', 'scripts/setup_db.py', '--setup'
        ], check=True)
        print("数据库初始化完成")
    except subprocess.CalledProcessError as e:
        print(f"数据库初始化失败: {e}")
        sys.exit(1)

def download_models():
    """下载模型"""
    print("下载模型...")
    try:
        # 运行模型下载脚本
        subprocess.run([
            'python', 'scripts/model_downloader.py', '--all'
        ], check=True)
        print("模型下载完成")
    except subprocess.CalledProcessError as e:
        print(f"模型下载失败: {e}")
        sys.exit(1)

def run_tests():
    """运行测试"""
    print("运行测试...")
    try:
        # 运行单元测试
        subprocess.run([
            'python', '-m', 'pytest', 'tests/unit', '-v'
        ], check=True)
        print("单元测试完成")
    except subprocess.CalledProcessError as e:
        print(f"测试运行失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='儿童教育AI系统启动脚本')
    parser.add_argument('--backend', action='store_true', help='启动后端服务')
    parser.add_argument('--frontend', action='store_true', help='启动前端服务')
    parser.add_argument('--setup-db', action='store_true', help='初始化数据库')
    parser.add_argument('--download-models', action='store_true', help='下载模型')
    parser.add_argument('--test', action='store_true', help='运行测试')
    parser.add_argument('--all', action='store_true', help='启动所有服务')
    
    args = parser.parse_args()
    
    # 创建必要的目录
    dirs_to_create = ['logs', 'data', 'models/stt', 'models/tts', 'models/agents']
    for dir_name in dirs_to_create:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
    
    if args.all or (not any([args.backend, args.frontend, args.setup_db, args.download_models, args.test])):
        # 默认运行后端服务
        run_backend()
    else:
        if args.setup_db:
            setup_database()
        
        if args.download_models:
            download_models()
        
        if args.test:
            run_tests()
        
        if args.backend:
            run_backend()
        
        if args.frontend:
            run_frontend()

if __name__ == '__main__':
    main()