# Simple HTTP/HTTPS Proxy Server
# 简易 HTTP/HTTPS 代理服务器

## 简介
这是一个基于 Python 标准库实现的轻量级 HTTP 代理服务器，支持 HTTP 和 HTTPS (CONNECT 隧道)。
专为配合 OneClick VPN 浏览器插件设计。

## 配置信息
- **协议**: HTTP
- **端口**: 8083
- **认证方式**: Basic Auth
- **用户名**: myuser
- **密码**: mypass123

## 如何运行
1. 进入目录: `cd http_proxy_server`
2. 给脚本添加权限(如果需要): `chmod +x start.sh stop.sh`
3. 启动服务: `./start.sh`
4. 停止服务: `./stop.sh`

## 日志
运行日志保存在当前目录下的 `proxy.log` 文件中。

## 依赖
需要 Python 3.x (系统通常已预装)。
