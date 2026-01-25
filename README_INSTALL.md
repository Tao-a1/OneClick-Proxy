# OneClick HTTPS Proxy Installer v2.0

## 安装步骤

### 1. 环境准备 (支持一键安装 Certbot)
进入 `server` 目录运行安装脚本，这将安装 Node.js 和 SSL 证书生成工具 (Certbot)：
```bash
cd server
chmod +x install_env.sh
sudo ./install_env.sh
cd ..
```

### 2. 运行配置向导
在当前目录下运行 Setup 脚本：
```bash
sudo python3 setup.py
```
*(注意：生成 SSL 证书需要 root 权限，建议加 sudo)*

该脚本会：
1. 询问您的 **域名** (例如 `vpn.example.com`)。
2. 询问是否 **自动生成 SSL 证书** (选 y 即可)。
3. 自动配置所有代码，并生成随机密码。
4. **自动打包** 适配该服务器的浏览器插件。

### 3. 启动服务
```bash
cd server
chmod +x start.sh
./start.sh
```

### 4. 客户端使用
1. 下载 `release/OneClick_Client.zip` 到您的电脑并解压。
2. 在 Chrome/Edge 中加载已解压的扩展程序。
