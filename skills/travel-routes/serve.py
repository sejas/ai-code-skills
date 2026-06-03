#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Local HTTP server for the travel-routes viewer.

Browsers block fetch() from file:// URLs. This script serves the output dir over
HTTP on 127.0.0.1, picks the first free port from 8765 upward, and opens the
viewer in the default browser.
"""

from __future__ import annotations

import http.server
import json
import os
import socket
import socketserver
import sys
import webbrowser
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent


def load_output_dir() -> Path:
    cfg = json.loads((SKILL_DIR / "config.json").read_text(encoding="utf-8"))
    return Path(os.path.expanduser(cfg["output_dir"]))


def free_port(start: int = 8765, span: int = 50) -> int:
    for p in range(start, start + span):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError(f"no free port in {start}–{start + span - 1}")


def main() -> int:
    root = load_output_dir()
    if not root.is_dir():
        print(f"Output dir not found: {root}. Run /travel-routes first.")
        return 1
    os.chdir(root)
    port = free_port()
    url = f"http://127.0.0.1:{port}/viewer.html"
    print(f"Serving {root}")
    print(f"  → {url}")
    print("  (Ctrl-C to stop)")
    webbrowser.open(url)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
