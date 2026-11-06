# 狼蛛键盘（AULA）WebHID 本地 100% 离线驱动控制面板

> 针对 `https://hev.aulacn.com/` 及底层方案商 `*.driveall.cn` 的完整离线化克隆与重构项目。  
> **彻底告别云端依赖：即使未来厂商停运、服务器关停或断网，也能永久在本地修改键盘回报率、灯效、键位、磁轴 RT 行程与刷机升级。**

---

## 🌟 核心特性

- **100% 纯本地离线运行**：所有静态 JS/CSS 运行时、258 种键盘键位矩阵、1336 款设备定义、150+ 款键盘高清图库、灯效预设 JSON、彩屏动图 JSON 均已全部下载并重写为本地相对路径。
- **真正的 WebHID 硬件级通信**：利用 Chromium 原生 WebHID API（`navigator.hid`），直接通过本地 USB/2.4G 接收器与键盘芯片通信。调节回报率（1000Hz/8000Hz）、按键重映射、宏编程、RGB 灯效、快速触发（RT）、防抖延迟**完全不需要任何外网服务器参与**。
- **内置 22 款官方固件升级二进制包**：已抓取官方 `update.json` 清单及全部 22 款官方固件升级程序（`.exe`），支持真正的本地离线固件刷写。
- **零安装门槛、极速秒开**：基于纯 Python 标准库提供轻量本地 HTTP 托管，无需繁重的 Node.js/Electron 依赖，启动仅需 0.1 秒，杜绝杀毒软件误报与弹窗报错。
- **跨平台兼容**：不仅支持 Windows，在 macOS 与 Linux 系统上同样支持通过 Chrome/Edge 浏览器进行离线配置。

---

## 🚀 极速上手使用

### 1. Windows 用户（一键启动）

1. 确保电脑已安装 Python 3（Windows 自带或官方安装版均可）。
2. 双击运行根目录下的 **`启动狼蛛驱动.bat`**。
3. 控制台会自动启动本地服务（默认端口 `http://127.0.0.1:8080`），并自动在你的默认浏览器中打开控制面板。
4. **连接键盘**：使用 USB 数据线或 2.4G 接收器连接键盘，在网页中点击**“连接设备”**，在浏览器弹窗中选中你的键盘并确认授权即可开始调参！

> 💡 **浏览器要求**：WebHID 为 Chromium 标准特性，请使用 **Google Chrome**、**Microsoft Edge**、**Brave**、**Opera** 等现代 Chromium 内核浏览器。

### 2. macOS / Linux 用户

```bash
# 1. 克隆或进入项目目录
git clone https://github.com/nightx521/aula-offline-driver.git
cd aula-offline-driver

# 2. 启动本地离线服务器
python3 server.py

# 3. 在 Chrome / Edge 浏览器中打开
# http://127.0.0.1:8080/#/
```
*(注：Linux 下访问 WebHID 可能需要配置 udev 规则赋予 `/dev/hidraw*` 普通用户访问权限)*。

---

## 📁 目录结构

```text
AULA_config_offline/
├── 启动狼蛛驱动.bat               # 【Windows 一键极速启动】
├── server.py                     # 【本地离线 HTTP 服务】带 Mock API 与动态端口
├── scrape_and_sync.py            # 【自动更新与抓取工具】未来官方有更新时可一键重爬打补丁
├── README.md                     # 项目用户说明
├── HANDOFF.md                    # 详尽的技术架构与交接文档
├── .gitignore                    # Git 忽略配置
├── site/                         # 【100% 完整离线站点资产库，共 216 MB】
│   ├── index.html                # 入口 HTML (已完成本地相对路径重写)
│   ├── favicon.ico               # 狼蛛图标
│   ├── update.json               # 官方固件更新索引
│   ├── *.exe                     # 22 款官方固件二进制升级文件 (离线刷机用)
│   ├── supplier_index.json       # 本地离线品牌配置
│   ├── static/                   # Vue 2 / Element / 键盘核心渲染 JS/CSS/Fonts/Icons
│   └── remote/                   # 解耦自 driveall.cn 的本地化云端资产
│       ├── config/               # 轴体定义、彩屏动图、灯效 JSON、Music.exe
│       └── static/               # 150+ 款键盘高清外观渲染图
└── archive/                      # 【归档】桌面客户端历史实现归档
```

---

## 🔧 技术原理解析

狼蛛（AULA）等外设厂商采用的是 **HFD（深圳华丰/杭州惠尔丰）** 提供的 WebHID SaaS 架构：
1. **硬件报文通信**：网页端在获取 HID 授权后，直接下发对应报文：
   - 报文 `33`：基础回报率与按键数据写入
   - 报文 `43` / `27`：RGB 灯效读写
   - 报文 `37` / `21`：宏定义读写
   - 报文 `38` / `22`：Fn 组合键定义
   - 报文 `80`：彩屏（TFT）图片与动图上传
   - 报文 `66` / `50`：音频律动数据同步
2. **彻底离线化**：本项目完整抓取了远端预设并重构前端路由，将原先所有对 `config.driveall.cn` 与 `static.driveall.cn` 的网络请求全量重写为本地虚拟路由 `/remote/*`，实现了完全脱机运行。

更详尽的架构分析、WAF 绕过细节与技术交接说明，请查阅 [HANDOFF.md](HANDOFF.md)。

---

## 📄 开源许可

本项目遵循 MIT License 协议开源。页面及固件版权归原厂商（AULA 狼蛛）所有，本项目仅供个人离线备份及学习研究使用。
