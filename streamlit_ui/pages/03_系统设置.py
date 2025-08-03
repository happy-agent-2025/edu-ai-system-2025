#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统设置页面
"""

import streamlit as st
import requests
import os

# 页面配置
st.set_page_config(
    page_title="系统设置",
    page_icon="⚙️",
    layout="wide"
)

# 应用配置
API_BASE_URL = "http://localhost:5000/api"

def main():
    st.title("⚙️ 系统设置")
    
    # 初始化会话状态
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 'default_child'
    
    # 侧边栏
    with st.sidebar:
        st.header("设置导航")
        section = st.radio(
            "选择设置项",
            ["基本设置", "API配置", "系统信息"]
        )
    
    # 根据选择的区域显示内容
    if section == "基本设置":
        show_basic_settings()
    elif section == "API配置":
        show_api_settings()
    elif section == "系统信息":
        show_system_info()

def show_basic_settings():
    """显示基本设置"""
    st.header("基本设置")
    
    # 用户设置
    st.subheader("用户设置")
    new_user_id = st.text_input("默认用户ID", st.session_state.user_id)
    if st.button("更新用户ID"):
        st.session_state.user_id = new_user_id
        st.success("用户ID已更新")
    
    # 界面设置
    st.subheader("界面设置")
    theme = st.selectbox("选择主题", ["默认", "明亮", "暗黑"])
    st.info("主题设置将在下次启动时生效")
    
    # 语言设置
    st.subheader("语言设置")
    language = st.selectbox("选择语言", ["中文", "English"])
    st.info("语言设置将在下次启动时生效")

def show_api_settings():
    """显示API配置"""
    st.header("API配置")
    
    # API基础URL设置
    st.subheader("API连接设置")
    api_url = st.text_input("API基础URL", API_BASE_URL)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("测试API连接"):
            try:
                response = requests.get(f"{api_url}/health", timeout=10)
                if response.status_code == 200:
                    st.success("✅ API连接成功")
                else:
                    st.warning("⚠️ API连接失败")
            except Exception as e:
                st.error(f"❌ 连接失败: {e}")
    
    with col2:
        if st.button("保存API配置"):
            # 在实际应用中，这里应该保存配置到文件或数据库
            st.success("API配置已保存")
    
    # API密钥设置
    st.subheader("认证设置")
    api_key = st.text_input("API密钥", type="password")
    if st.button("保存密钥"):
        # 在实际应用中，这里应该安全地保存密钥
        st.success("API密钥已保存")

def show_system_info():
    """显示系统信息"""
    st.header("系统信息")
    
    st.info("""
    **儿童教育AI系统**
    
    这是一个专为儿童设计的AI教育助手系统，具有以下特点：
    - 多Agent架构，支持教育和情感陪伴功能
    - 完善的安全审查机制
    - 智能对话历史管理
    - 家长监控功能
    - 语音交互支持
    """)
    
    st.subheader("系统架构")
    st.markdown("""
    1. **元Agent**: 负责意图识别和路由
    2. **教育Agent**: 处理教育相关问题
    3. **情感Agent**: 提供情感陪伴支持
    4. **安全Agent**: 内容安全审查
    5. **记忆Agent**: 对话历史管理
    """)
    
    st.subheader("技术栈")
    st.markdown("""
    - **后端**: Python, Flask, LangChain
    - **前端**: Streamlit
    - **数据库**: SQLite
    - **AI模型**: 集成多种大语言模型
    - **部署**: Docker支持
    """)
    
    st.subheader("系统状态")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            st.success(f"✅ 系统运行正常: {data.get('message', '')}")
        else:
            st.warning("⚠️ 系统状态异常")
    except:
        st.error("❌ 无法连接到后端服务")
    
    st.subheader("版本信息")
    st.markdown("""
    - 版本: 1.0.0
    - 发布日期: 2023年
    - 开发者: 儿童教育AI团队
    """)

if __name__ == "__main__":
    main()