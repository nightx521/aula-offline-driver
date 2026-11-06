# 狼蛛键盘（AULA）离线驱动控制面板 - 项目交接文档 (HANDOFF.md)

---

## 一、 项目背景与交付目标

- **原始站点**：`https://hev.aulacn.com/#/`
- **方案商云端**：`https://config.driveall.cn` / `https://static.driveall.cn` / `https://cp.driveall.cn`
- **立项痛点**：狼蛛（AULA）全系列键盘（如 F75、F87 Pro、F99 MAX、NOVA 系列、MINI 磁轴系列等）目前高度依赖网页端驱动进行回报率切换（1000Hz/8000Hz）、按键重映射、RGB 灯效调节、快速触发（Rapid Trigger 磁轴行程）与固件升级。若厂商未来倒闭、服务器欠费或域名关停，键盘将丧失调参和升级能力。
- **交付目标**：实现一套 **100% 自包含、开箱即用、零外部依赖** 的永久离线控制系统，并已完成代码重构、资产去云端化、固件离线包归档及 GitHub 开源发布。

---

## 二、 系统架构与关键技术原理

```
[ 用户物理键盘 / 2.4G接收器 ]
             ▲
             │ USB / 蓝牙 HID 协议报文 (Report ID: 33, 43, 27, 37, 80 等)
             ▼
[ 现代 Chromium 内核浏览器 (Chrome / Edge / Brave 等) ]
             ▲
             │ navigator.hid (WebHID API, 原生支持 http://localhost 顶级信任域)
             ▼
[ 本地自包含 Web 控制面板 (Vue 2 + Element-UI + 键盘核心渲染引擎) ]
             ▲
             │ HTTP 请求 (所有远程 CDN 路径均已被重写为本地相对路径)
             ▼
[ 本地轻量化 HTTP 服务 (server.py - 纯 Python 原生标准库，带 Mock API 路由) ]
```

### 1. 为什么该控制面板可以 100% 离线运行？
- **硬件通信本质**：驱动调节回报率、自定义宏、改键位、RGB 调色并不是通过向服务器发请求实现的，而是前端 JavaScript 直接调用浏览器的标准 **WebHID API**（`navigator.hid.requestDevice` 与 `device.sendReport` / `device.receiveFeatureReport`），通过 USB 总线与键盘 MCU 芯片直接握手。
- **设备配置早已打包进前端**：前端的 `chunk-keyboard` 与 `app.js` 中早已内置了 **258 种键盘矩阵布局算法** 以及 **1336 款设备的参数定义**（包含按键物理坐标、轴体行程区间、旋钮功能配置等），无需联网下载。

### 2. 攻克的三大难点与代码重构
1. **反爬与 WAF 穿透**：
   `hev.aulacn.com` 部署有雷池/Nginx 拦截层，外部爬虫首次请求会返回 `403 Forbidden` 并附带加密的 `Set-Cookie`。爬虫脚本（`scrape_and_sync.py`）中集成了带 Cookie 保持的会话处理器，模拟浏览器自动解算并复用会话，实现自动化全量抓取。
2. **切断 `driveall.cn` 云端 CDN 强绑定**：
   - 原前端代码深度依赖方案商远程 CDN（`config.driveall.cn` 获取轴体配置、彩屏 GIF 动画、预设灯效；`static.driveall.cn` 获取 150+ 款键盘的高清外观图）。
   - **重构方案**：对 `index.html` 与 `app.c35ca532.js` 实施正则扫描重写，将所有远程云端绝对 URL 彻底替换为本地虚拟路径 `/remote/config` 与 `/remote/static`，并已将云端数据全部下载至本地 `site/` 对应目录。
3. **本地 Mock API 支撑**：
   原网站启动时会调用供应商接口 `/api/supplier/index`，若接口 404 会影响品牌样式加载。`server.py` 中实现了本地路由拦截，返回真实的 `supplier_index.json`（已匹配 AULA 狼蛛品牌 ID 54），并在纯离线状态下提供模拟认证，杜绝前端报错。

---

## 三、 项目资产与数据清单

本项目当前本地自包含资产共计 **415 个文件，约 216 MB**：

| 模块分类 | 路径 | 内容与规模 |
| :--- | :--- | :--- |
| **入口与基础** | `site/index.html`, `site/favicon.ico` | 驱动入口与本地狼蛛 Logo 图标 |
| **前端运行时** | `site/static/js/`, `site/static/css/` | Vue 2、Element-UI、Pintura 图形引擎、键盘渲染核心模块 |
| **静态字体与矢量** | `site/static/fonts/`, `site/static/img/` | `element-icons`、`iconfont`、全套多语言国旗 SVG、轴体示意图 |
| **键盘外观图库** | `site/remote/static/keyboards/` | 全网 **150+ 款键盘高清渲染图**（包括 F75、F87 Pro、F99 MAX、NOVA99、A80、S87 等） |
| **灯效与屏幕配置** | `site/remote/config/` | `axial.json` 轴体数据、全套 `r7c70`/`r5c63`/`r7c7`/`r5c51`/`r5c67` LED 预设 JSON、彩屏动图数据 |
| **官方离线固件包** | `site/*.exe`, `site/update.json` | 官方固件更新清单及 **全套 22 款键盘固件升级二进制程序**（F87 Pro 各版本、F108、MINI 系列等） |
| **音乐律动助手** | `site/remote/config/music/v2/` | `Music.exe`（官方音频拾音与屏幕光效同步桌面助手） |

---

## 四、 核心文件索引与职责

```text
AULA_config_offline/
├── 启动狼蛛驱动.bat               # 【用户入口】Windows 一键极速启动脚本 (GBK编码，自动唤起浏览器)
├── server.py                     # 【核心服务】轻量本地 HTTP 服务器 (路由重写、Mock API、MIME 处理)
├── scrape_and_sync.py            # 【更新工具】全量自动化在线爬取与离线打补丁脚本 (上游更新时使用)
├── README.md                     # 【说明文档】面向终端用户的完整使用指南
├── HANDOFF.md                    # 【交接文档】本项目架构设计与技术移交说明
├── .gitignore                    # Git 忽略配置
├── site/                         # 【核心资产库】解耦打补丁后的完整离线站点 (216 MB)
└── archive/                      # 【归档目录】
    └── desktop_client/           # Electron 桌面客户端历史源码归档 (因依赖过重与杀软误报已归档)
```

---

## 五、 操作与运行指引

### 1. 终端用户日常使用
1. 双击运行 `启动狼蛛驱动.bat`。
2. 本地服务器（默认端口 8080）自动启动，并在默认浏览器中弹出控制面板。
3. 键盘通过 USB 有线或 2.4G 接收器连接电脑，点击界面上的**“连接设备”**，在浏览器 WebHID 授权弹窗中选中键盘即可正常配置。
4. 关闭黑窗口命令行即停止服务。

### 2. 跨平台运行（macOS / Linux）
控制面板不局限于 Windows，在 macOS 或 Linux 上同样可用：
```bash
# 进入工程目录
cd AULA_config_offline
# 启动本地服务
python3 server.py
# 浏览器访问
open http://localhost:8080/#/
```
*(注：Linux 下访问 WebHID 可能需要配置 udev 规则赋予 `/dev/hidraw*` 普通用户读写权限)*。

### 3. 上游更新同步指引（开发者）
若未来官方网站发布了全新键盘型号或新固件，可在联网环境下运行：
```bash
python scrape_and_sync.py
```
脚本会自动重新获取增量资源、拉取新固件，并自动为最新的 JS/HTML 文件注入本地化相对路由补丁。

---

## 六、 桌面客户端归档说明 (Decision Record)

在开发阶段曾调研并实现了基于 Electron 的独立桌面客户端版本（代码已归档于 `archive/desktop_client/`）。经实际测试后决定全面转向 Python WebServer 方案，主要决策原因如下：
1. **依赖臃肿**：Electron 需要下载近 200MB 的二进制依赖及数百个 npm 包，给普通用户的初次上手造成极高门槛。
2. **Windows 杀软误拦截风险**：在 Windows 11 下，工程目录动态安装的未签名 `electron.exe` 频繁被 Windows Defender 行为引擎拦截 Mojo Named Pipe IPC 通信（表现为启动静默崩溃）。
3. **功能完全等价**：Chromium（Chrome / Edge）原生赋予 `http://localhost` 最高的安全上下文信任权限，通过 Python 启动网页版的 WebHID 与桌面版无任何硬件通信差异，且启动速度提升 10 倍以上。

---

**交付状态**：项目已完成全部资产离线化、补丁重写、文档归档，并在 GitHub 完成全新开源仓库推送。
