#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AULA 狼蛛键盘 Web 驱动站点全量爬取与离线化补丁脚本 (scrape_and_sync.py)
用于从 https://hev.aulacn.com/ 与 *.driveall.cn 完整镜像所有静态资源并打上离线路径补丁。
"""

import os
import sys
import re
import json
import time
import urllib.request
import urllib.error
import urllib.parse
import http.cookiejar
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://hev.aulacn.com"
CONFIG_CDN = "https://config.driveall.cn"
STATIC_CDN = "https://static.driveall.cn"
CP_API = "https://cp.driveall.cn"

SITE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "site"))
REMOTE_CONFIG_DIR = os.path.join(SITE_DIR, "remote", "config")
REMOTE_STATIC_DIR = os.path.join(SITE_DIR, "remote", "static")

# 1. 初始化带 Cookie 保持的 Opener (解决首访 403 WAF Cookie 校验)
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener.addheaders = [
    ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
]

def request_url(url, timeout=15):
    # 自动重试 3 次，首访处理 403 Cookie Challenge
    for attempt in range(3):
        try:
            resp = opener.open(url, timeout=timeout)
            return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 403 and attempt == 0:
                time.sleep(0.5)
                continue
            if attempt == 2:
                raise
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1)

def download_file(url, local_path):
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        return True, "exists"
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    try:
        data = request_url(url)
        with open(local_path, "wb") as f:
            f.write(data)
        return True, f"{len(data)} B"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("  开始执行 AULA 狼蛛键盘网页端驱动全量镜像与离线化")
    print("=" * 60)

    # 1. 抓取 index.html
    print("\n[1/7] 抓取首页 index.html ...")
    html_data = request_url(BASE_URL + "/")
    html_text = html_data.decode("utf-8", errors="ignore")
    index_path = os.path.join(SITE_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_text)
    print(f"  [OK] 已保存 index.html ({len(html_text)} 字符)")

    # 2. 提取并下载所有的 JS / CSS 核心包
    print("\n[2/7] 抓取核心静态资源 (JS/CSS/Fonts/Icons) ...")
    scripts = re.findall(r'src="(static/js/[^"]+)"', html_text)
    links = re.findall(r'href="(static/css/[^"]+)"', html_text)
    core_assets = scripts + links

    for rel in core_assets:
        url = f"{BASE_URL}/{rel}"
        local = os.path.join(SITE_DIR, rel)
        ok, msg = download_file(url, local)
        print(f"  [{'OK' if ok else 'FAIL'}] {rel}: {msg}")

    # 3. 抓取字体与界面图片图标
    print("\n[3/7] 抓取界面字体与图标素材 ...")
    app_js_path = [os.path.join(SITE_DIR, s) for s in scripts if 'app.' in s][0]
    with open(app_js_path, "r", encoding="utf-8") as f:
        app_js_text = f.read()

    icon_paths = set(re.findall(r'static/(?:img|fonts)/[a-zA-Z0-9_\.\-]+', app_js_text))
    # 加上标准的 element 图标和字体
    icon_paths.update([
        'static/fonts/element-icons.f1a45d74.ttf',
        'static/fonts/element-icons.ff18efd1.woff',
        'static/fonts/iconfont.20d86295.ttf'
    ])
    for rel in sorted(icon_paths):
        url = f"{BASE_URL}/{rel}"
        local = os.path.join(SITE_DIR, rel)
        ok, msg = download_file(url, local)
        print(f"  [{'OK' if ok else 'FAIL'}] {rel}: {msg}")

    # 4. 下载全量固件升级配置文件与升级包二进制文件
    print("\n[4/7] 抓取官方固件更新清单与固件二进制文件 (*.exe) ...")
    update_json_url = f"{BASE_URL}/update.json"
    update_json_path = os.path.join(SITE_DIR, "update.json")
    try:
        up_data = request_url(update_json_url)
        with open(update_json_path, "wb") as f:
            f.write(up_data)
        updates = json.loads(up_data.decode("utf-8"))
        print(f"  [OK] update.json 包含 {len(updates)} 项固件配置")
        for item in updates:
            for key in ['file_name', 'highlight_name']:
                if key in item:
                    fn = item[key]
                    fw_url = f"{BASE_URL}/{urllib.parse.quote(fn)}"
                    fw_dest = os.path.join(SITE_DIR, fn)
                    ok, msg = download_file(fw_url, fw_dest)
                    print(f"    [{'OK' if ok else 'FAIL'}] 固件 {fn}: {msg}")
    except Exception as e:
        print(f"  [FAIL] 抓取固件更新失败: {e}")

    # 5. 抓取 driveall.cn CDN 核心数据
    print("\n[5/7] 抓取 driveall.cn 云端数据 (轴体/灯效/屏幕动画/键盘图库) ...")
    # 基础配置文件
    cdn_bases = [
        (f"{CONFIG_CDN}/axial.json", os.path.join(REMOTE_CONFIG_DIR, "axial.json")),
        (f"{CONFIG_CDN}/gif/defaultGif.json", os.path.join(REMOTE_CONFIG_DIR, "gif", "defaultGif.json")),
        (f"{CONFIG_CDN}/logo/aula/favicon.ico", os.path.join(SITE_DIR, "favicon.ico")),
        (f"{CONFIG_CDN}/logo/hfd/logo.png", os.path.join(REMOTE_CONFIG_DIR, "logo", "hfd", "logo.png")),
        (f"{CONFIG_CDN}/music/v2/Music.exe", os.path.join(REMOTE_CONFIG_DIR, "music", "v2", "Music.exe")),
        (f"{STATIC_CDN}/static/keyboards/kb_bg.png", os.path.join(REMOTE_STATIC_DIR, "keyboards", "kb_bg.png")),
        (f"{STATIC_CDN}/static/mouses/hfd.png", os.path.join(REMOTE_STATIC_DIR, "mouses", "hfd.png")),
        (f"{CP_API}/api/supplier/index", os.path.join(SITE_DIR, "supplier_index.json")),
        (f"{CP_API}/api/fileinfo/index", os.path.join(SITE_DIR, "fileinfo_index.json")),
    ]
    for url, dest in cdn_bases:
        ok, msg = download_file(url, dest)
        print(f"  [{'OK' if ok else 'FAIL'}] {os.path.basename(dest)}: {msg}")

    # 6. 对 app.js 与 index.html 进行离线化重写
    print("\n[6/7] 执行代码重写，切断远程依赖，转向本地端点 ...")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
    html = html.replace('https://config.driveall.cn/logo/aula/favicon.ico', 'favicon.ico')
    html = re.sub(r'<script[^>]*bt-stats\.js[^>]*></script>', '<script defer src="bt-stats.js"></script>', html)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    # 确保 bt-stats.js 存在以防控制台 404
    bt_stats_path = os.path.join(SITE_DIR, "bt-stats.js")
    if not os.path.exists(bt_stats_path):
        open(bt_stats_path, "w", encoding="utf-8").write("")

    with open(app_js_path, "r", encoding="utf-8") as f:
        js = f.read()
    js = js.replace("https://config.driveall.cn", "/remote/config")
    js = js.replace("https://static.driveall.cn", "/remote")
    js = js.replace("https://cp.driveall.cn", "")
    with open(app_js_path, "w", encoding="utf-8") as f:
        f.write(js)
    print("  [OK] 代码补丁应用完成！")

    print("\n[7/7] 离线化制作完毕！")
    print("现在双击运行 `启动狼蛛驱动_网页版.bat` 即可完全离线使用！")

if __name__ == "__main__":
    main()
