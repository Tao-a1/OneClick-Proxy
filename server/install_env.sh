#!/bin/bash

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root (sudo)"
  exit
fi

echo "=== Installing Dependencies ==="

# 1. Install Node.js
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y nodejs
else
    echo "Node.js is already installed."
fi

# 2. Install Certbot
if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    if [ -x "$(command -v apt-get)" ]; then
        apt-get update
        apt-get install -y certbot
    elif [ -x "$(command -v yum)" ]; then
        yum install -y certbot
    else
        echo "Warning: Could not detect package manager (apt/yum). Please install 'certbot' manually."
    fi
else
    echo "Certbot is already installed."
fi

# 3. Install NPM packages
if [ -f "package.json" ]; then
    echo "Installing NPM packages..."
    npm install
fi

echo "=== Environment Setup Complete ==="
