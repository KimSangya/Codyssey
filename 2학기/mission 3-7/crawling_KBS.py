#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crawling_KBS_json_api.py
------------------------
KBS 메인 JSON API에서 헤드라인 뉴스 가져오기
"""

import sys
import requests


URL = 'https://news.kbs.co.kr/expose/localNewsListForMain.json'


def fetch_json(url: str, timeout: float = 10.0) -> dict:
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0 Safari/537.36'
        )
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def parse_headlines(data: dict, limit: int = 10) -> list[str]:
    headlines = []
    # JSON 안에 localHeadlineNews_10, 20, … 이런 구조가 있음
    for key, value in data.get('data', {}).items():
        if key.startswith('localHeadlineNews'):
            if isinstance(value, dict) and 'manualList' in value:
                for item in value['manualList']:
                    title = item.get('title')
                    if title:
                        headlines.append(title.strip())

    # 중복 제거
    seen, result = set(), []
    for h in headlines:
        if h not in seen:
            seen.add(h)
            result.append(h)

    if limit is not None:
        result = result[:max(limit, 0)]
    return result


def print_headlines(headlines: list[str]) -> None:
    if not headlines:
        print('가져온 헤드라인이 없습니다.')
        return
    for i, title in enumerate(headlines, start=1):
        print(f'{i:02d}. {title}')


def main(argv: list[str]) -> int:
    limit = 10
    if len(argv) > 1:
        try:
            n = int(argv[1])
            limit = None if n == 0 else max(n, 0)
        except ValueError:
            pass

    try:
        data = fetch_json(URL)
        headlines = parse_headlines(data, limit)
    except requests.RequestException as exc:
        print(f'네트워크 오류: {exc}')
        return 1

    print_headlines(headlines)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
