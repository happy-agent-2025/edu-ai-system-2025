#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
安全警报组件
"""

import streamlit as st
from typing import Dict, Any, List

def display_safety_alert(violation_data: Dict[str, Any]):
    """
    显示安全警报
    
    Args:
        violation_data (Dict[str, Any]): 违规数据
    """
    st.warning("⚠️ 检测到安全问题")
    
    with st.expander("查看详情"):
        st.markdown(f"**用户ID**: {violation_data.get('user_id', '未知')}")
        st.markdown(f"**违规时间**: {violation_data.get('timestamp', '未知')}")
        st.markdown(f"**违规类型**: {violation_data.get('violation_reason', '未知')}")
        st.markdown(f"**处理Agent**: {violation_data.get('agent_name', '未知')}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**用户输入**:")
            st.error(violation_data.get('user_input', ''))
        with col2:
            st.markdown("**AI响应**:")
            st.error(violation_data.get('agent_response', ''))

def display_safety_violations_list(violations: List[Dict[str, Any]]):
    """
    显示安全违规列表
    
    Args:
        violations (List[Dict[str, Any]]): 违规记录列表
    """
    if not violations:
        st.info("暂无安全违规记录")
        return
    
    for i, violation in enumerate(violations):
        with st.container():
            st.markdown(f"**违规记录 {i+1}**")
            display_safety_alert(violation)
            st.markdown("---")

def display_safety_statistics(stats: Dict[str, Any]):
    """
    显示安全统计信息
    
    Args:
        stats (Dict[str, Any]): 安全统计信息
    """
    st.subheader("安全统计")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_violations = stats.get('total_violations', 0)
        st.metric("总违规数", total_violations)
    
    with col2:
        # 计算违规率
        total_conversations = stats.get('total_conversations', 1)
        violation_rate = (total_violations / max(total_conversations, 1)) * 100
        st.metric("违规率", f"{violation_rate:.2f}%")
    
    with col3:
        st.metric("监控状态", "✅ 正常")

def display_safety_dashboard(safety_data: Dict[str, Any]):
    """
    显示安全仪表板
    
    Args:
        safety_data (Dict[str, Any]): 安全数据
    """
    st.header("🛡️ 安全监控面板")
    
    # 显示安全统计
    stats = safety_data.get('stats', {})
    display_safety_statistics(stats)
    
    st.markdown("---")
    
    # 显示违规类型分布
    st.subheader("违规类型分布")
    violation_dist = stats.get('violation_distribution', {})
    if violation_dist:
        for violation_type, count in violation_dist.items():
            st.progress(count / max(sum(violation_dist.values()), 1))
            st.markdown(f"{violation_type}: {count}")
    else:
        st.info("暂无违规类型数据")
    
    st.markdown("---")
    
    # 显示最近违规记录
    st.subheader("最近违规记录")
    recent_violations = safety_data.get('recent_violations', [])
    display_safety_violations_list(recent_violations)

def display_content_safety_check(status: str, reason: str = None):
    """
    显示内容安全检查结果
    
    Args:
        status (str): 检查状态 ('approved', 'rejected')
        reason (str): 拒绝原因
    """
    if status == 'approved':
        st.success("✅ 内容安全检查通过")
    elif status == 'rejected':
        st.error("❌ 内容安全检查未通过")
        if reason:
            st.markdown(f"**拒绝原因**: {reason}")
    else:
        st.warning("⚠️ 内容安全检查状态未知")

def display_safety_policy():
    """显示安全策略信息"""
    st.info("""
    **儿童AI助手安全策略**
    
    我们采用多层安全机制保护儿童用户:
    
    1. **内容过滤**: 实时检测和过滤不当内容
    2. **隐私保护**: 不收集个人敏感信息
    3. **时间管理**: 控制使用时长，保护视力
    4. **家长控制**: 提供家长监控功能
    5. **情感支持**: 关注儿童心理健康
    
    所有对话均经过严格的安全审查，确保为儿童提供安全、健康的交流环境。
    """)

def display_emergency_alert():
    """显示紧急警报"""
    st.error("🚨 紧急情况")
    st.markdown("""
    如果您遇到以下情况，请立即联系家长或老师：
    - 感到不安全或受到威胁
    - 遇到让您感到不适的内容
    - 需要紧急帮助
    
    紧急联系电话：
    - 家长: _________
    - 老师: _________
    - 报警: 110
    """)