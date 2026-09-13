
from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from api_router import AIRouter
from config_manager import load_config

ROUTER = AIRouter()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        status, payload = ROUTER.handle(self.path)
        body = ROUTER.encode(payload)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print("GTS-AI1-API | " + fmt % args)

def main() -> None:
    cfg = load_config()
    server = ThreadingHTTPServer((cfg.host, cfg.port), Handler)
    print("GTS AI-1 API: http://%s:%s" % (cfg.host, cfg.port))
    server.serve_forever()

if __name__ == "__main__":
    main()
