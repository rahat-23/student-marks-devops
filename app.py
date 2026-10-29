"""Tiny HTTP application. Uses only the Python standard library."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit


def classify_marks(marks: int) -> str:
    if not 0 <= marks <= 100:
        raise ValueError("Marks must be between 0 and 100")
    return "Pass" if marks >= 50 else "Fail"


def grade_result(raw_marks: str):
    """Return (status_code, JSON-serializable response)."""
    try:
        marks = int(raw_marks)
        result = classify_marks(marks)
    except (ValueError, TypeError):
        return 400, {"error": "marks must be a whole number from 0 to 100"}
    return 200, {"marks": marks, "result": result}


HOME = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Student Marks • DevOps Lab</title>
<style>body{font-family:system-ui,sans-serif;background:#f6f8fc;margin:0;padding:48px 16px;color:#192537}
main{max-width:530px;margin:0 auto;background:#fff;padding:28px;border-radius:14px;border:1px solid #d9e0eb}
label{display:block;margin:18px 0 6px}input,button{font-size:17px;padding:10px;border-radius:7px}
input{border:1px solid #9baac0;width:130px}button{background:#213c66;color:#fff;border:none;margin-left:8px}
p{line-height:1.6}code{background:#edf2f8;padding:2px 5px}</style></head>
<body><main><h1>Student Marks API</h1><p>A tiny Python app for learning Docker and CI/CD.</p>
<form action="/grade" method="get"><label for="marks">Enter marks (0–100):</label>
<input id="marks" name="marks" type="number" min="0" max="100" value="75" required>
<button type="submit">Check result</button></form>
<p>Health endpoint: <a href="/health"><code>/health</code></a></p>
<p>Try: <a href="/grade?marks=85"><code>/grade?marks=85</code></a></p>
</main></body></html>"""


class AppHandler(BaseHTTPRequestHandler):
    def respond(self, code, body, content_type="application/json; charset=utf-8"):
        data = (json.dumps(body) if isinstance(body, dict) else body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlsplit(self.path)
        if path.path == "/":
            self.respond(200, HOME, "text/html; charset=utf-8")
        elif path.path == "/health":
            self.respond(200, {"status": "ok"})
        elif path.path == "/grade":
            raw_marks = parse_qs(path.query).get("marks", [""])[0]
            code, body = grade_result(raw_marks)
            self.respond(code, body)
        else:
            self.respond(404, {"error": "route not found"})


if __name__ == "__main__":
    # Suitable for local learning; real deployments need production hardening.
    server = ThreadingHTTPServer(("0.0.0.0", 5000), AppHandler)
    print("Student Marks API listening on port 5000", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
