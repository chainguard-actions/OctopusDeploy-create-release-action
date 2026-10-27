#!/usr/bin/env python3
"""Minimal recording stand-in for an Octopus Deploy server.

Every request (method, path, headers, body) is appended to the log file given
as argv[2]. Every request is answered with HTTP 500 and an Octopus-style error
body, so the action under test always fails after contacting the server. Tests
use the log to tell whether the action got past input validation.
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 18080
LOG = sys.argv[2] if len(sys.argv) > 2 else "/tmp/octopus-requests.log"


class Handler(BaseHTTPRequestHandler):
    def _handle(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode("utf-8", "replace") if length else ""
        with open(LOG, "a") as f:
            f.write("REQUEST %s %s\n" % (self.command, self.path))
            for k, v in self.headers.items():
                f.write("HEADER %s: %s\n" % (k, v))
            if body:
                f.write("BODY %s\n" % body)
            f.write("----\n")
        payload = json.dumps(
            {"ErrorMessage": "mock octopus server", "Errors": ["mock"]}
        ).encode()
        self.send_response(500)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    do_GET = _handle
    do_POST = _handle
    do_PUT = _handle
    do_DELETE = _handle

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
