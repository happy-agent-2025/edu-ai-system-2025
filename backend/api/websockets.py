#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WebSocket处理
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
from typing import Dict, Any
import json

# 初始化SocketIO
socketio = None


def init_socketio(app):
    """初始化SocketIO"""
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*")
    register_events()
    return socketio


def register_events():
    """注册WebSocket事件处理函数"""
    @socketio.on('connect')
    def handle_connect():
        """处理客户端连接"""
        print(f'客户端连接: {request.sid}')
        emit('connected', {'data': 'WebSocket连接成功'})

    @socketio.on('disconnect')
    def handle_disconnect():
        """处理客户端断开连接"""
        print(f'客户端断开连接: {request.sid}')

    @socketio.on('join')
    def handle_join(data):
        """处理客户端加入房间"""
        user_id = data.get('user_id', 'default_user')
        join_room(user_id)
        emit('joined', {'room': user_id})

    @socketio.on('leave')
    def handle_leave(data):
        """处理客户端离开房间"""
        user_id = data.get('user_id', 'default_user')
        leave_room(user_id)
        emit('left', {'room': user_id})

    @socketio.on('chat_message')
    def handle_chat_message(data):
        """处理聊天消息"""
        try:
            # 解析消息数据
            if isinstance(data, str):
                data = json.loads(data)
            
            user_text = data.get('text', '')
            user_id = data.get('user_id', 'default_user')
            
            if not user_text:
                emit('error', {'message': '消息内容不能为空'})
                return
            
            # 这里应该调用实际的聊天处理逻辑
            # 模拟处理结果
            response = {
                'response': f'收到消息: {user_text}',
                'agent': 'WebSocketAgent',
                'user_id': user_id
            }
            
            # 发送响应给客户端
            emit('chat_response', response)
            
            # 广播到用户房间
            room_response = response.copy()
            room_response['timestamp'] = __import__('datetime').datetime.now().isoformat()
            emit('user_message', room_response, room=user_id)
            
        except Exception as e:
            emit('error', {'message': f'处理消息时出错: {str(e)}'})

    @socketio.on('audio_data')
    def handle_audio_data(data):
        """处理音频数据"""
        try:
            # 这里应该处理实际的音频数据
            # 模拟处理结果
            response = {
                'transcription': '模拟语音识别结果',
                'response': '这是对语音消息的回应',
                'agent': 'STTAgent'
            }
            
            emit('audio_response', response)
            
        except Exception as e:
            emit('error', {'message': f'处理音频时出错: {str(e)}'})

    @socketio.on('error')
    def handle_error(error):
        """处理错误"""
        print(f'WebSocket错误: {error}')


def send_realtime_update(room: str, event: str, data: Dict[str, Any]):
    """
    发送实时更新到指定房间
    
    Args:
        room (str): 房间名
        event (str): 事件名
        data (Dict[str, Any]): 数据
    """
    if socketio:
        socketio.emit(event, data, room=room)