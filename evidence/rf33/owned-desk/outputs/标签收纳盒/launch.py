"""Local-only launcher for the self-contained collection application."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import socket
import threading
import webbrowser

class LocalServer(ThreadingHTTPServer):
    allow_reuse_address = False

    def server_bind(self):
        # Windows otherwise permits multiple reusable servers on one address.
        if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()

def main():
    parser = argparse.ArgumentParser(description="标签收纳盒本地启动器")
    parser.add_argument('--no-browser', action='store_true', help='仅启动，不自动打开浏览器')
    options = parser.parse_args()
    folder = Path(__file__).resolve().parent
    address = 'http://127.0.0.1:8877/'
    handler = partial(SimpleHTTPRequestHandler, directory=str(folder))
    try:
        server = LocalServer(('127.0.0.1', 8877), handler)
    except OSError as error:
        print('无法启动标签收纳盒：本地地址可能已被占用。')
        print('请先关闭之前启动的窗口，再重试。错误详情：', error)
        return 1
    server.daemon_threads = True
    print('标签收纳盒已启动：' + address, flush=True)
    print('请保持此窗口打开。使用结束后，关闭此窗口或按 Ctrl+C 即可停止。', flush=True)
    print('数据保存在当前浏览器；关闭启动窗口不会清空数据。', flush=True)
    timer = None
    if not options.no_browser:
        timer = threading.Timer(0.4, lambda: webbrowser.open(address))
        timer.daemon = True
        timer.start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('标签收纳盒已停止。')
    finally:
        if timer:
            timer.cancel()
        server.server_close()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
