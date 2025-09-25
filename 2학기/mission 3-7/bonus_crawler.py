#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bonus_crawler.py
- 암호화폐: Binance 현재가
- 국내주식: 네이버 증권 현재가 (여러 셀렉터 폴백)
- Python 3.7~3.9 호환 (Optional/Dict/List 사용)
"""
import sys
from typing import Optional, Dict, List
import requests
from bs4 import BeautifulSoup

BINANCE_TICKER_URL = 'https://api.binance.com/api/v3/ticker/price'
NAVER_STOCK_URL = 'https://finance.naver.com/item/sise.nhn?code={code}'   # 구주소도 아직 동작
# 대안: 'https://finance.naver.com/item/sise.naver?code={code}'

def fetch_json(url: str, params: Optional[Dict[str, str]] = None,
               timeout: float = 10.0) -> Dict:
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, params=params, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

def get_crypto_price(symbol: str = 'BTCUSDT') -> str:
    data = fetch_json(BINANCE_TICKER_URL, params={'symbol': symbol})
    price = data.get('price')
    return '{} 현재가: {}'.format(symbol, price) if price else '{} 가격 정보를 찾을 수 없습니다.'.format(symbol)

def _extract_naver_now_price(soup: BeautifulSoup) -> Optional[str]:
    """
    네이버 증권 HTML에서 현재가 텍스트만 뽑는다.
    다양한 페이지 변형을 대비해 여러 셀렉터를 순차 시도한다.
    """
    selectors = [
        '#_nowVal',                 # 예전 구조
        '#now_value',               # 변형
        '.no_today .blind',         # 현재가가 .blind 안에 들어가는 최신 구조
        '.today .no_today .blind',  # 섹션 래퍼 포함
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    # 추가 폴백: 숫자만 있는 큰 값 찾기
    cand = soup.select_one('.no_today') or soup.select_one('.today')
    if cand:
        txt = cand.get_text(' ', strip=True)
        if txt:
            return txt.split()[0]
    return None

def get_korean_stock_price(code: str = '005930') -> str:
    url = NAVER_STOCK_URL.format(code=code)
    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    # 네이버 금융은 euc-kr 인코딩을 쓰는 경우가 많음
    resp.encoding = resp.apparent_encoding or 'euc-kr'
    soup = BeautifulSoup(resp.text, 'html.parser')

    price = _extract_naver_now_price(soup)
    if price:
        return '종목 {} 현재가: {}원'.format(code, price)
    return '종목 {} 가격 정보를 찾을 수 없습니다.'.format(code)

def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print('사용법:')
        print('  python bonus_crawler.py price [SYMBOL]')
        print('  python bonus_crawler.py stock [CODE]')
        return 0

    cmd = argv[1].lower()
    try:
        if cmd == 'price':
            symbol = argv[2].upper() if len(argv) >= 3 else 'BTCUSDT'
            print(get_crypto_price(symbol)); return 0
        if cmd == 'stock':
            code = argv[2] if len(argv) >= 3 else '005930'
            print(get_korean_stock_price(code)); return 0
    except requests.RequestException as exc:
        print('네트워크 오류: {}'.format(exc)); return 1

    print('알 수 없는 명령입니다. price 또는 stock 을 사용하세요.')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
