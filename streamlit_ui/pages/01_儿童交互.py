#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
儿童交互页面
"""

import streamlit as st
import requests
import asyncio

# 页面配置
st.set_page_config(
    page_title="儿童交互",
    page_icon="👋",
    layout="wide"
)

# 应用配置
API_BASE_URL = "http://localhost:5000/api"

def main():
    st.title("👋 你好，小朋友！")
    st.markdown("在这里你可以和AI助手聊天学习")
    
    # 初始化会话状态
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 'default_child'
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # 侧边栏
    with st.sidebar:
        st.header("用户设置")
        st.session_state.user_id = st.text_input("用户ID", st.session_state.user_id)
        st.markdown("---")
        st.header("使用说明")
        st.info("""
        🎯 你可以和AI助手聊任何话题
        
        📚 学习问题：数学、语文、英语等
        
        💬 情感交流：分享你的开心和烦恼
        
        🔒 所有对话都会经过安全检查
        """)
    
    # 显示聊天历史
    st.subheader("对话历史")
    
    # 创建一个容器来显示聊天记录
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])
    
    # 用户输入
    st.subheader("开始聊天")
    user_input = st.chat_input("想聊什么？")
    
    if user_input:
        # 显示用户消息
        st.chat_message("user").write(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # 发送请求到后端API
        with st.spinner("AI助手正在思考..."):
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
    
    # 清空聊天历史按钮
    if st.button("清空聊天历史"):
        st.session_state.chat_history = []
        st.experimental_rerun()

if __name__ == "__main__":
    main()