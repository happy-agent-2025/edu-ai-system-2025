#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask主应用
"""

from flask import Flask
from flask_cors import CORS

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    CORS(app)  # 允许跨域请求
    
    # 加载配置
    app.config['SECRET_KEY'] = 'edu-ai-system-secret-key'
    
    # 注册蓝图
    from backend.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/')
    def health_check():
        return {'status': 'ok', 'message': 'Education AI System is running'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)