# -*- coding: utf-8 -*-
"""
Open trace in browser.
"""

import http.server
import os
import socketserver
import webbrowser
import click

# HTTP Server used to open the trace in the browser.
class HttpHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler for opening trace in browser."""

    def end_headers(self):
        """End headers."""
        self.send_header("Access-Control-Allow-Origin", self.server.allow_origin)
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_GET(self):
        """Handle GET request."""
        if self.path != "/" + self.server.expected_fname:
            self.send_error(404, "File not found")
            return

        self.server.fname_get_completed = True
        super().do_GET()

    def do_POST(self):
        """Handle POST request."""
        self.send_error(404, "File not found")


def open_trace_in_browser(
    path: str,
    open_browser: bool = True,
    origin: str = "https://ui.perfetto.dev",
):
    """
    在浏览器中打开 trace 文件，自动启动本地 HTTP 服务并跳转到 Perfetto UI。

    Args:
        path (str): 本地 trace 文件路径。
        open_browser (bool): 是否自动打开浏览器，默认 True。
        origin (str): 允许的跨域来源，默认 https://ui.perfetto.dev。
    """
    # We reuse the HTTP+RPC port because it's the only one allowed by the CSP.
    if path is None or not os.path.exists(path):
        print(f"Trace file not found: {path}")
        return
    PORT = 9001
    path = os.path.abspath(path)
    os.chdir(os.path.dirname(path))
    fname = os.path.basename(path)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), HttpHandler) as httpd:
        url = f"http://127.0.0.1:{PORT}"
        path = f"/{fname}&referrer=record_android_trace"
        address = f"{origin}/#!/?url={url}{path}"
        if open_browser:
            webbrowser.open_new_tab(address)
        else:
            print(f"Open URL in browser: {address}")

        httpd.expected_fname = fname
        httpd.fname_get_completed = None
        httpd.allow_origin = origin
        while httpd.fname_get_completed is None:
            httpd.handle_request()

@click.command()
@click.argument("path", type=click.Path(exists=True))
def opentrace(path: str):
    """
    命令行入口：在浏览器中打开指定 trace 文件。

    Args:
        path (str): 本地 trace 文件路径。
    """
    open_trace_in_browser(path)

if __name__ == "__main__":
    opentrace()