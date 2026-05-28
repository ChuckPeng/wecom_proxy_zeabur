import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

TARGET_HOST = "https://qyapi.weixin.qq.com"

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def handle_request(self):
        allowed_paths = ['/cgi-bin/gettoken', '/cgi-bin/message/send', '/cgi-bin/menu/create']
        path_without_query = self.path.split('?')[0]
        
        if path_without_query not in allowed_paths:
            self.send_response(403)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Forbidden: Path not allowed")
            return

        target_url = TARGET_HOST + self.path

        req_headers = {'User-Agent': 'Mozilla/5.0'}
        if self.headers.get('Content-Type'):
            req_headers['Content-Type'] = self.headers.get('Content-Type')

        body = None
        if self.command == 'POST':
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length)

        req = urllib.request.Request(target_url, data=body, headers=req_headers, method=self.command)
        
        try:
            with urllib.request.urlopen(req) as response:
                resp_body = response.read()
                self.send_response(response.status)
                self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json'))
                self.send_header('Content-Length', str(len(resp_body)))
                self.end_headers()
                self.wfile.write(resp_body)
        except urllib.error.HTTPError as e:
            resp_body = e.read()
            self.send_response(e.code)
            self.send_header('Content-Type', e.headers.get('Content-Type', 'application/json'))
            self.send_header('Content-Length', str(len(resp_body)))
            self.end_headers()
            self.wfile.write(resp_body)
        except Exception as e:
            msg = str(e).encode('utf-8')
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)

if __name__ == '__main__':
    # 核心：Zeabur 会通过 PORT 环境变量动态分配端口
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), ProxyHandler)
    print(f"Proxy server running on port {port}")
    server.serve_forever()
