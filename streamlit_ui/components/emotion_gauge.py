#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
情绪仪表盘组件
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any, List

def display_emotion_gauge(emotion: str, confidence: float = 1.0):
    """
    显示情绪仪表盘
    
    Args:
        emotion (str): 情绪类型
        confidence (float): 置信度 (0-1)
    """
    # 情绪映射
    emotion_mapping = {
        'happy': {'name': '开心', 'color': 'green', 'value': 80},
        'sad': {'name': '难过', 'color': 'blue', 'value': 20},
        'angry': {'name': '生气', 'color': 'red', 'value': 40},
        'excited': {'name': '兴奋', 'color': 'orange', 'value': 90},
        'calm': {'name': '平静', 'color': 'lightblue', 'value': 60},
        'confused': {'name': '困惑', 'color': 'purple', 'value': 30},
        'neutral': {'name': '中性', 'color': 'gray', 'value': 50}
    }
    
    emotion_info = emotion_mapping.get(emotion.lower(), 
                                     {'name': emotion, 'color': 'gray', 'value': 50})
    
    # 创建仪表盘
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=emotion_info['value'],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"情绪状态: {emotion_info['name']}", 'font': {'size': 20}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': emotion_info['color']},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 100], 'color': 'white'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': emotion_info['value']
            }
        }
    ))
    
    fig.update_layout(
        font={'color': "darkblue", 'family': "Arial"},
        margin=dict(l=20, r=20, t=40, b=20),
        height=200
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 显示置信度
    st.progress(confidence)
    st.caption(f"情绪识别置信度: {confidence:.1%}")

def display_emotion_history(emotion_history: List[Dict[str, Any]]):
    """
    显示情绪历史
    
    Args:
        emotion_history (List[Dict[str, Any]]): 情绪历史记录
    """
    if not emotion_history:
        st.info("暂无情绪历史记录")
        return
    
    st.subheader("情绪变化趋势")
    
    # 准备数据
    timestamps = [record['timestamp'] for record in emotion_history]
    emotions = [record['emotion'] for record in emotion_history]
    
    # 简化的可视化（实际应用中可以使用更复杂的图表）
    emotion_values = {
        'happy': 5,
        'sad': 1,
        'angry': 2,
        'excited': 4,
        'calm': 3,
        'confused': 1.5,
        'neutral': 2.5
    }
    
    values = [emotion_values.get(e, 0) for e in emotions]
    
    # 创建简单的情绪趋势图
    chart_data = {
        '时间': timestamps,
        '情绪值': values
    }
    
    st.line_chart(chart_data, x='时间', y='情绪值')

def display_emotion_insights(emotion_data: Dict[str, Any]):
    """
    显示情绪洞察
    
    Args:
        emotion_data (Dict[str, Any]): 情绪数据
    """
    st.subheader("情绪洞察")
    
    dominant_emotion = emotion_data.get('dominant_emotion', 'neutral')
    emotion_frequency = emotion_data.get('emotion_frequency', {})
    
    st.markdown(f"**主要情绪**: {dominant_emotion}")
    
    # 显示情绪频率
    if emotion_frequency:
        st.markdown("**情绪频率分布**:")
        for emotion, freq in emotion_frequency.items():
            st.progress(freq)
            st.markdown(f"{emotion}: {freq:.1%}")

def display_emotion_recommendation(emotion: str):
    """
    根据情绪显示推荐
    
    Args:
        emotion (str): 当前情绪
    """
    recommendations = {
        'happy': "😊 你看起来很开心！可以和我分享你的快乐，或者尝试一些有挑战性的学习内容。",
        'sad': "😢 感到难过是正常的。可以和我说说是什么让你难过，或者听个故事放松一下。",
        'angry': "😠 生气时可以先深呼吸，告诉我发生了什么，我们一起想办法解决。",
        'excited': "🤩 你很兴奋呢！可以把你兴奋的事情告诉我，或者尝试一些有趣的活动。",
        'calm': "😌 平静的状态很适合学习。可以尝试阅读或解决一些数学问题。",
        'confused': "😕 感到困惑时，可以把问题告诉我，我会尽力帮你解答。",
        'neutral': "😐 你的情绪很平稳。可以尝试一些新的学习内容或活动。"
    }
    
    recommendation = recommendations.get(emotion.lower(), "保持你的好奇心，继续探索吧！")
    st.info(recommendation)

def create_emotion_tracker():
    """
    创建情绪追踪器
    
    Returns:
        str: 选择的情绪
    """
    st.subheader("😊 情绪打卡")
    
    emotions = {
        "😊 开心": "happy",
        "😢 难过": "sad",
        "😠 生气": "angry",
        "🤩 兴奋": "excited",
        "😌 平静": "calm",
        "😕 困惑": "confused",
        "😐 平常": "neutral"
    }
    
    selected_emoji = st.selectbox("今天你的心情是？", list(emotions.keys()))
    selected_emotion = emotions.get(selected_emoji, "neutral")
    
    if st.button("记录情绪"):
        st.success(f"已记录你的情绪: {selected_emoji}")
        return selected_emotion
    
    return None