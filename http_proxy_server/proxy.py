import http.server
import socketserver
import socket
import select
import base64
import urllib.parse
import sys

# 配置
PORT = 8083
USERNAME = "myuser"
PASSWORD = "mypass123"

# 构造预期的认证头值
AUTH_STRING = f"{USERNAME}:{PASSWORD}"
AUTH_B64 = base64.b64encode(AUTH_STRING.encode("utf-8")).decode("utf-8")
EXPECTED_AUTH_HEADER = f"Basic {AUTH_B64}"

class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def _send_auth_request(self):
        self.send_response(407)
        self.send_header("Proxy-Authenticate", 'Basic realm="Proxy"')
        self.end_headers()

    def _check_auth(self):
        auth_header = self.headers.get("Proxy-Authorization")
        if not auth_header or auth_header != EXPECTED_AUTH_HEADER:
            self._send_auth_request()
            return False
        return True

    def do_CONNECT(self):
        if not self._check_auth():
            return

        address = self.path.split(":", 1)
        if len(address) == 1:
            address.append(80)
        host, port = address[0], int(address[1])

        try:
            s_remote = socket.create_connection((host, port))
        except Exception as e:
            self.send_error(502, f"Bad Gateway: {e}")
            return

        self.send_response(200, "Connection Established")
        self.end_headers()

        # 隧道传输数据
        conns = [self.connection, s_remote]
        try:
            while True:
                rlist, _, _ = select.select(conns, [], [], 10)
                if not rlist:
                    # 超时或无数据，通常保持连接直到一方关闭
                    continue
                    
                if self.connection in rlist:
                    data = self.connection.recv(4096)
                    if not data: break
                    s_remote.sendall(data)
                
                if s_remote in rlist:
                    data = s_remote.recv(4096)
                    if not data: break
                    self.connection.sendall(data)
        except Exception:
            pass
        finally:
            s_remote.close()
            self.connection.close()

    def do_GET(self):
        self._handle_http_request()

    def do_POST(self):
        self._handle_http_request()

    def do_PUT(self):
        self._handle_http_request()

    def do_DELETE(self):
        self._handle_http_request()
    
    def do_HEAD(self):
        self._handle_http_request()
        
    def do_OPTIONS(self):
        self._handle_http_request()

    def _handle_http_request(self):
        if not self._check_auth():
            return

        url = self.path
        # 简单解析 URL 获取 host 和 port
        # 浏览器发给代理的 path 通常是完整 URL: http://www.google.com/foo
        u = urllib.parse.urlparse(url)
        if u.scheme != 'http' and u.scheme != 'ftp':
            self.send_error(400, "Unsupported scheme (only http/ftp or CONNECT for https)")
            return

        host = u.hostname
        port = u.port or 80
        path = u.path
        if u.query:
            path += "?" + u.query

        try:
            # 连接远程服务器
            s_remote = socket.create_connection((host, port))
            
            # 构造新的请求行
            # 注意：这里我们简单转发，去掉 Proxy-* 头
            # HTTP/1.1 需要 Host 头
            
            # 发送请求行
            req_line = f"{self.command} {path} {self.request_version}\r\n"
            s_remote.sendall(req_line.encode('iso-8859-1'))
            
            # 发送 header
            # 过滤掉 Proxy-Authorization, Proxy-Connection 等
            for key, value in self.headers.items():
                if key.lower() in ['proxy-authorization', 'proxy-connection', 'connection', 'keep-alive']:
                    continue
                s_remote.sendall(f"{key}: {value}\r\n".encode('iso-8859-1'))
            
            # 添加 Connection: close 简化处理（不支持 Keep-Alive 以避免复杂性）
            s_remote.sendall(b"Connection: close\r\n")
            s_remote.sendall(b"\r\n")

            # 发送 Body (如果有)
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length)
                s_remote.sendall(body)

            # 读取响应并转发回客户端
            # 这里简单地读取所有数据并转发，或者解析响应头
            # 为了简单起见，我们使用 makefile 读取响应头，然后流式传输 body
            
            f_remote = s_remote.makefile("rb")
            
            # 读取状态行
            status_line = f_remote.readline()
            if not status_line:
                return # 没数据
            
            self.wfile.write(status_line)
            
            # 读取并转发 headers
            while True:
                line = f_remote.readline()
                if line in (b'\r\n', b'\n', b''):
                    self.wfile.write(b'\r\n')
                    break
                self.wfile.write(line)
            
            # 转发 body
            while True:
                data = f_remote.read(4096)
                if not data:
                    break
                self.wfile.write(data)
                
            f_remote.close()
            s_remote.close()

        except Exception as e:
            self.send_error(502, f"Bad Gateway: {e}")

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

if __name__ == "__main__":
    print(f"Starting HTTP/HTTPS Proxy on port {PORT}...")
    print(f"Auth: {USERNAME} / {PASSWORD}")
    server = ThreadedHTTPServer(("", PORT), ProxyHTTPRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping proxy...")
        server.server_close()
