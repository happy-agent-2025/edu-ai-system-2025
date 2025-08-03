#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
认证模块
"""

import jwt
import hashlib
import secrets
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# 秘钥（实际应用中应该从环境变量或配置文件中读取）
SECRET_KEY = "edu-ai-system-secret-key"
ADMIN_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()  # 示例密码


class AuthManager:
    """
    认证管理类
    """
    
    @staticmethod
    def generate_token(user_id: str, user_type: str = "user", expires_in: int = 3600) -> str:
        """
        生成JWT令牌
        
        Args:
            user_id (str): 用户ID
            user_type (str): 用户类型 ('user' 或 'admin')
            expires_in (int): 过期时间（秒）
            
        Returns:
            str: JWT令牌
        """
        payload = {
            'user_id': user_id,
            'user_type': user_type,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        验证JWT令牌
        
        Args:
            token (str): JWT令牌
            
        Returns:
            Optional[Dict[str, Any]]: 令牌载荷，如果验证失败则返回None
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        哈希密码
        
        Args:
            password (str): 原始密码
            
        Returns:
            str: 哈希后的密码
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        验证密码
        
        Args:
            password (str): 原始密码
            hashed_password (str): 哈希后的密码
            
        Returns:
            bool: 密码是否正确
        """
        return AuthManager.hash_password(password) == hashed_password


def require_auth(user_types: list = None):
    """
    认证装饰器
    
    Args:
        user_types (list): 允许的用户类型列表，None表示允许所有认证用户
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({
                    'status': 'error',
                    'message': '缺少访问令牌'
                }), 401
            
            # 移除Bearer前缀
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = AuthManager.verify_token(token)
            if not payload:
                return jsonify({
                    'status': 'error',
                    'message': '无效或过期的访问令牌'
                }), 401
            
            # 检查用户类型
            if user_types and payload.get('user_type') not in user_types:
                return jsonify({
                    'status': 'error',
                    'message': '权限不足'
                }), 403
            
            # 将用户信息添加到请求上下文
            request.user_payload = payload
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def login_user(user_id: str) -> Dict[str, Any]:
    """
    用户登录
    
    Args:
        user_id (str): 用户ID
        
    Returns:
        Dict[str, Any]: 登录结果
    """
    token = AuthManager.generate_token(user_id, 'user')
    return {
        'status': 'success',
        'token': token,
        'user_id': user_id,
        'user_type': 'user'
    }


def login_admin(password: str) -> Dict[str, Any]:
    """
    管理员登录
    
    Args:
        password (str): 管理员密码
        
    Returns:
        Dict[str, Any]: 登录结果
    """
    if AuthManager.verify_password(password, ADMIN_PASSWORD_HASH):
        token = AuthManager.generate_token('admin', 'admin')
        return {
            'status': 'success',
            'token': token,
            'user_id': 'admin',
            'user_type': 'admin'
        }
    else:
        return {
            'status': 'error',
            'message': '密码错误'
        }


def generate_secure_token() -> str:
    """
    生成安全的随机令牌
    
    Returns:
        str: 安全令牌
    """
    return secrets.token_urlsafe(32)