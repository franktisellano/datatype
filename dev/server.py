"""Dev server: HTTP + WebSocket + file watcher for live preview."""

import asyncio
import http.server
import json
import os
import subprocess
import sys
import threading
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

HTTP_PORT = 8080
WS_PORT = 8081

ws_clients = set()


class DevHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler serving preview page and font files."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PROJECT_ROOT, **kwargs)

    def end_headers(self):
        # Enable CORS and disable caching for fonts
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_GET(self):
        # Serve preview.html at root
        if self.path == "/" or self.path == "/index.html":
            self.path = "/dev/preview.html"
        super().do_GET()

    def log_message(self, format, *args):
        # Quiet logging
        pass


def run_http_server():
    """Start HTTP server in background thread."""
    server = http.server.HTTPServer(("", HTTP_PORT), DevHTTPHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


async def ws_handler(websocket):
    """Handle a WebSocket connection."""
    ws_clients.add(websocket)
    try:
        async for _ in websocket:
            pass  # We only push to clients, don't read
    finally:
        ws_clients.discard(websocket)


async def notify_reload():
    """Send reload message to all connected browsers."""
    if ws_clients:
        msg = json.dumps({"type": "reload", "time": time.time()})
        await asyncio.gather(
            *[client.send(msg) for client in ws_clients],
            return_exceptions=True
        )


def run_build(dev=False):
    """Run the font build script."""
    print("  Rebuilding fonts...")
    cmd = [sys.executable, os.path.join(PROJECT_ROOT, "sources", "build.py")]
    if dev:
        cmd.append("--dev")
    result = subprocess.run(
        cmd,
        capture_output=True, text=True, cwd=PROJECT_ROOT
    )
    if result.returncode != 0:
        print(f"  Build FAILED:\n{result.stderr}")
        return False
    else:
        # Print last few lines of output
        lines = result.stdout.strip().split("\n")
        for line in lines[-3:]:
            print(f"  {line}")
        return True


class FileWatcher:
    """Watch sources/ directory for changes using watchdog."""

    def __init__(self, loop, dev=False):
        self.loop = loop
        self.last_build = 0
        self.debounce = 0.5  # seconds
        self.dev = dev

    def start(self):
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        watcher = self

        class Handler(FileSystemEventHandler):
            def on_any_event(self, event):
                if event.is_directory:
                    return
                if not event.src_path.endswith(".py"):
                    return
                now = time.time()
                if now - watcher.last_build < watcher.debounce:
                    return
                watcher.last_build = now
                print(f"\n  File changed: {os.path.relpath(event.src_path, PROJECT_ROOT)}")
                if run_build(dev=watcher.dev):
                    asyncio.run_coroutine_threadsafe(notify_reload(), watcher.loop)

        observer = Observer()
        observer.schedule(Handler(), os.path.join(PROJECT_ROOT, "sources"), recursive=True)
        observer.start()
        return observer


async def main():
    import websockets

    # Initial build
    print("Datatype Dev Server")
    print("=" * 40)
    print("Running initial build...")
    run_build(dev=True)

    # Start HTTP server
    http_server = run_http_server()
    print(f"\n  HTTP:      http://localhost:{HTTP_PORT}")
    print(f"  WebSocket: ws://localhost:{WS_PORT}")
    print(f"\n  Watching sources/ for changes...")
    print(f"  Press Ctrl+C to stop\n")

    # Start file watcher
    loop = asyncio.get_event_loop()
    watcher = FileWatcher(loop, dev=True)
    observer = watcher.start()

    # Start WebSocket server
    async with websockets.serve(ws_handler, "localhost", WS_PORT):
        try:
            await asyncio.Future()  # run forever
        except asyncio.CancelledError:
            pass
        finally:
            observer.stop()
            http_server.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down.")
