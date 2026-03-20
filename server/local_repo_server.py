import http.server
import os
import socketserver
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORT = int(os.environ.get("CYBERGAME_PORT", "8000"))


def main() -> None:
    os.chdir(str(ROOT))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("0.0.0.0", PORT), handler) as httpd:
        print(f"[server] serving {ROOT} on port {PORT}")
        print(f"[server] download page: http://localhost:{PORT}/")
        print(f"[server] wheelhouse url: http://localhost:{PORT}/wheelhouse/")
        httpd.serve_forever()


if __name__ == "__main__":
    main()

