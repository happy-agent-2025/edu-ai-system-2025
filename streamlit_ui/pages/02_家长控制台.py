#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
家长控制台页面
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="家长控制台",
    page_icon="👨‍👩‍👧‍👦",
    layout="wide"
)

# 应用配置
API_BASE_URL = "http://localhost:5000/api"

def main():
    st.title("👨‍👩‍👧‍👦 家长控制台")
    st.markdown("在这里可以监控孩子的学习情况和系统状态")
    
    # 初始化会话状态
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 'default_child'
    
    # 侧边栏
    with st.sidebar:
        st.header("控制面板")
        st.session_state.user_id = st.text_input("监控的用户ID", st.session_state.user_id)
        st.markdown("---")
        st.header("导航")
        section = st.radio(
            "选择查看内容",
            ["系统状态", "学习统计", "对话历史", "安全监控"]
        )
    
    # 根据选择的区域显示内容
    if section == "系统状态":
        show_system_status()
    elif section == "学习统计":
        show_learning_statistics()
    elif section == "对话历史":
        show_conversation_history()
    elif section == "安全监控":
        show_safety_monitoring()

def show_system_status():
    """显示系统状态"""
    st.header("系统状态")
    
    col1, col2, col3 = st.columns(3)
    
    # 检查API连接
    with col1:
        st.subheader("API状态")
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                st.success("✅ API连接正常")
            else:
                st.error("❌ API连接异常")
        except:
            st.error("❌ 无法连接到API")
    
    # 获取系统统计
    with col2:
        st.subheader("用户统计")
        try:
            stats_response = requests.get(f"{API_BASE_URL}/stats", timeout=10)
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                stats = stats_data.get("stats", {})
                users_stats = stats.get("users", {})
                st.metric("总用户数", users_stats.get("total_users", 0))
                st.metric("活跃用户", users_stats.get("active_users", 0))
            else:
                st.warning("无法获取统计信息")
        except Exception as e:
            st.error(f"获取统计信息失败: {e}")
    
    with col3:
        st.subheader("对话统计")
        try:
            stats_response = requests.get(f"{API_BASE_URL}/stats", timeout=10)
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                stats = stats_data.get("stats", {})
                conv_stats = stats.get("conversations", {})
                st.metric("总对话数", conv_stats.get("total_conversations", 0))
            else:
                st.warning("无法获取统计信息")
        except Exception as e:
            st.error(f"获取统计信息失败: {e}")

def show_learning_statistics():
    """显示学习统计"""
    st.header("学习统计")
    
    try:
        stats_response = requests.get(f"{API_BASE_URL}/stats", timeout=10)
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            stats = stats_data.get("stats", {})
            
            # 显示用户年级分布
            st.subheader("用户年级分布")
            grade_dist = stats.get("users", {}).get("grade_distribution", {})
            if grade_dist:
                grade_df = pd.DataFrame(list(grade_dist.items()), columns=['年级', '用户数'])
                fig_grade = px.bar(grade_df, x='年级', y='用户数', title='用户年级分布')
                st.plotly_chart(fig_grade, use_container_width=True)
            else:
                st.info("暂无年级分布数据")
            
            # 显示Agent处理对话分布
            st.subheader("Agent对话分布")
            agent_dist = stats.get("conversations", {}).get("agent_distribution", {})
            if agent_dist:
                agent_df = pd.DataFrame(list(agent_dist.items()), columns=['Agent', '对话数'])
                fig_agent = px.pie(agent_df, values='对话数', names='Agent', title='Agent对话分布')
                st.plotly_chart(fig_agent, use_container_width=True)
            else:
                st.info("暂无Agent分布数据")
            
            # 显示每日对话趋势
            st.subheader("每日对话趋势")
            daily_conv = stats.get("conversations", {}).get("daily_conversations", {})
            if daily_conv:
                daily_df = pd.DataFrame(list(daily_conv.items()), columns=['日期', '对话数'])
                daily_df['日期'] = pd.to_datetime(daily_df['日期'])
                fig_daily = px.line(daily_df, x='日期', y='对话数', title='每日对话趋势')
                st.plotly_chart(fig_daily, use_container_width=True)
            else:
                st.info("暂无每日对话数据")
        else:
            st.warning("无法获取统计信息")
    except Exception as e:
        st.error(f"获取统计信息失败: {e}")

def show_conversation_history():
    """显示对话历史"""
    st.header("对话历史")
    
    # 查询参数
    col1, col2 = st.columns(2)
    with col1:
        limit = st.number_input("显示记录数", min_value=1, max_value=100, value=20)
    with col2:
        user_id = st.text_input("用户ID", st.session_state.user_id)
    
    if st.button("查询历史"):
        try:
            history_response = requests.get(
                f"{API_BASE_URL}/user/{user_id}/history",
                params={"limit": limit},
                timeout=10
            )
            
            if history_response.status_code == 200:
                history_data = history_response.json()
                history = history_data.get("history", [])
                
                if history:
                    # 转换为DataFrame显示
                    df = pd.DataFrame(history)
                    st.dataframe(df[['timestamp', 'agent_name', 'user_input', 'agent_response', 'safety_check']])
                    
                    # 显示详细信息
                    st.subheader("详细记录")
                    for i, item in enumerate(history):
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

def show_safety_monitoring():
    """显示安全监控"""
    st.header("安全监控")
    
    try:
        # 获取安全统计
        stats_response = requests.get(f"{API_BASE_URL}/stats", timeout=10)
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            stats = stats_data.get("stats", {})
            safety_stats = stats.get("safety", {})
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总违规数", safety_stats.get("total_violations", 0))
            with col2:
                st.metric("违规率", f"{safety_stats.get('total_violations', 0) / max(stats.get('conversations', {}).get('total_conversations', 1) * 100, 1):.2f}%")
            with col3:
                st.metric("监控中", "✅")
        
        # 显示违规类型分布
        st.subheader("违规类型分布")
        violation_dist = safety_stats.get("violation_distribution", {})
        if violation_dist:
            violation_df = pd.DataFrame(list(violation_dist.items()), columns=['违规类型', '次数'])
            fig_violation = px.bar(violation_df, x='违规类型', y='次数', title='违规类型分布')
            st.plotly_chart(fig_violation, use_container_width=True)
        else:
            st.info("暂无违规类型数据")
        
        # 显示最近的安全违规记录
        st.subheader("最近安全违规记录")
        violations_response = requests.get(
            f"{API_BASE_URL}/safety/violations",
            params={"limit": 20},
            timeout=10
        )
        
        if violations_response.status_code == 200:
            violations_data = violations_response.json()
            violations = violations_data.get("violations", [])
            
            if violations:
                # 转换为DataFrame显示
                df = pd.DataFrame(violations)
                st.dataframe(df[['timestamp', 'user_id', 'agent_name', 'violation_reason']])
                
                # 显示详细信息
                st.subheader("详细记录")
                for violation in violations:
                    with st.expander(f"{violation['timestamp']} - {violation['user_id']}"):
                        st.markdown(f"**用户ID**: {violation['user_id']}")
                        st.markdown(f"**Agent**: {violation['agent_name']}")
                        st.markdown(f"**用户输入**: {violation['user_input']}")
                        st.markdown(f"**AI响应**: {violation['agent_response']}")
                        st.markdown(f"**违规原因**: {violation['violation_reason']}")
            else:
                st.info("暂无安全违规记录")
        else:
            st.error("获取安全违规记录失败")
    except Exception as e:
        st.error(f"获取安全监控信息失败: {e}")

if __name__ == "__main__":
    main()