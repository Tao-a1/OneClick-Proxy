# OneClick HTTPS Proxy

A lightweight, secure HTTPS proxy server solution that automatically configures a Chrome extension for easy connection.

## Features
- **One-Click Deployment**: Setup scripts for both IP-based and Domain-based deployment.
- **Automatic Extension Configuration**: Generates a pre-configured Chrome extension `.zip` file.
- **Country Detection**: Automatically names the extension based on the server's location (e.g., "Singapore", "Japan").
- **Secure**: Supports HTTPS/SSL (Self-Signed or Let's Encrypt).
- **Authentication**: Unique credentials generated for each deployment.

## Installation

### Prerequisites
- Python 3
- Node.js (for the proxy server)
- Certbot (only if using Domain mode)

### 1. IP-Based Deployment (No Domain)
Use this if you just want a quick proxy using your server's IP address.

```bash
# 1. Clone the repo
git clone https://github.com/Tao-a1/OneClick-Proxy.git
cd OneClick-Proxy

# 2. Run the deployment script
python3 auto_deploy.py
```

This will:
- Generate a self-signed SSL certificate for your IP.
- Start the proxy server on port 8083.
- Generate a `release/OneClick_Client.zip` extension.

**Note**: Since it uses a self-signed certificate, you may need to install the generated CA certificate (`server/certs/fullchain.pem`) on your client machine as a Trusted Root Certificate.

### 2. Domain-Based Deployment (Recommended)
Use this if you have a domain pointing to your server.

**Prerequisite**: Ensure you have already generated an SSL certificate using Certbot for your domain.
```bash
certbot certonly --standalone -d your.domain.com
```

**Deploy**:
```bash
python3 deploy_with_domain.py your.domain.com
```

This will:
- Copy your existing Let's Encrypt certificates.
- Configure and start the proxy server.
- Generate a `release/OneClick_Client.zip` extension.
- Update the extension name to match the server location.

## Client Usage
1. Download the generated `release/OneClick_Client.zip` from your server.
2. Unzip it on your local computer.
3. Open Chrome/Edge -> Extensions -> Manage Extensions.
4. Enable "Developer mode".
5. Click "Load unpacked" and select the unzipped folder.
6. The proxy will connect automatically!

## License
MIT
