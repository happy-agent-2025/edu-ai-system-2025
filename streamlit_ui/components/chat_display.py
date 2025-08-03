#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
聊天展示组件
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Any

def display_chat_message(role: str, content: str, timestamp: str = None):
    """
    显示单条聊天消息
    
    Args:
        role (str): 消息角色 ('user' 或 'assistant')
        content (str): 消息内容
        timestamp (str): 时间戳
    """
    if role == "user":
        with st.chat_message("user"):
            st.write(content)
            if timestamp:
                st.caption(f"发送时间: {timestamp}")
    else:
        with st.chat_message("assistant"):
            st.write(content)
            if timestamp:
                st.caption(f"回复时间: {timestamp}")

def display_chat_history(chat_history: List[Dict[str, Any]]):
    """
    显示聊天历史
    
    Args:
        chat_history (List[Dict[str, Any]]): 聊天历史记录列表
    """
    for message in chat_history:
        display_chat_message(
            role=message["role"],
            content=message["content"],
            timestamp=message.get("timestamp")
        )

def display_conversation(conversation: Dict[str, Any]):
    """
    显示单次对话（用户输入+AI回复）
    
    Args:
        conversation (Dict[str, Any]): 对话记录
    """
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**用户输入:**")
        st.info(conversation.get("user_input", ""))
        st.caption(f"时间: {conversation.get('timestamp', '未知')}")
    
    with col2:
        st.markdown("**AI回复:**")
        st.success(conversation.get("agent_response", ""))
        st.caption(f"Agent: {conversation.get('agent_name', '未知')}")

def display_conversation_list(conversations: List[Dict[str, Any]]):
    """
    显示对话列表
    
    Args:
        conversations (List[Dict[str, Any]]): 对话记录列表
    """
    for i, conv in enumerate(conversations):
        with st.expander(f"对话 {len(conversations)-i} - {conv.get('agent_name', '未知')}"):
            display_conversation(conv)

def display_emotion_indicator(emotion: str):
    """
    显示情感指示器
    
    Args:
        emotion (str): 情感状态
    """
    emotion_icons = {
        "happy": "😊",
        "sad": "😢",
        "angry": "😠",
        "neutral": "😐",
        "excited": "🤩",
        "tired": "😴"
    }
    
    icon = emotion_icons.get(emotion, "😐")
    st.markdown(f"情感状态: {icon} {emotion}")

def display_agent_info(agent_name: str, agent_description: str):
    """
    显示Agent信息
    
    Args:
        agent_name (str): Agent名称
        agent_description (str): Agent描述
    """
    st.markdown(f"**当前Agent**: {agent_name}")
    st.markdown(f"*{agent_description}*")

def display_safety_status(status: str):
    """
    显示安全状态
    
    Args:
        status (str): 安全状态
    """
    if status == "approved":
        st.success("✅ 内容安全检查通过")
    elif status == "rejected":
        st.error("❌ 内容安全检查未通过")
    else:
        st.warning("⚠️ 安全状态未知")

def create_chat_interface(on_send_callback=None):
    """
    创建聊天界面
    
    Args:
        on_send_callback (function): 发送消息时的回调函数
        
    Returns:
        str: 用户输入的内容
    """
    # 聊天输入区域
    st.subheader("开始聊天")
    
    # 创建输入框
    user_input = st.chat_input("想聊什么？")
    
    # 如果用户输入了内容
    if user_input and on_send_callback:
        on_send_callback(user_input)
    
    return user_input

def display_typing_indicator():
    """显示正在输入指示器"""
    st.markdown("🤖 AI助手正在思考...")