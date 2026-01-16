const https = require('https');
const http = require('http');
const net = require('net');
const url = require('url');
const fs = require('fs');

const PORT = 8083;
// 预设账号密码
const VALID_USER = 'User_3639e5';
const VALID_PASS = 'Pwd_de2d1accd75ac23b';

// SSL 证书
const options = {
  key: fs.readFileSync('/etc/letsencrypt/live/vpn.lytide.asia/privkey.pem'),
  cert: fs.readFileSync('/etc/letsencrypt/live/vpn.lytide.asia/fullchain.pem')
};

// === IP 白名单管理 ===
// Map<IP_Address, Expiry_Timestamp>
const ipWhitelist = new Map();
const SESSION_DURATION = 24 * 60 * 60 * 1000; // 24小时有效

function isIpAllowed(ip) {
    // 1. 处理 IPv6 映射 (::ffff:1.2.3.4)
    if (ip.startsWith('::ffff:')) {
        ip = ip.substring(7);
    }
    
    const expiry = ipWhitelist.get(ip);
    if (expiry && expiry > Date.now()) {
        return true;
    }
    return false;
}

function addIpToWhitelist(ip) {
    if (ip.startsWith('::ffff:')) {
        ip = ip.substring(7);
    }
    const expiry = Date.now() + SESSION_DURATION;
    ipWhitelist.set(ip, expiry);
    console.log(`[Auth] IP added to whitelist: ${ip} (Expires in 24h)`);
}

// 定期清理过期 IP (每小时)
setInterval(() => {
    const now = Date.now();
    for (const [ip, expiry] of ipWhitelist.entries()) {
        if (expiry <= now) {
            ipWhitelist.delete(ip);
        }
    }
}, 60 * 60 * 1000);

// === HTTP 请求处理 (API + 代理) ===
const server = https.createServer(options, (req, res) => {
    const clientIp = req.socket.remoteAddress;

    // --- 1. API 接口处理 ---
    if (req.url === '/api/login' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                const creds = JSON.parse(body);
                if (creds.username === VALID_USER && creds.password === VALID_PASS) {
                    addIpToWhitelist(clientIp);
                    res.writeHead(200, { 
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*' // 允许跨域调用
                    });
                    res.end(JSON.stringify({ success: true, ip: clientIp }));
                } else {
                    res.writeHead(401, { 
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    });
                    res.end(JSON.stringify({ success: false, error: "Invalid credentials" }));
                }
            } catch (e) {
                res.writeHead(400);
                res.end(JSON.stringify({ success: false, error: "Bad Request" }));
            }
        });
        return;
    }

    // --- 2. 代理请求处理 ---
    
    // 检查白名单
    if (!isIpAllowed(clientIp)) {
        // 如果不在白名单，返回 403 Forbidden (而不是 407)
        // 这样浏览器就不会弹窗，而是直接显示拒绝访问
        res.writeHead(403);
        res.end('Access Denied. Please login via extension first.');
        return;
    }

    // 正常代理逻辑
    let requestUrl = req.url;
    if (!requestUrl.startsWith('http')) {
        requestUrl = 'http://' + req.headers.host + req.url;
    }
    
    const parsedUrl = url.parse(requestUrl);
    const proxyOptions = {
        hostname: parsedUrl.hostname,
        port: parsedUrl.port || 80,
        path: parsedUrl.path,
        method: req.method,
        headers: req.headers
    };

    const proxyReq = http.request(proxyOptions, (proxyRes) => {
        res.writeHead(proxyRes.statusCode, proxyRes.headers);
        proxyRes.pipe(res, { end: true });
    });

    proxyReq.on('error', (err) => {
        if (!res.headersSent) {
            res.writeHead(502);
            res.end('Bad Gateway');
        }
    });

    req.pipe(proxyReq, { end: true });
});

// === CONNECT 处理 (HTTPS 隧道) ===
server.on('connect', (req, clientSocket, head) => {
    const clientIp = req.socket.remoteAddress;

    // 检查白名单
    if (!isIpAllowed(clientIp)) {
        clientSocket.write('HTTP/1.1 403 Forbidden\r\n\r\n');
        clientSocket.end();
        return;
    }

    let target = req.url;
    let hostname, port;

    if (target.includes(':')) {
        const parts = target.split(':');
        hostname = parts[0];
        port = parts[1];
    } else {
        hostname = target;
        port = 443;
    }

    const serverSocket = net.connect(port, hostname, () => {
        clientSocket.write('HTTP/1.1 200 Connection Established\r\n\r\n');
        serverSocket.write(head);
        serverSocket.pipe(clientSocket);
        clientSocket.pipe(serverSocket);
    });

    serverSocket.on('error', (err) => {
        try { clientSocket.write('HTTP/1.1 502 Bad Gateway\r\n\r\n'); } catch (e) {}
    });
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`Node.js Secure Proxy (API Auth Mode) running on port ${PORT}`);
});
