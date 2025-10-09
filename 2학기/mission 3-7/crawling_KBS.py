#!/usr/bin/env python3            # 유닉스/맥에서 이 파일을 파이썬3 인터프리터로 실행하도록 하는 shebang
# -*- coding: utf-8 -*-            # 소스 인코딩 표기(파이썬3 기본이 UTF-8이지만 명시적으로 적어 둠)
"""
crawling_KBS_json_api.py
------------------------
KBS 메인 JSON API에서 헤드라인 뉴스 가져오기
"""                                   # 모듈(파일) 수준 설명을 담는 도큐스트링

import sys                           # 종료 코드 반환을 위해 sys.exit 사용
import requests                      # HTTP 요청(REST/JSON) 전송을 위한 외부 패키지

URL = 'https://news.kbs.co.kr/expose/localNewsListForMain.json'  # 메인 페이지가 Ajax로 호출하는 JSON 엔드포인트

def fetch_json(url: str, timeout: float = 10.0) -> dict:         # url에서 JSON을 받아 dict로 반환하는 함수
    headers = {                                                   # 서버가 봇으로 차단하지 않도록 브라우저 유사 UA 헤더 지정
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0 Safari/537.36'
        )
    }
    resp = requests.get(url, headers=headers, timeout=timeout)    # GET 요청 전송(타임아웃 포함)
    resp.raise_for_status()                                       # HTTP 4xx/5xx 발생 시 예외를 던져 상위에서 처리
    return resp.json()                                            # 응답 본문을 JSON으로 파싱하여 dict로 반환

def parse_headlines(data: dict, limit: int = 10) -> list[str]:    # JSON(dict)에서 제목만 뽑아 리스트로 만드는 함수
    headlines = []                                                # 결과를 담을 리스트
    # JSON 안에 localHeadlineNews_10, 20, … 이런 구조가 있음
    for key, value in data.get('data', {}).items():               # 최상위 'data' 아래의 모든 키/값 순회
        if key.startswith('localHeadlineNews'):                   # 헤드라인 그룹들만 필터링
            if isinstance(value, dict) and 'manualList' in value: # 각 그룹 안의 수동 편집 목록 존재 확인
                for item in value['manualList']:                  # 수동 목록의 개별 기사 아이템 순회
                    title = item.get('title')                     # 기사 제목 필드 꺼내기
                    if title:                                     # None/빈 문자열이 아닌 경우만
                        headlines.append(title.strip())           # 앞뒤 공백 제거 후 결과에 추가

    # 중복 제거
    seen, result = set(), []                                      # 이미 본 제목을 기록할 set, 최종 결과 리스트
    for h in headlines:                                           # 수집된 제목들을 순회하면서
        if h not in seen:                                         # 아직 나오지 않은 제목이면
            seen.add(h)                                           # 집합에 등록하고
            result.append(h)                                      # 결과 리스트에 추가

    if limit is not None:                                         # 출력 개수 제한이 설정된 경우
        result = result[:max(limit, 0)]                           # 0보다 작은 수 방지 후 슬라이싱
    return result                                                 # 최종 제목 리스트 반환

def print_headlines(headlines: list[str]) -> None:                # 제목 리스트를 보기 좋게 출력하는 함수
    if not headlines:                                             # 비어 있으면 안내 문구 출력
        print('가져온 헤드라인이 없습니다.')
        return
    for i, title in enumerate(headlines, start=1):                # 1부터 번호 매기며 순회
        print(f'{i:02d}. {title}')                                # 2자리 번호 + 제목 출력(예: 01. 제목)

def main(argv: list[str]) -> int:                                 # 진입점 함수(반환값은 프로세스 종료 코드)
    limit = 10                                                    # 기본 출력 개수는 10개
    if len(argv) > 1:                                             # 명령행 인자가 있으면
        try:
            n = int(argv[1])                                      # 첫 번째 인자를 정수로 파싱
            limit = None if n == 0 else max(n, 0)                 # 0이면 전체, 양수면 그 개수, 음수 방지는 max
        except ValueError:                                        # 정수 변환 실패 시
            pass                                                  # 조용히 무시하고 기본값(10) 사용

    try:
        data = fetch_json(URL)                                    # JSON 엔드포인트 호출해 dict 획득
        headlines = parse_headlines(data, limit)                  # dict에서 제목 리스트 추출
    except requests.RequestException as exc:                      # 네트워크/HTTP 오류 처리
        print(f'네트워크 오류: {exc}')
        return 1                                                  # 비정상 종료 코드(1) 반환

    print_headlines(headlines)                                    # 제목 리스트를 출력
    return 0                                                      # 정상 종료 코드(0) 반환

if __name__ == '__main__':                                        # 이 파일이 스크립트로 직접 실행될 때만
    sys.exit(main(sys.argv))                                      # main() 실행 후 반환 코드를 OS에 전달
