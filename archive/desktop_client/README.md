# 桌面客户端归档说明 (Desktop Client Archive)

本目录存放原先尝试开发的 Electron 桌面客户端实现文件。

## 归档原因

1. **依赖过重**：Electron 需要下载安装 180MB+ 的 Node.js/Electron 运行时和 `node_modules`，对只想改改键盘配置的用户而言过于沉重。
2. **Windows Defender 行为误拦截**：在 Windows 11 下，由于安全防护机制，工程目录内动态下载的未签名 `electron.exe` 容易被杀软行为引擎阻断 Mojo 命名管道通信（Named Pipe IPC），导致静默退出。
3. **网页离线版体验更佳**：
   - 网页离线版直接使用系统自带的 Python 启动轻量服务（仅需几十行代码）。
   - Chromium 内核（Chrome、Edge、Brave 等）原生对 `http://localhost` 赋予最高安全信任等级（Secure Context），WebHID API 完全畅通。
   - 启动仅需 0.1 秒，零额外占用，功能与所谓“桌面客户端”完全一致（底层调用的都是一样的 WebHID 报文）。

因此，项目主体已聚焦于 **纯本地轻量 Web 服务 + 浏览器 WebHID** 的优雅离线方案，本目录文件仅作代码归档留存。
