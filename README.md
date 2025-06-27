                                     video-download
python script for download youtube, twitter and bilibili videos with covers and subtitles

介绍

视频下载脚本，可下载YouTube，twitter，哔哩哔哩视频。同时下载视频封面，字幕和视频简介。

准备工作

for mac pc

bash

1. brew install yt-dlp

2. brew install jq

脚本修改

1. 查看是否使用了代理，可以在脚本里添加代理，修改自己的代理地址就行。

 DEFAULT_PROXY = "http://127.0.0.1:54890" # 默认代理

2. 添加网页cookie，浏览器中使用Get cookies.txt LOCALLY插件，下载并命令为cookies.txt，保存在和脚本同一目录下。

 COOKIES_FILE = "cookies.txt" # Cookies文件路径

示例：


1. bash： python my_download.py


<img width="1193" alt="截屏2025-06-27 16 36 20" src="https://github.com/user-attachments/assets/c71eaaec-099d-4591-9780-a9f1db4f8ac9" />


2. 结果会自动保存在一个以时间戳为单位的文件夹里。包含封面，视频简介，视频格式为.mp4。

<img width="935" alt="截屏2025-06-27 16 42 57" src="https://github.com/user-attachments/assets/86862817-91f8-4008-a09b-0793033f13db" />


3. 视频选择了最大分辨率下载，音频最最优码率。


<img width="391" alt="截屏2025-06-27 16 49 15" src="https://github.com/user-attachments/assets/4a5ceb31-8a62-4720-aa6a-403c2f0f7203" />

