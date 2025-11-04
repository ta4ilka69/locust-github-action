from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import time


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/status/'):
            try:
                code = int(self.path.split('/')[2])
            except Exception:
                code = 200
            self.send_response(code)
            self.end_headers()
            return
        if self.path.startswith('/delay/'):
            try:
                sec = float(self.path.split('/')[2])
            except Exception:
                sec = 0.0
            time.sleep(sec)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

    def log_message(self, fmt, *args):
        pass


def main() -> None:
    port = int(os.environ.get('PORT', '8000'))
    HTTPServer(('127.0.0.1', port), Handler).serve_forever()


if __name__ == '__main__':
    main()
