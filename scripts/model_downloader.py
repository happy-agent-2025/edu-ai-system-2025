#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模型下载脚本
支持Fish Speech v1.2、Whisper和SpeakEncoder模型下载
"""

import os
import sys
import urllib.request
from tqdm import tqdm
import hashlib


def download_file(url, filename, description=""):
    """下载文件并显示进度条"""
    class DownloadProgressBar(tqdm):
        def update_to(self, b=1, bsize=1, tsize=None):
            if tsize is not None:
                self.total = tsize
            self.update(b * bsize - self.n)
    
    with DownloadProgressBar(unit='B', unit_scale=True,
                           miniters=1, desc=description) as t:
        urllib.request.urlretrieve(url, filename, 
                                 reporthook=t.update_to)


def verify_file_checksum(filepath, expected_checksum):
    """验证文件校验和"""
    if not os.path.exists(filepath):
        return False
    
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    
    return hash_md5.hexdigest() == expected_checksum


def download_stt_models():
    """下载STT模型"""
    print("下载STT模型...")
    stt_dir = os.path.join("models", "stt")
    os.makedirs(stt_dir, exist_ok=True)
    
    # 下载Fish Speech v1.2模型
    fish_speech_url = "https://example.com/fish-speech-v1.2.pth"  # 示例URL
    fish_speech_file = os.path.join(stt_dir, "fish_speech_v1.2.pth")
    fish_speech_checksum = "example_checksum_fish_speech"  # 示例校验和
    
    if not os.path.exists(fish_speech_file) or not verify_file_checksum(fish_speech_file, fish_speech_checksum):
        print("下载Fish Speech v1.2模型...")
        download_file(fish_speech_url, fish_speech_file, "Fish Speech v1.2")
        if verify_file_checksum(fish_speech_file, fish_speech_checksum):
            print("Fish Speech v1.2模型下载并验证成功")
        else:
            print("警告: Fish Speech v1.2模型校验失败")
    else:
        print("Fish Speech v1.2模型已存在且校验通过")
    
    print(f"STT模型文件位置: {stt_dir}")


def download_tts_models():
    """下载TTS模型"""
    print("下载TTS模型...")
    tts_dir = os.path.join("models", "tts")
    os.makedirs(tts_dir, exist_ok=True)
    
    # 下载Whisper模型
    whisper_url = "https://example.com/whisper-tts.pth"  # 示例URL
    whisper_file = os.path.join(tts_dir, "whisper.pth")
    whisper_checksum = "example_checksum_whisper"  # 示例校验和
    
    if not os.path.exists(whisper_file) or not verify_file_checksum(whisper_file, whisper_checksum):
        print("下载Whisper TTS模型...")
        download_file(whisper_url, whisper_file, "Whisper TTS")
        if verify_file_checksum(whisper_file, whisper_checksum):
            print("Whisper TTS模型下载并验证成功")
        else:
            print("警告: Whisper TTS模型校验失败")
    else:
        print("Whisper TTS模型已存在且校验通过")
    
    print(f"TTS模型文件位置: {tts_dir}")


def download_audio_models():
    """下载音频处理模型"""
    print("下载音频处理模型...")
    audio_dir = os.path.join("models", "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    # 下载SpeakEncoder模型
    speakencoder_url = "https://example.com/speakencoder.pth"  # 示例URL
    speakencoder_file = os.path.join(audio_dir, "speakencoder.pth")
    speakencoder_checksum = "example_checksum_speakencoder"  # 示例校验和
    
    if not os.path.exists(speakencoder_file) or not verify_file_checksum(speakencoder_file, speakencoder_checksum):
        print("下载SpeakEncoder模型...")
        download_file(speakencoder_url, speakencoder_file, "SpeakEncoder")
        if verify_file_checksum(speakencoder_file, speakencoder_checksum):
            print("SpeakEncoder模型下载并验证成功")
        else:
            print("警告: SpeakEncoder模型校验失败")
    else:
        print("SpeakEncoder模型已存在且校验通过")
    
    print(f"音频模型文件位置: {audio_dir}")


def download_agent_models():
    """下载Agent模型"""
    print("下载Agent模型...")
    agent_dir = os.path.join("models", "agents")
    os.makedirs(agent_dir, exist_ok=True)
    
    # 创建说明文件
    readme_file = os.path.join(agent_dir, "README.md")
    with open(readme_file, "w") as f:
        f.write("# Agent Models\n\n")
        f.write("Agent models are managed by Ollama and MLflow.\n")
        f.write("请使用Ollama拉取模型:\n")
        f.write("```\n")
        f.write("ollama pull qwen:0.5b\n")
        f.write("ollama pull llama2\n")
        f.write("```\n")
    
    print(f"Agent模型说明文件已创建: {readme_file}")


def download_all_models():
    """下载所有模型"""
    print("开始下载所有模型...")
    
    download_stt_models()
    download_tts_models()
    download_audio_models()
    download_agent_models()
    
    print("所有模型下载完成!")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='模型下载工具')
    parser.add_argument('--stt', action='store_true', help='下载STT模型')
    parser.add_argument('--tts', action='store_true', help='下载TTS模型')
    parser.add_argument('--audio', action='store_true', help='下载音频处理模型')
    parser.add_argument('--agent', action='store_true', help='下载Agent模型')
    parser.add_argument('--all', action='store_true', help='下载所有模型')
    
    args = parser.parse_args()
    
    if args.stt:
        download_stt_models()
    elif args.tts:
        download_tts_models()
    elif args.audio:
        download_audio_models()
    elif args.agent:
        download_agent_models()
    elif args.all:
        download_all_models()
    else:
        # 默认下载所有模型
        download_all_models()


if __name__ == '__main__':
    main()