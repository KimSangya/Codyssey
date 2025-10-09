#!/usr/bin/env python3                   # 유닉스/리눅스 환경에서 python3 인터프리터로 실행되도록 지정
# -*- coding: utf-8 -*-                  # 소스 파일의 인코딩을 UTF-8로 명시
"""
bonus_crawler.py
- 암호화폐: Binance 현재가
- 국내주식: 네이버 증권 현재가 (여러 셀렉터 폴백)
- Python 3.7~3.9 호환 (Optional/Dict/List 사용)
"""                                      # 파일에 대한 설명 (도큐스트링)

import sys                               # sys.argv와 sys.exit를 사용하기 위해 import
from typing import Optional, Dict, List  # 타입 힌트를 위해 Optional, Dict, List 가져옴
import requests                          # HTTP 요청을 보내기 위한 외부 라이브러리
from bs4 import BeautifulSoup            # HTML 파싱을 위한 BeautifulSoup

BINANCE_TICKER_URL = 'https://api.binance.com/api/v3/ticker/price'   # 바이낸스 시세 조회 API URL
NAVER_STOCK_URL = 'https://finance.naver.com/item/sise.nhn?code={code}'   # 네이버 주식 종목 페이지 URL (코드 자리 {code})

# JSON 데이터를 가져오는 함수
def fetch_json(url: str, params: Optional[Dict[str, str]] = None,
               timeout: float = 10.0) -> Dict:
    headers = {'User-Agent': 'Mozilla/5.0'}                          # 브라우저 흉내내기 위한 User-Agent
    resp = requests.get(url, params=params, headers=headers, timeout=timeout)  # HTTP GET 요청
    resp.raise_for_status()                                          # 상태 코드가 4xx, 5xx면 예외 발생
    return resp.json()                                               # 응답을 JSON으로 파싱해서 반환

# 암호화폐 현재가 가져오기
def get_crypto_price(symbol: str = 'BTCUSDT') -> str:
    data = fetch_json(BINANCE_TICKER_URL, params={'symbol': symbol}) # symbol 심볼에 대한 시세 요청
    price = data.get('price')                                        # price 키에서 값 꺼내기
    return '{} 현재가: {}'.format(symbol, price) if price else '{} 가격 정보를 찾을 수 없습니다.'.format(symbol)
                                                                     # 값이 있으면 출력 문자열, 없으면 에러 메시지

# 네이버 증권 HTML에서 현재가 텍스트 추출
def _extract_naver_now_price(soup: BeautifulSoup) -> Optional[str]:
    """
    네이버 증권 HTML에서 현재가 텍스트만 뽑는다.
    다양한 페이지 변형을 대비해 여러 셀렉터를 순차 시도한다.
    """
    selectors = [                                                    # 여러가지 후보 셀렉터 정의
        '#_nowVal',                 # 예전 구조
        '#now_value',               # 변형 구조
        '.no_today .blind',         # 최신 구조 (blind 클래스 안에 현재가 있음)
        '.today .no_today .blind',  # 래퍼 포함 구조
    ]
    for sel in selectors:                                           # 셀렉터를 순회하면서
        el = soup.select_one(sel)                                   # 첫 번째 매칭되는 요소 찾기
        if el and el.get_text(strip=True):                          # 요소가 존재하고 텍스트가 비어있지 않으면
            return el.get_text(strip=True)                          # 텍스트 반환
    # 폴백: 큰 숫자가 들어있는 div에서 첫 번째 값 가져오기
    cand = soup.select_one('.no_today') or soup.select_one('.today')# no_today나 today 클래스 블록 찾기
    if cand:
        txt = cand.get_text(' ', strip=True)                        # 내부 텍스트를 공백 기준으로 가져오기
        if txt:
            return txt.split()[0]                                   # 첫 번째 토큰(현재가) 반환
    return None                                                     # 아무것도 못 찾으면 None

# 국내 주식 현재가 가져오기
def get_korean_stock_price(code: str = '005930') -> str:
    url = NAVER_STOCK_URL.format(code=code)                         # 종목 코드 적용한 URL 생성
    headers = {'User-Agent': 'Mozilla/5.0'}                         # User-Agent 지정
    resp = requests.get(url, headers=headers, timeout=10)           # GET 요청
    resp.raise_for_status()                                         # 에러 코드 있으면 예외
    resp.encoding = resp.apparent_encoding or 'euc-kr'              # 응답 인코딩 설정 (네이버는 EUC-KR일 수 있음)
    soup = BeautifulSoup(resp.text, 'html.parser')                  # HTML 파싱

    price = _extract_naver_now_price(soup)                          # 현재가 추출 시도
    if price:
        return '종목 {} 현재가: {}원'.format(code, price)             # 성공 시 출력
    return '종목 {} 가격 정보를 찾을 수 없습니다.'.format(code)       # 실패 시 출력

# 메인 함수
def main(argv: List[str]) -> int:
    if len(argv) < 2:                                               # 인자가 부족하면 사용법 출력
        print('사용법:')
        print('  python bonus_crawler.py price [SYMBOL]')
        print('  python bonus_crawler.py stock [CODE]')
        return 0

    cmd = argv[1].lower()                                           # 두 번째 인자(명령) 소문자로 변환
    try:
        if cmd == 'price':                                          # price 명령이면
            symbol = argv[2].upper() if len(argv) >= 3 else 'BTCUSDT' # 세 번째 인자 있으면 심볼, 없으면 기본값
            print(get_crypto_price(symbol)); return 0               # 가격 조회 후 출력, 정상 종료
        if cmd == 'stock':                                          # stock 명령이면
            code = argv[2] if len(argv) >= 3 else '005930'          # 세 번째 인자 있으면 종목 코드, 없으면 기본 삼성전자
            print(get_korean_stock_price(code)); return 0           # 주가 조회 후 출력, 정상 종료
    except requests.RequestException as exc:                        # 네트워크 오류 처리
        print('네트워크 오류: {}'.format(exc)); return 1

    print('알 수 없는 명령입니다. price 또는 stock 을 사용하세요.')   # 잘못된 명령어일 때
    return 0

if __name__ == '__main__':                                         # 이 파일이 직접 실행될 때만
    sys.exit(main(sys.argv))                                       # main 함수 실행 후 종료 코드 반환


# python bonus_crawler.py price BTCUSDT
# python bonus_crawler.py stock 005930
# python bonus_crawler.py stock 035420