#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import json
from datetime import datetime

# 配置区（可修改）
DEFAULT_PROXY = "http://127.0.0.1:54890"  # 默认代理
COOKIES_FILE = "cookies.txt"              # Cookies文件路径

def get_timestamp_folder():
    """生成年月日+时间的文件夹名（如202506271114）"""
    return datetime.now().strftime("%Y%m%d%H%M")

def get_best_streams(url, proxy=None, cookies=None):
    """自动检测最佳视频和音频流"""
    try:
        cmd = ['yt-dlp', '-F', url]
        if proxy:
            cmd[1:1] = ['--proxy', proxy]
        if cookies:
            cmd[1:1] = ['--cookies', cookies]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        lines = result.stdout.split('\n')

        # 分析可用的流
        video_streams = []
        audio_streams = []
        
        for line in lines:
            if 'video only' in line:
                parts = line.split()
                stream_id = parts[0]
                resolution = parts[2] if parts[2] != 'audio' else 'N/A'
                codec = parts[3]
                video_streams.append({
                    'id': stream_id,
                    'resolution': resolution,
                    'codec': codec,
                    'line': line
                })
            elif 'audio only' in line:
                parts = line.split()
                audio_streams.append({
                    'id': parts[0],
                    'codec': parts[3],
                    'bitrate': parts[-2] if 'k' in parts[-2] else 'N/A',
                    'line': line
                })

        # 选择最佳视频流（优先vp9编码，其次avc1）
        best_video = None
        for stream in sorted(video_streams, key=lambda x: (
            -int(x['resolution'].split('x')[1]) if 'x' in x['resolution'] else 0,
            x['codec'].startswith('vp9')
        )):
            if not best_video or (stream['codec'].startswith('vp9') and not best_video['codec'].startswith('vp9')):
                best_video = stream

        # 选择最佳音频流（优先opus编码）
        best_audio = None
        for stream in sorted(audio_streams, key=lambda x: (
            x['codec'].startswith('opus'),
            -int(x['bitrate'][:-1]) if x['bitrate'].endswith('k') else 0
        ), reverse=True):
            if not best_audio or (stream['codec'].startswith('opus') and not best_audio['codec'].startswith('opus')):
                best_audio = stream

        return f"{best_video['id']}+{best_audio['id']}"

    except Exception as e:
        print(f"\033[31m❌ 流分析失败: {str(e)}\033[0m")
        return "bestvideo[height<=1080]+bestaudio"  # 退回保守选择

def download_video(url, proxy=None, cookies=None):
    """执行下载任务"""
    folder_name = get_timestamp_folder()
    os.makedirs(folder_name, exist_ok=True)

    try:
        # 获取最佳流组合
        stream_combination = get_best_streams(url, proxy, cookies)
        print(f"\n🔍 自动选择流组合: {stream_combination}")

        cmd = [
            'yt-dlp',
            '-f', stream_combination,
            '--merge-output-format', 'mp4',
            '--output', f'{folder_name}/%(title)s.%(ext)s',
            '--write-subs',
            '--sub-langs', 'en,zh-Hans',
            '--convert-subs', 'srt',
            '--write-thumbnail',
            '--convert-thumbnails', 'png',
            '--write-info-json',
            '--exec', f'''
                echo "视频URL: {url}" > "{folder_name}/视频信息.txt";
                echo "最佳流组合: {stream_combination}" >> "{folder_name}/视频信息.txt";
                jq -r '[.id, .title, .uploader, .upload_date] | join("|")' "{folder_name}/%(title)s.info.json" >> "{folder_name}/视频信息.txt";
                echo "\n------简介------" >> "{folder_name}/视频信息.txt";
                jq -r .description "{folder_name}/%(title)s.info.json" >> "{folder_name}/视频信息.txt";
                rm "{folder_name}/%(title)s.info.json"
            ''',
            url
        ]

        if proxy:
            cmd[1:1] = ['--proxy', proxy]
        if cookies:
            cmd[1:1] = ['--cookies', cookies]

        print(f"\n\033[36m🚀 开始下载到文件夹: {folder_name}\033[0m")
        subprocess.run(cmd, check=True)
        print(f"\n\033[32m✅ 下载完成！文件保存在: \033[34m{folder_name}\033[0m")

    except subprocess.CalledProcessError as e:
        print(f"\033[31m❌ 下载失败: {e.stderr if e.stderr else '未知错误'}\033[0m")
    except Exception as e:
        print(f"\033[31m❌ 发生错误: {str(e)}\033[0m")

if __name__ == "__main__":
    try:
        # 检查依赖
        subprocess.run(['yt-dlp', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['jq', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 用户输入
        print("\n" + "="*40)
        print("📺 智能视频下载器（自动选择最佳画质）")
        print("="*40)
        
        url = input("\n🔗 请输入视频URL: ").strip()
        use_proxy = input(f"🔄 是否使用默认代理 {DEFAULT_PROXY}？(Y/N): ").strip().upper()
        proxy = DEFAULT_PROXY if use_proxy == 'Y' else None
        
        use_cookies = input("🍪 是否使用Cookies文件？(Y/N): ").strip().upper()
        cookies = COOKIES_FILE if use_cookies == 'Y' and os.path.exists(COOKIES_FILE) else None

        download_video(url, proxy, cookies)
    except subprocess.CalledProcessError:
        print("\033[31m❌ 请先安装依赖:")
        print("1. yt-dlp: pip install yt-dlp --upgrade")
        print("2. jq: brew install jq (Mac) 或 sudo apt install jq (Linux)\033[0m")
    except Exception as e:
        print(f"\033[31m❌ 启动失败: {str(e)}\033[0m")