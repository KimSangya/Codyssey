#!/usr/bin/env python3
"""
조금 더 나은 웹서버 (Python 3.x, stdlib only)

요구사항:
- http.server 기반, 포트 8080
- index.html 파일(별도 작성)을 읽어 전송
- 매 접속 시 서버 콘솔에 접속 시간/클라이언트 IP 출력
- 성공 시 200 OK 헤더 전송
- (보너스) /whoami: 접속자 IP와 대략적 위치 조회(JSON, 실패 시 geo=None)
"""

from __future__ import annotations

import json
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

HOST = ''
PORT = 8080
INDEX_FILE = 'index.html'

_request_count = 0
_counter_lock = threading.Lock()


def log_access(client_ip: str, path: str) -> None:
    """접속 시간/클라이언트 IP/누적 요청 수를 콘솔에 출력한다."""
    global _request_count
    with _counter_lock:
        _request_count += 1
        count = _request_count
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[ACCESS] time={now} ip={client_ip} path="{path}" count={count}')


def is_private_ip(ip: str) -> bool:
    """사설/루프백 대역 여부."""
    return ip.startswith((
        '10.', '192.168.', '172.16.', '172.17.', '172.18.', '172.19.',
        '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.',
        '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.',
        '127.', '::1'
    ))


def lookup_geo(ip: str, timeout: float = 2.5) -> Optional[Dict[str, str]]:
    """
    (보너스) ip-api.com 으로 대략적 위치를 조회한다(표준 urllib 사용).
    실패/사설망이면 None.
    """
    if is_private_ip(ip):
        return None
    url = f'http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,query'
    try:
        req = Request(url, headers={'User-Agent': 'std-http-server/1.0'})
        with urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode('utf-8', errors='replace'))
    except (URLError, HTTPError, TimeoutError, ValueError):
        return None
    if data.get('status') != 'success':
        return None
    return {
        'ip': data.get('query', ''),
        'country': data.get('country', ''),
        'region': data.get('regionName', ''),
        'city': data.get('city', '')
    }


class SpaceHandler(BaseHTTPRequestHandler):
    server_version = 'SpaceHTTP/0.2'

    def do_GET(self) -> None:  # noqa: N802
        client_ip = self.client_address[0]
        path = self.path or '/'
        log_access(client_ip, path)

        if path == '/' or path == '/index.html':
            self._serve_index()
            return
        if path == '/whoami':
            self._serve_whoami(client_ip)
            return
        self._send_not_found()

    def _serve_index(self) -> None:
        """index.html을 읽어 전송(성공 시 200 OK)."""
        try:
            with open(INDEX_FILE, 'rb') as f:
                body = f.read()
        except FileNotFoundError:
            self._send_error_page(
                500,
                'index.html 파일이 서버 디렉터리에 없습니다. index.html을 작성해 주세요.'
            )
            return

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_whoami(self, client_ip: str) -> None:
        """보너스: 접속자 IP와 위치 정보를 JSON으로 반환."""
        geo = lookup_geo(client_ip)
        payload = {
            'ip': client_ip,
            'geo': geo if geo is not None else None,
            'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_not_found(self) -> None:
        body = (
            '<!doctype html><meta charset="utf-8">'
            '<title>404</title><h1>404 Not Found</h1>'
        ).encode('utf-8')
        self.send_response(404)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error_page(self, code: int, message: str) -> None:
        body = (
            f'<!doctype html><meta charset="utf-8"><title>{code}</title>'
            f'<h1>{code} Error</h1><p>{message}</p>'
        ).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # 기본 로그 억제(우리의 log_access가 요구 로그를 충족)
    def log_message(self, format: str, *args) -> None:  # noqa: A003
        pass


def run() -> None:
    httpd = ThreadingHTTPServer((HOST, PORT), SpaceHandler)
    print(f'Serving on http://127.0.0.1:{PORT} (Ctrl+C to quit)')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down...')
    finally:
        httpd.server_close()


if __name__ == '__main__':
    run()
