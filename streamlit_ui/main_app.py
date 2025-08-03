#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Streamlit前端主应用
"""

import streamlit as st
import requests
import json
from datetime import datetime
import os

# 应用配置
API_BASE_URL = "http://localhost:5000/api"
WEBSOCKET_URL = "http://localhost:5000"

def main():
    """主应用函数"""
    st.set_page_config(
        page_title="儿童教育AI系统",
        page_icon="🎓",
        layout="wide"
    )
    
    # 侧边栏
    with st.sidebar:
        st.title("🎓 儿童教育AI系统")
        st.markdown("---")
        
        # 用户信息
        if 'user_id' not in st.session_state:
            st.session_state.user_id = 'default_child'
        
        st.session_state.user_id = st.text_input("用户ID", st.session_state.user_id)
        
        # 页面导航
        page = st.radio(
            "选择页面",
            ["儿童交互", "家长控制台", "系统设置"]
        )
    
    # 页面路由
    if page == "儿童交互":
        child_interface()
    elif page == "家长控制台":
        parent_dashboard()
    elif page == "系统设置":
        system_settings()


def child_interface():
    """儿童交互界面"""
    st.title("👋 你好，小朋友！")
    st.markdown("在这里你可以和AI助手聊天学习")
    
    # 显示聊天历史
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # 显示对话历史
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])
    
    # 用户输入
    user_input = st.chat_input("想聊什么？")
    
    if user_input:
        # 显示用户消息
        st.chat_message("user").write(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # 发送请求到后端API
        try:
            response = requests.post(
                f"{API_BASE_URL}/chat",
                json={
                    "text": user_input,
                    "user_id": st.session_state.user_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("response", "抱歉，我没有理解你的问题。")
                
                # 显示AI响应
                st.chat_message("assistant").write(ai_response)
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            else:
                st.error(f"API请求失败: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"网络请求错误: {e}")
        except Exception as e:
            st.error(f"发生错误: {e}")


def parent_dashboard():
    """家长控制台界面"""
    st.title("👨‍👩‍👧‍👦 家长控制台")
    st.markdown("在这里可以监控孩子的学习情况和系统状态")
    
    # 系统状态
    st.subheader("系统状态")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            st.success("系统运行正常")
        else:
            st.warning("系统状态异常")
    except:
        st.error("无法连接到后端服务")
    
    # 统计信息
    st.subheader("统计信息")
    try:
        stats_response = requests.get(f"{API_BASE_URL}/stats", timeout=10)
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            stats = stats_data.get("stats", {})
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总用户数", stats.get("users", {}).get("total_users", 0))
            with col2:
                st.metric("总对话数", stats.get("conversations", {}).get("total_conversations", 0))
            with col3:
                st.metric("安全违规数", stats.get("safety", {}).get("total_violations", 0))
        else:
            st.warning("无法获取统计信息")
    except Exception as e:
        st.error(f"获取统计信息失败: {e}")
    
    # 用户对话历史
    st.subheader("用户对话历史")
    user_id = st.text_input("查询用户ID", st.session_state.user_id)
    
    if st.button("查询历史"):
        try:
            history_response = requests.get(
                f"{API_BASE_URL}/user/{user_id}/history",
                params={"limit": 20},
                timeout=10
            )
            
            if history_response.status_code == 200:
                history_data = history_response.json()
                history = history_data.get("history", [])
                
                if history:
                    for item in history:
                        with st.expander(f"{item['timestamp']} - {item['agent_name']}"):
                            st.markdown(f"**用户**: {item['user_input']}")
                            st.markdown(f"**AI助手**: {item['agent_response']}")
                            st.markdown(f"**安全检查**: {item['safety_check']}")
                else:
                    st.info("暂无对话历史")
            else:
                st.error("获取对话历史失败")
        except Exception as e:
            st.error(f"查询对话历史失败: {e}")
    
    # 安全违规记录
    st.subheader("安全违规记录")
    try:
        violations_response = requests.get(
            f"{API_BASE_URL}/safety/violations",
            params={"limit": 10},
            timeout=10
        )
        
        if violations_response.status_code == 200:
            violations_data = violations_response.json()
            violations = violations_data.get("violations", [])
            
            if violations:
                for violation in violations:
                    with st.expander(f"{violation['timestamp']} - {violation['agent_name']}"):
                        st.markdown(f"**用户ID**: {violation['user_id']}")
                        st.markdown(f"**用户输入**: {violation['user_input']}")
                        st.markdown(f"**AI响应**: {violation['agent_response']}")
                        st.markdown(f"**违规原因**: {violation['violation_reason']}")
            else:
                st.info("暂无安全违规记录")
        else:
            st.error("获取安全违规记录失败")
    except Exception as e:
        st.error(f"获取安全违规记录失败: {e}")


def system_settings():
    """系统设置界面"""
    st.title("⚙️ 系统设置")
    
    st.subheader("API配置")
    api_url = st.text_input("API基础URL", API_BASE_URL)
    if st.button("测试API连接"):
        try:
            response = requests.get(f"{api_url}/health", timeout=10)
            if response.status_code == 200:
                st.success("API连接成功")
            else:
                st.warning("API连接失败")
        except Exception as e:
            st.error(f"连接失败: {e}")
    
    st.subheader("用户设置")
    new_user_id = st.text_input("设置新的默认用户ID", st.session_state.user_id)
    if st.button("更新用户ID"):
        st.session_state.user_id = new_user_id
        st.success("用户ID已更新")
    
    st.subheader("系统信息")
    st.info("""
    **儿童教育AI系统**
    
    这是一个专为儿童设计的AI教育助手系统，具有以下特点：
    - 多Agent架构，支持教育和情感陪伴功能
    - 完善的安全审查机制
    - 智能对话历史管理
    - 家长监控功能
    - 语音交互支持
    
    系统组件：
    - 元Agent：负责意图识别和路由
    - 教育Agent：处理教育相关问题
    - 情感Agent：提供情感陪伴支持
    - 安全Agent：内容安全审查
    - 记忆Agent：对话历史管理
    """)


if __name__ == "__main__":
    main()