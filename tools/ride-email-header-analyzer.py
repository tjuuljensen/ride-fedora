#!/usr/bin/env python3
"""Purpose:
  Launch the RIDE-managed local MailTower email header analyzer.

Behavior:
  Verify the owned static files, serve the single-page app on an ephemeral
  IPv4 loopback port, and open the user's default browser. Requests are served
  locally; request paths are not logged.

Compatibility:
  Python 3.9 or later on Fedora Workstation x86_64.

Usage:
  ride-email-header-analyzer

Inputs:
  The owned app at ~/.local/share/ride-fedora/apps/email-header-analyzer and
  its manifest at ~/.local/share/ride-fedora/owned-tools.

Side effects:
  Starts a foreground loopback HTTP server until interrupted and opens a local
  browser tab. It does not modify the app or browser profile.

Prerequisites:
  Python 3.9 or later and a desktop browser for interactive use.

Ownership and provenance:
  RIDE Fedora 3.0.0 launcher for the MIT-licensed MailTower source recorded in
  catalog/operations.json. The server binds only to 127.0.0.1.

Version:
  3.0.0

Changelog:
  3.0.0: Add loopback-only launcher for the local email header analyzer.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import http.server
import json
import os
from pathlib import Path
import sys
import webbrowser


OPERATION_ID = "package.email-header-analyzer"
APP_RELATIVE = Path(".local/share/ride-fedora/apps/email-header-analyzer")
MANIFEST_RELATIVE = Path(".local/share/ride-fedora/owned-tools/package.email-header-analyzer.json")


def tree_sha256(root: Path) -> str:
    """Hash relative names and bytes, refusing symlinks and special files."""
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("app destination is not a directory")
    digest = hashlib.sha256()
    for current, dirs, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        dirs.sort()
        files.sort()
        for name in list(dirs):
            path = current_path / name
            if path.is_symlink():
                raise ValueError("app contains a symbolic link")
            rel = path.relative_to(root).as_posix().encode()
            digest.update(b"D\0" + rel + b"\0")
        for name in files:
            path = current_path / name
            if path == root / ".ride-running.lock":
                continue
            if path.is_symlink() or not path.is_file():
                raise ValueError("app contains an unsupported file")
            rel = path.relative_to(root).as_posix().encode()
            digest.update(b"F\0" + rel + b"\0")
            with path.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
    return digest.hexdigest()


class LocalSpaHandler(http.server.SimpleHTTPRequestHandler):
    """Serve SPA routes and assets without logging request paths."""

    def __init__(self, *args, directory: str, **kwargs):
        self._root = Path(directory).resolve(strict=True)
        super().__init__(*args, directory=str(self._root), **kwargs)

    def send_head(self):
        requested = Path(self.translate_path(self.path))
        if not requested.is_file():
            self.path = "/index.html"
        return super().send_head()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; font-src 'self' data:; connect-src 'self'; "
            "object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'",
        )
        super().end_headers()

    def log_message(self, _format: str, *args) -> None:
        return


def serve() -> int:
    home_input = Path(os.environ.get("HOME", str(Path.home())))
    if home_input.is_symlink():
        raise ValueError("home path is a symbolic link")
    home = home_input.resolve(strict=True)
    app = home / APP_RELATIVE
    manifest_path = home / MANIFEST_RELATIVE
    owned_paths = (
        home / ".local",
        home / ".local/share",
        home / ".local/share/ride-fedora",
        home / ".local/share/ride-fedora/apps",
        app,
        home / ".local/share/ride-fedora/owned-tools",
        manifest_path,
    )
    if any(path.is_symlink() for path in owned_paths):
        raise ValueError("owned app path contains a symbolic link")
    lock_path = app / ".ride-running.lock"
    with lock_path.open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("id") != OPERATION_ID or manifest.get("destination") != str(app):
            raise ValueError("app ownership manifest does not match the expected destination")
        if tree_sha256(app) != manifest.get("contentSha256"):
            raise ValueError("owned app files changed; refusing to serve them")
        web_root = app / "dist" / "spa"
        if not (web_root / "index.html").is_file():
            raise ValueError("built app index is missing")
        server = http.server.ThreadingHTTPServer(
            ("127.0.0.1", 0),
            lambda *args, **kwargs: LocalSpaHandler(*args, directory=str(web_root), **kwargs),
        )
        host, port = server.server_address
        url = f"http://{host}:{port}/"
        print(f"Local analyzer: {url}", flush=True)
        if os.environ.get("RIDE_DISABLE_BROWSER") != "1":
            webbrowser.open(url, new=2)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch the local email header analyzer.")
    parser.add_argument("--tree-sha256", metavar="DIRECTORY", help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        if args.tree_sha256:
            print(tree_sha256(Path(args.tree_sha256)))
            return 0
        return serve()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"RIDE email header analyzer: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
