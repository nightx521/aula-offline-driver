const { app, BrowserWindow, session } = require('electron');
const path = require('path');
const http = require('http');
const fs = require('fs');
const url = require('url');

// 适配特殊 Windows 权限与沙箱环境
app.commandLine.appendSwitch('no-sandbox');
app.commandLine.appendSwitch('disable-gpu-sandbox');

// 将应用数据目录重定向到本地，防止 Windows 权限拦截
const localData = path.join(__dirname, 'electron_data');
try {
  if (!fs.existsSync(localData)) {
    fs.mkdirSync(localData, { recursive: true });
  }
  app.setPath('userData', path.join(localData, 'user'));
  app.setPath('sessionData', path.join(localData, 'session'));
} catch (_) {}

let server;
let mainWindow;

const SITE_DIR = path.join(__dirname, 'site');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.ico': 'image/x-icon',
  '.svg': 'image/svg+xml',
  '.ttf': 'font/ttf',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.exe': 'application/octet-stream'
};

function startLocalServer(callback) {
  server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url, true);
    let reqPath = decodeURIComponent(parsedUrl.pathname);

    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', '*');

    if (req.method === 'OPTIONS') {
      res.statusCode = 200;
      res.end();
      return;
    }

    if (reqPath === '/api/supplier/index') {
      const suppPath = path.join(SITE_DIR, 'supplier_index.json');
      if (fs.existsSync(suppPath)) {
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        fs.createReadStream(suppPath).pipe(res);
        return;
      }
    } else if (reqPath === '/api/fileinfo/index') {
      const fiPath = path.join(SITE_DIR, 'fileinfo_index.json');
      if (fs.existsSync(fiPath)) {
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        fs.createReadStream(fiPath).pipe(res);
        return;
      }
    } else if (reqPath.startsWith('/api/')) {
      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify({ code: 1, msg: 'ok', data: { list: [], total: 0 } }));
      return;
    }

    if (reqPath === '/' || reqPath === '') {
      reqPath = '/index.html';
    }

    const fullPath = path.normalize(path.join(SITE_DIR, reqPath));

    if (!fullPath.startsWith(SITE_DIR)) {
      res.statusCode = 403;
      res.end('Forbidden');
      return;
    }

    const ext = path.extname(fullPath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    fs.readFile(fullPath, (err, data) => {
      if (err) {
        if (err.code === 'ENOENT') {
          res.statusCode = 404;
          res.end(`Not Found: ${reqPath}`);
        } else {
          res.statusCode = 500;
          res.end('Internal Server Error');
        }
      } else {
        res.writeHead(200, { 'Content-Type': contentType });
        res.end(data);
      }
    });
  });

  server.listen(0, '127.0.0.1', () => {
    const port = server.address().port;
    console.log(`[AULA Driver] 本地离线 HTTP 服务运行于: http://127.0.0.1:${port}`);
    callback(port);
  });
}

function createWindow(port) {
  const iconPath = path.join(SITE_DIR, 'favicon.ico');

  mainWindow = new BrowserWindow({
    width: 1440,
    height: 900,
    title: "狼蛛键盘本地离线驱动 (AULA Driver Offline)",
    icon: fs.existsSync(iconPath) ? iconPath : undefined,
    autoHideMenuBar: true,
    show: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false,
      zoomFactor: 0.9
    }
  });

  mainWindow.loadURL(`http://127.0.0.1:${port}/#/`);

  mainWindow.once('ready-to-show', () => {
    mainWindow.maximize();
    mainWindow.show();
  });

  // WebHID 自动静默授权与选择
  const ses = mainWindow.webContents.session;

  ses.on('select-hid-device', (event, details, callback) => {
    event.preventDefault();
    if (details.deviceList && details.deviceList.length > 0) {
      console.log('[WebHID] 自动连接设备:', details.deviceList[0].name || details.deviceList[0].productId);
      callback(details.deviceList[0].deviceId);
    } else {
      callback(''); // 传入空字符串取消选择，切勿传入 undefined
    }
  });

  ses.setPermissionCheckHandler((webContents, permission) => {
    if (permission === 'hid') return true;
    return true; // 允许本地上下文权限
  });

  ses.setDevicePermissionHandler((details) => {
    return details.deviceType === 'hid';
  });
}

app.whenReady().then(() => {
  startLocalServer((port) => {
    createWindow(port);
  });
});

app.on('window-all-closed', () => {
  if (server) {
    server.close();
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
