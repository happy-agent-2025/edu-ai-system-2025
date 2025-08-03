#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音频输入输出组件
"""

import streamlit as st
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    gTTS = None

import io
import base64
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    AudioSegment = None

import numpy as np

def audio_input_component():
    """
    音频输入组件
    
    Returns:
        str: 识别的文本，如果失败则返回None
    """
    st.subheader("🎤 语音输入")
    
    if not SPEECH_RECOGNITION_AVAILABLE:
        st.warning("语音识别库未安装，请安装 speechrecognition 库以启用此功能")
        return None
    
    # 文件上传方式
    st.markdown("上传音频文件:")
    audio_file = st.file_uploader("上传音频文件", type=['wav', 'mp3', 'm4a'])
    
    if audio_file is not None:
        try:
            # 读取音频文件
            audio_bytes = audio_file.read()
            
            # 保存音频文件以便播放
            st.audio(audio_bytes, format='audio/wav')
            
            # 尝试语音识别
            recognized_text = recognize_audio(audio_bytes)
            if recognized_text:
                st.success(f"识别结果: {recognized_text}")
                return recognized_text
            else:
                st.warning("无法识别音频内容")
        except Exception as e:
            st.error(f"处理音频文件时出错: {e}")
    
    return None

def recognize_audio(audio_bytes):
    """
    识别音频内容
    
    Args:
        audio_bytes (bytes): 音频数据
        
    Returns:
        str: 识别的文本，如果失败则返回None
    """
    if not SPEECH_RECOGNITION_AVAILABLE:
        return None
        
    try:
        # 创建SpeechRecognition识别器
        recognizer = sr.Recognizer()
        
        # 将字节数据转换为AudioFile
        audio_data = sr.AudioData(audio_bytes, sample_rate=22050, sample_width=2)
        
        # 尝试识别
        text = recognizer.recognize_google(audio_data, language="zh-CN")
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        st.error(f"语音识别服务错误: {e}")
        return None
    except Exception as e:
        st.error(f"音频识别错误: {e}")
        return None

def text_to_speech_component(text, lang='zh'):
    """
    文本转语音组件
    
    Args:
        text (str): 要转换的文本
        lang (str): 语言代码
    """
    if not text:
        return
    
    if not GTTS_AVAILABLE:
        st.warning("文本转语音库未安装，请安装 gtts 库以启用此功能")
        return
    
    st.subheader("🔊 语音输出")
    
    try:
        # 使用gTTS生成语音
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # 将语音保存到字节流
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        # 显示音频播放器
        st.audio(audio_buffer, format='audio/mp3')
        
        # 提供下载链接
        st.download_button(
            label="下载语音",
            data=audio_buffer,
            file_name="response.mp3",
            mime="audio/mp3"
        )
        
    except Exception as e:
        st.error(f"文本转语音失败: {e}")

def audio_visualization_component(audio_bytes):
    """
    音频可视化组件
    
    Args:
        audio_bytes (bytes): 音频数据
    """
    if not PYDUB_AVAILABLE:
        st.warning("音频处理库未安装，请安装 pydub 库以启用此功能")
        return
        
    st.subheader("📊 音频可视化")
    
    try:
        # 使用pydub加载音频
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        
        # 显示音频基本信息
        st.info(f"""
        音频信息:
        - 时长: {len(audio) / 1000:.2f} 秒
        - 帧率: {audio.frame_rate} Hz
        - 声道数: {audio.channels}
        """)
        
        # 简单的波形可视化（使用st.line_chart）
        samples = np.array(audio.get_array_of_samples())
        st.line_chart(samples[::max(1, len(samples)//1000)])  # 采样以提高性能
        
    except Exception as e:
        st.warning(f"无法生成音频可视化: {e}")

def audio_player_component(audio_bytes, format='audio/wav'):
    """
    音频播放器组件
    
    Args:
        audio_bytes (bytes): 音频数据
        format (str): 音频格式
    """
    st.audio(audio_bytes, format=format)