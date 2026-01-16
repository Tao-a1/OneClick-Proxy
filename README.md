# 🚀 HTTPS Secure Proxy & OneClick Extension
**(HTTPS 安全代理服务 + 零配置浏览器插件)**

这是一个轻量级、高安全性的 Web 代理解决方案。它包含一个基于 Node.js 的 HTTPS 代理服务端，以及一个预配置好的 Chrome/Edge 浏览器扩展。

## ✨ 特性 (Features)

*   **🔒 HTTPS 加密传输**: 所有流量经过 TLS 加密，有效防止防火墙探测和干扰。
*   **⚡️ 零配置插件**: 插件已内置服务器地址和加密凭据，用户下载安装即用，无需填写任何设置。
*   **🔑 自动认证**: 插件内置自动应答机制，彻底解决浏览器反复弹出密码框的问题。
*   **🚀 高性能**: 基于 Node.js 事件驱动模型，资源占用极低。

---

## 📂 目录结构

*   `server/` - 代理服务器端代码 (Node.js)
*   `extension/` - 浏览器插件源码
*   `release/` - **[推荐]** 供用户直接下载安装的插件包 (.zip)

---

## 🛠 服务端部署 (Server Setup)

### 1. 环境准备 (一键安装)
我们提供了一个脚本来自动安装 Node.js 和 Certbot：

```bash
cd server
chmod +x install_env.sh
sudo ./install_env.sh
```

### 2. 申请 SSL 证书
代理服务必须使用 HTTPS，因此你需要一个域名和证书。
```bash
# 请将 vpn.yourdomain.com 替换为你实际解析到本机的域名
sudo certbot certonly --standalone -d vpn.yourdomain.com
```

### 3. 配置文件
修改 `server/proxy.js` 中的配置：

```javascript
const PORT = 8083;
const USERNAME = 'myuser';
const PASSWORD = 'mypass123';
// SSL 证书路径
const options = {
  key: fs.readFileSync('/etc/letsencrypt/live/your.domain.com/privkey.pem'),
  cert: fs.readFileSync('/etc/letsencrypt/live/your.domain.com/fullchain.pem')
};
```

### 3. 运行服务
```bash
cd server
chmod +x start.sh stop.sh

# 启动服务 (后台运行)
./start.sh

# 停止服务
./stop.sh
```

---

## 🧩 插件安装 (Client Installation)

本插件支持 Chrome、Edge、Brave 等所有 Chromium 内核浏览器。

1.  **下载插件**:
    *   进入本仓库的 `release` 目录，下载 `OneClick_VPN_Extension_v1.0.zip`。
    *   **解压** 该压缩包到一个文件夹。

2.  **加载扩展**:
    *   在浏览器地址栏输入 `chrome://extensions/` (Chrome) 或 `edge://extensions/` (Edge)。
    *   打开右上角的 **开发者模式 (Developer Mode)** 开关。
    *   点击左上角的 **加载已解压的扩展程序 (Load Unpacked)**。
    *   选择步骤 1 中解压的文件夹。

3.  **使用**:
    *   点击浏览器右上角的插件图标。
    *   点击 **“开启代理”**，当状态变为绿色 🟢 即表示连接成功。

---

## ⚠️ 免责声明
本项目仅供技术研究和教育使用，请遵守当地法律法规。
