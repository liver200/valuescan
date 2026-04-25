#!/usr/bin/env python3
import http.server
import json
import os
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get("PORT", 8765))

# Keys from environment variables (set in Railway dashboard)
def get_keys():
    return {
        "anthropic":    os.environ.get("ANTHROPIC_API_KEY", ""),
        "alphavantage": os.environ.get("ALPHAVANTAGE_API_KEY", ""),
    }

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"  {args[0]} {args[1]}")

    def send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            html_path = os.path.join(os.path.dirname(__file__), "valuescan_v2.html")
            with open(html_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_cors()
            self.end_headers()
            self.wfile.write(content)
            return

        if self.path == "/api/keys-status":
            keys = get_keys()
            self._json(200, {
                "anthropic":    bool(keys["anthropic"]),
                "alphavantage": bool(keys["alphavantage"]),
                "mode": "cloud"
            })
            return

        self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)

        # Proxy → Anthropic
        if self.path == "/api/anthropic":
            ak = get_keys()["anthropic"]
            if not ak:
                self._json(401, {"error": "ANTHROPIC_API_KEY no configurada en Railway"}); return
            try:
                req = urllib.request.Request(
                    "https://api.anthropic.com/v1/messages",
                    data=body,
                    headers={
                        "Content-Type":      "application/json",
                        "x-api-key":         ak,
                        "anthropic-version": "2023-06-01"
                    },
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=60) as resp:
                    result = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.end_headers()
                self.wfile.write(result)
            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.end_headers()
                self.wfile.write(e.read())
            except Exception as e:
                self._json(500, {"error": str(e)})
            return

        # Proxy → Alpha Vantage
        if self.path == "/api/av":
            av = get_keys()["alphavantage"]
            if not av:
                self._json(401, {"error": "ALPHAVANTAGE_API_KEY no configurada en Railway"}); return
            try:
                data   = json.loads(body)
                params = "&".join(f"{k}={v}" for k, v in data.items())
                url    = f"https://www.alphavantage.co/query?{params}&apikey={av}"
                req    = urllib.request.Request(url, headers={"User-Agent": "ValueScan/2.0"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    result = resp.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.end_headers()
                self.wfile.write(result)
            except Exception as e:
                self._json(500, {"error": str(e)})
            return

        # save-keys no aplica en cloud — las keys vienen de env vars
        if self.path == "/api/save-keys":
            self._json(200, {"ok": True, "msg": "En modo cloud las keys se configuran en Railway. Ver instrucciones."})
            return

        self.send_error(404)

    def _json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_cors()
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print(f"\n  ValueScan corriendo en puerto {PORT}")
    keys = get_keys()
    print(f"  Anthropic key:    {'✓ OK' if keys['anthropic']    else '✗ Falta ANTHROPIC_API_KEY'}")
    print(f"  Alpha Vantage key: {'✓ OK' if keys['alphavantage'] else '✗ Falta ALPHAVANTAGE_API_KEY'}\n")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
