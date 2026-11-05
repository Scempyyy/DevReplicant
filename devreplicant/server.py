"""DevReplicant Web Console HTTP Server."""

import http.server
import json
import os
import socketserver
import urllib.parse
from devreplicant.collector import create_snapshot, generate_restore_script, generate_dockerfile


WEB_DIR = os.path.join(os.path.dirname(__file__), "web")


class DevReplicantHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/snapshot":
            snapshot = create_snapshot()
            restore_script = generate_restore_script(snapshot)
            dockerfile = generate_dockerfile(snapshot)

            res = {
                "snapshot": snapshot,
                "restore_script": restore_script,
                "dockerfile": dockerfile,
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        elif parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"service": "DevReplicant", "status": "active"}).encode("utf-8"))
            return

        super().do_GET()


def start_replicant_server(host: str = "127.0.0.1", port: int = 8960):
    class ReuseAddressServer(socketserver.TCPServer):
        allow_reuse_address = True

    with ReuseAddressServer((host, port), DevReplicantHTTPHandler) as httpd:
        print(f"\n⚡ DevReplicant Studio live at http://{host}:{port}")
        print("Press Ctrl+C to terminate.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStudio terminated cleanly.")
