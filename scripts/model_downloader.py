#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模型下载脚本
"""

import os
import sys
import urllib.request
from tqdm import tqdm


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


def download_stt_models():
    """下载STT模型"""
    print("下载STT模型...")
    stt_dir = os.path.join("models", "stt")
    os.makedirs(stt_dir, exist_ok=True)
    
    # 这里应该是实际的模型下载链接
    # 由于是示例，我们创建一个占位文件
    placeholder_file = os.path.join(stt_dir, "stt_model_placeholder.txt")
    with open(placeholder_file, "w") as f:
        f.write("STT模型占位文件\n")
        f.write("实际使用时应替换为真实的STT模型文件\n")
    
    print(f"STT模型占位文件已创建: {placeholder_file}")


def download_tts_models():
    """下载TTS模型"""
    print("下载TTS模型...")
    tts_dir = os.path.join("models", "tts")
    os.makedirs(tts_dir, exist_ok=True)
    
    # 创建占位文件
    placeholder_file = os.path.join(tts_dir, "tts_model_placeholder.txt")
    with open(placeholder_file, "w") as f:
        f.write("TTS模型占位文件\n")
        f.write("实际使用时应替换为真实的TTS模型文件\n")
    
    print(f"TTS模型占位文件已创建: {placeholder_file}")


def download_agent_models():
    """下载Agent模型"""
    print("下载Agent模型...")
    agent_dir = os.path.join("models", "agents")
    os.makedirs(agent_dir, exist_ok=True)
    
    # 创建占位文件
    placeholder_file = os.path.join(agent_dir, "agent_model_placeholder.txt")
    with open(placeholder_file, "w") as f:
        f.write("Agent模型占位文件\n")
        f.write("实际使用时应替换为真实的Agent模型文件\n")
    
    print(f"Agent模型占位文件已创建: {placeholder_file}")


def download_all_models():
    """下载所有模型"""
    print("开始下载所有模型...")
    
    download_stt_models()
    download_tts_models()
    download_agent_models()
    
    print("所有模型下载完成!")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='模型下载工具')
    parser.add_argument('--stt', action='store_true', help='下载STT模型')
    parser.add_argument('--tts', action='store_true', help='下载TTS模型')
    parser.add_argument('--agent', action='store_true', help='下载Agent模型')
    parser.add_argument('--all', action='store_true', help='下载所有模型')
    
    args = parser.parse_args()
    
    if args.stt:
        download_stt_models()
    elif args.tts:
        download_tts_models()
    elif args.agent:
        download_agent_models()
    elif args.all:
        download_all_models()
    else:
        # 默认下载所有模型
        download_all_models()


if __name__ == '__main__':
    main()