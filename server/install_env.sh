#!/bin/bash
set -e

echo "🚀 开始配置代理服务器环境..."

# 1. 检查并安装 Node.js (v20 LTS)
if ! command -v node &> /dev/null; then
    echo "📦 正在安装 Node.js v20..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
else
    echo "✅ Node.js 已安装: $(node -v)"
fi

# 2. 检查并安装 Certbot (SSL 证书工具)
if ! command -v certbot &> /dev/null; then
    echo "📦 正在安装 Certbot..."
    apt-get update
    apt-get install -y certbot
else
    echo "✅ Certbot 已安装: $(certbot --version)"
fi

echo "------------------------------------------------"
echo "🎉 环境配置完成！"
echo ""
echo "下一步操作："
echo "1. 申请 SSL 证书 (请替换为你自己的域名):"
echo "   certbot certonly --standalone -d vpn.example.com"
echo ""
echo "2. 修改 server/proxy.js 中的证书路径和密码。"
echo ""
echo "3. 启动服务:"
echo "   ./start.sh"
echo "------------------------------------------------"
