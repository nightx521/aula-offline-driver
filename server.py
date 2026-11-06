import http.server
import socketserver
import os
import sys
import webbrowser
import urllib.parse
import json
import subprocess
import time

PORT = 8080
SITE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "site"))

MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".ttf": "font/ttf",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".exe": "application/octet-stream",
}

class AulaOfflineHandler(http.server.BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length) if content_length > 0 else b""

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()

        if "/api/user/login" in path:
            resp = {
                "code": 1,
                "msg": "登录成功(离线模式)",
                "time": "1784596561",
                "data": {
                    "token": "offline_local_token",
                    "userinfo": {
                        "id": 1,
                        "username": "offline_user",
                        "nickname": "离线用户",
                        "avatar": ""
                    }
                }
            }
        else:
            resp = {"code": 1, "msg": "ok", "time": "1784596561", "data": {}}
        self.wfile.write(json.dumps(resp, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        url_parts = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(url_parts.path)

        if path == "/api/supplier/index":
            supp_path = os.path.join(SITE_DIR, "supplier_index.json")
            if os.path.exists(supp_path):
                self.serve_file(supp_path, "application/json; charset=utf-8")
                return
        elif path == "/api/fileinfo/index":
            fi_path = os.path.join(SITE_DIR, "fileinfo_index.json")
            if os.path.exists(fi_path):
                self.serve_file(fi_path, "application/json; charset=utf-8")
                return
        elif path.startswith("/api/"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            resp = {"code": 1, "msg": "ok", "time": "1784596561", "data": {"list": [], "total": 0}}
            self.wfile.write(json.dumps(resp, ensure_ascii=False).encode("utf-8"))
            return

        rel_path = path.lstrip("/")
        if not rel_path or rel_path == "":
            rel_path = "index.html"

        file_path = os.path.normpath(os.path.join(SITE_DIR, rel_path))

        if not file_path.startswith(SITE_DIR):
            self.send_error(403, "Forbidden")
            return

        if os.path.isdir(file_path):
            file_path = os.path.join(file_path, "index.html")

        if not os.path.exists(file_path):
            self.send_error(404, f"File Not Found: {path}")
            return

        ext = os.path.splitext(file_path)[1].lower()
        mime = MIME_TYPES.get(ext, "application/octet-stream")
        self.serve_file(file_path, mime)

    def serve_file(self, file_path, content_type):
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

    def log_message(self, format, *args):
        msg = format % args
        if " 404 " in msg:
            print(f"[-] {msg}")

def find_chromium_browser():
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def run_server(port=PORT):
    is_app_mode = "--app" in sys.argv
    no_browser = "--no-browser" in sys.argv

    for p in range(port, port + 20):
        try:
            server = socketserver.TCPServer(("127.0.0.1", p), AulaOfflineHandler)
            print("=" * 60)
            print("狼蛛键盘 Web 驱动控制面板 (100% 本地离线服务已启动)")
            print(f"本地访问地址: http://127.0.0.1:{p}/#/")
            print("=" * 60)

            app_url = f"http://127.0.0.1:{p}/#/"

            if is_app_mode:
                browser_exe = find_chromium_browser()
                if browser_exe:
                    user_data = os.path.abspath(os.path.join(os.path.dirname(__file__), "app_profile"))
                    print(f"正在以独立桌面客户端窗口模式启动 (引擎: {os.path.basename(browser_exe)})...")
                    cmd = [
                        browser_exe,
                        f"--app={app_url}",
                        "--window-size=1440,900",
                        f"--user-data-dir={user_data}"
                    ]
                    # Start browser in non-blocking way
                    subprocess.Popen(cmd)
                else:
                    print("未找到 Edge/Chrome，切换为默认浏览器打开...")
                    webbrowser.open(app_url)
            elif not no_browser:
                webbrowser.open(app_url)

            server.serve_forever()
            return
        except OSError as e:
            if "address already in use" in str(e).lower() or getattr(e, 'errno', 0) == 10048:
                continue
            raise e

if __name__ == "__main__":
    run_server()
