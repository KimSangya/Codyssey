#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
crawling_KBS.py

네이버에 접속하여 비로그인/로그인 상태의 콘텐츠 차이를 확인하고,
로그인 후에만 보이는 콘텐츠(예: 네이버 메일함 제목들)를 크롤링하여
리스트에 담아 출력하는 예제 스크립트.

요구사항 요약
- Python 3.x
- 표준 라이브러리 + 허용 라이브러리만 사용 (Selenium 허용 가정)
- PEP 8 스타일 준수
- 문자열은 기본적으로 단일 인용부호(') 사용
- 함수/변수는 스네이크 표기, 클래스는 CapWords
- 경고 메시지 없이 실행

준비물
- Chrome + ChromeDriver (PATH 등록)
- 환경변수 NAVER_ID, NAVER_PW 설정
"""

import os  # 환경변수(NAVER_ID, NAVER_PW) 읽기 위해 사용
import sys  # 표준 에러 출력 및 종료 코드 반환을 위해 사용
import time  # 명시적 대기(sleep) 사용
from typing import List, Optional, Tuple  # 타입 힌트(List, Optional, Tuple)

from selenium import webdriver  # Selenium WebDriver 사용
from selenium.webdriver.chrome.options import Options  # 크롬 옵션 설정용
from selenium.webdriver.chrome.service import Service  # ChromeDriver 서비스 핸들러
from selenium.webdriver.common.by import By  # 요소 선택 시 By 사용
from selenium.webdriver.remote.webdriver import WebDriver  # 드라이버 타입 힌트
from selenium.webdriver.support import expected_conditions as EC  # 명시적 대기 조건
from selenium.webdriver.support.ui import WebDriverWait  # 명시적 대기 구현

NAVER_HOME = 'https://www.naver.com/'  # 네이버 메인 URL
NAVER_LOGIN_PAGE = (  # 네이버 로그인 페이지 URL (로그인 후 리다이렉트 포함)
    'https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com/'
)  # 튜플 괄호는 줄바꿈을 위한 것
NAVER_MAIL = 'https://mail.naver.com/'  # 네이버 메일 URL

class LoginError(Exception):  # 로그인 관련 사용자 정의 예외
    """네이버 로그인 실패 시 사용되는 예외 클래스."""  # 예외 설명
    pass  # 추가 구현 없이 예외 타입만 정의

def build_driver(headless: bool = False) -> WebDriver:  # Chrome WebDriver 생성 함수
    """
    크롬 WebDriver를 생성한다.
    """  # 함수 설명 (docstring 유지)
    chrome_options = Options()  # 크롬 옵션 객체 생성
    if headless:  # 헤드리스 모드가 요청된 경우
        chrome_options.add_argument('--headless=new')  # 최신 헤드리스 모드 활성화
    chrome_options.add_argument('--window-size=1280,900')  # 창 크기 지정(안정적 렌더링)
    chrome_options.add_argument('--disable-gpu')  # GPU 가속 비활성화(호환성)
    chrome_options.add_argument('--no-sandbox')  # 샌드박스 비활성화(일부 환경 필요)
    chrome_options.add_argument('--lang=ko-KR')  # 브라우저 언어 한국어 설정
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 자동화 탐지 회피 플래그

    service = Service()  # PATH에 등록된 chromedriver 사용
    driver = webdriver.Chrome(service=service, options=chrome_options)  # 드라이버 인스턴스 생성
    driver.implicitly_wait(2)  # 암묵적 대기(요소 탐색 시 최대 2초 대기)
    return driver  # 생성한 드라이버 반환

def wait_for(  # 특정 요소가 나타날 때까지 명시적으로 대기하는 헬퍼
    driver: WebDriver,  # 사용 중인 WebDriver
    by: By,  # 선택 방식(By.CSS_SELECTOR 등)
    selector: str,  # 선택자 문자열
    timeout: int = 10  # 최대 대기 시간(초)
):  # 함수 헤더 종료
    """
    특정 요소가 나타날 때까지 대기한다.
    """  # 함수 설명
    return WebDriverWait(driver, timeout).until(  # timeout 내 조건을 만족하면 요소 반환
        EC.presence_of_element_located((by, selector))  # DOM에 요소가 존재할 때까지 대기
    )

def collect_public_content(driver: WebDriver) -> List[str]:  # 비로그인 상태 공개 콘텐츠 수집
    """
    비로그인 상태에서 네이버 메인에서 확인 가능한 공개 콘텐츠 일부를 수집한다.
    (예: 메인 뉴스·쇼핑/엔터테인먼트 블록 타이틀 텍스트 등)
    """  # 함수 설명
    driver.get(NAVER_HOME)  # 네이버 메인 페이지로 이동
    time.sleep(1)  # 초기 렌더링 안정화를 위해 짧게 대기

    texts: List[str] = []  # 수집한 텍스트를 담을 리스트

    candidates = [  # 섹션 제목 후보 셀렉터들
        (By.CSS_SELECTOR, 'h2.NM_THEME_META_title'),  # 테마 섹션 제목
        (By.CSS_SELECTOR, 'div.header_area h2'),  # 헤더 영역 h2
        (By.CSS_SELECTOR, 'h2#NM_THEME_META'),  # 특정 ID의 h2
    ]  # 후보 리스트 끝

    for by, sel in candidates:  # 각 후보 셀렉터 반복
        try:  # 셀렉터별 탐색 시도
            elems = driver.find_elements(by, sel)  # 복수 요소 찾기
            for e in elems:  # 찾은 요소들 순회
                t = e.text.strip()  # 텍스트 추출 후 공백 제거
                if t:  # 내용이 있는 경우만
                    texts.append(t)  # 리스트에 추가
        except Exception:  # 셀렉터 미적중/오류 시
            continue  # 다음 후보로 넘어감

    more_candidates = [  # 추가 섹션 후보(보다 포괄적)
        (By.CSS_SELECTOR, 'section h2'),  # 섹션 내부 h2들
        (By.CSS_SELECTOR, 'div.group_title'),  # 그룹 타이틀
        (By.CSS_SELECTOR, 'h3'),  # 보조 타이틀들
    ]  # 추가 후보 리스트 끝
    for by, sel in more_candidates:  # 추가 후보 순회
        try:  # 탐색 시도
            elems = driver.find_elements(by, sel)  # 요소 목록
            for e in elems[:5]:  # 최대 5개까지만 수집
                t = e.text.strip()  # 텍스트 추출
                if t and t not in texts:  # 비어있지 않고 중복 아니면
                    texts.append(t)  # 추가
        except Exception:  # 실패 시
            continue  # 무시하고 진행

    dedup = []  # 중복 제거를 위한 새 리스트
    for t in texts:  # 수집 텍스트 순회
        if t and t not in dedup:  # 비어있지 않고 아직 없으면
            dedup.append(t)  # 추가
    return dedup[:10]  # 상위 10개만 반환

def login_naver(driver: WebDriver, user_id: str, user_pw: str) -> None:  # 네이버 로그인 절차
    """
    네이버에 로그인한다.
    """  # 함수 설명
    driver.get(NAVER_LOGIN_PAGE)  # 로그인 페이지 이동
    wait_for(driver, By.TAG_NAME, 'body', timeout=10)  # body 로드까지 대기

    filled = False  # 입력 성공 여부 플래그
    selectors: List[Tuple[By, str]] = [  # 아이디 입력 필드 후보
        (By.ID, 'id'),
        (By.NAME, 'id'),
        (By.CSS_SELECTOR, 'input#id'),
        (By.CSS_SELECTOR, 'input[name="id"]'),
    ]  # 아이디 셀렉터 후보 끝
    pw_selectors: List[Tuple[By, str]] = [  # 비밀번호 입력 필드 후보
        (By.ID, 'pw'),
        (By.NAME, 'pw'),
        (By.CSS_SELECTOR, 'input#pw'),
        (By.CSS_SELECTOR, 'input[name="pw"]'),
    ]  # 비밀번호 셀렉터 후보 끝

    for by1, sel1 in selectors:  # 아이디 셀렉터 순회
        for by2, sel2 in pw_selectors:  # 비밀번호 셀렉터 순회
            try:  # 각 조합으로 입력 시도
                id_box = wait_for(driver, by1, sel1, timeout=6)  # 아이디 입력 요소 대기/획득
                pw_box = wait_for(driver, by2, sel2, timeout=6)  # 비밀번호 입력 요소 대기/획득
                id_box.clear()  # 기존 입력 값 제거
                id_box.send_keys(user_id)  # 아이디 입력
                pw_box.clear()  # 기존 입력 값 제거
                pw_box.send_keys(user_pw)  # 비밀번호 입력
                filled = True  # 입력 성공
                break  # 비밀번호 루프 종료
            except Exception:  # 실패하면
                continue  # 다음 조합 시도
        if filled:  # 입력 성공했으면
            break  # 아이디 루프 종료

    if not filled:  # 모든 셀렉터가 실패한 경우
        try:  # JS로 값 주입
            driver.execute_script(  # 아이디 필드에 값 설정
                'document.querySelector("#id").value = arguments[0];', user_id
            )  # execute_script 종료
            driver.execute_script(  # 비밀번호 필드에 값 설정
                'document.querySelector("#pw").value = arguments[0];', user_pw
            )  # execute_script 종료
            filled = True  # 입력 성공으로 간주
        except Exception as exc:  # JS 주입마저 실패
            raise LoginError('로그인 필드를 찾을 수 없습니다.') from exc  # 사용자 정의 예외 발생

    clicked = False  # 로그인 버튼 클릭 성공 여부
    login_btn_candidates: List[Tuple[By, str]] = [  # 로그인 버튼 후보 셀렉터
        (By.ID, 'log.login'),
        (By.CSS_SELECTOR, 'button.btn_login'),
        (By.CSS_SELECTOR, 'input.btn_login'),
        (By.CSS_SELECTOR, 'button[type="submit"]'),
        (By.XPATH, '//button[contains(@class,"btn_login")]'),
    ]  # 버튼 후보 끝
    for by, sel in login_btn_candidates:  # 후보들 순회
        try:  # 클릭 시도
            btn = driver.find_element(by, sel)  # 버튼 요소 찾기
            btn.click()  # 클릭
            clicked = True  # 성공 표시
            break  # 루프 탈출
        except Exception:  # 실패 시
            continue  # 다음 후보 시도

    if not clicked:  # 버튼 클릭이 모두 실패한 경우
        try:  # 폼 직접 submit 시도
            driver.execute_script(
                'document.querySelector("form").submit();'
            )  # 첫 번째 form 제출
            clicked = True  # 제출 성공으로 간주
        except Exception as exc:  # 실패 시
            raise LoginError('로그인 버튼 클릭 실패') from exc  # 예외 발생

    time.sleep(2)  # 서버 처리/리다이렉트 대기

    try:  # 로그인 성공 여부 확인
        driver.get(NAVER_HOME)  # 메인으로 이동
        time.sleep(1)  # 초기 렌더링 대기
        any_logged_marker = False  # 로그인 지표 발견 여부
        probes: List[Tuple[By, str]] = [  # 로그인 상태를 암시하는 요소 후보
            (By.CSS_SELECTOR, 'a#NM_mail_icon'),  # 메일 아이콘
            (By.CSS_SELECTOR, 'a#NM_ly_la'),  # 알림/레이어 라우처
            (By.CSS_SELECTOR, 'a#NM_MY'),  # MY 네이버
            (By.CSS_SELECTOR, 'a[href*="mail.naver.com"]'),  # 메일 링크
        ]  # 지표 후보 끝
        for by, sel in probes:  # 각 지표 탐색
            elems = driver.find_elements(by, sel)  # 요소 목록
            if elems:  # 하나라도 있으면
                any_logged_marker = True  # 로그인 상태로 간주
                break  # 루프 종료
        if not any_logged_marker:  # 지표가 전혀 없으면
            raise LoginError('로그인 표시 요소를 찾지 못했습니다.')  # 실패 처리
    except Exception as exc:  # 예외 발생 시
        raise LoginError('로그인 확인 실패') from exc  # 래핑하여 보고

def collect_mail_subjects(driver: WebDriver, limit: int = 20) -> List[str]:  # 로그인 후 메일 제목 수집
    """
    로그인된 세션으로 네이버 메일함 제목을 수집한다.
    """  # 함수 설명
    driver.get(NAVER_MAIL)  # 메일 서비스로 이동
    wait_for(driver, By.TAG_NAME, 'body', timeout=15)  # 페이지 로드 대기
    time.sleep(2)  # 동적 렌더링/리스트 로딩 대기

    subjects: List[str] = []  # 결과 제목 리스트
    sel_candidates: List[Tuple[By, str]] = [  # 제목 후보 셀렉터 모음(다양한 UI 대응)
        (By.CSS_SELECTOR, 'a.mail_title, a.subject_title, a.subject'),  # 일반적인 제목 링크들
        (By.CSS_SELECTOR, '[role="grid"] a'),  # 접근성 grid 내부 링크
        (By.CSS_SELECTOR, 'div.mailList a'),  # 구형 UI 리스트
        (By.CSS_SELECTOR, 'a[href*="read"]'),  # 읽기 링크 포함 앵커
    ]  # 후보 끝

    for by, sel in sel_candidates:  # 각 후보 순회
        elems = driver.find_elements(by, sel)  # 요소들 수집
        for e in elems:  # 요소 순회
            t = (e.text or '').strip()  # 텍스트 안전 추출 및 트림
            if t and t not in subjects:  # 비어있지 않고 중복 아니면
                subjects.append(t)  # 추가
        if subjects:  # 하나라도 수집되면
            break  # 다음 후보 탐색 중단

    cleaned = []  # 후처리된 제목 리스트
    for t in subjects:  # 원본 제목 순회
        if len(t) >= 2 and '삭제' not in t and '중요' not in t:  # 불필요 텍스트 필터
            cleaned.append(t)  # 정제된 제목 추가

    return cleaned[:limit]  # 요청 개수(limit)만큼 반환

def main() -> None:  # 스크립트 엔트리 포인트
    """
    스크립트 엔트리 포인트.
    - 비로그인 상태 공개 콘텐츠 수집
    - 로그인
    - 로그인 전용 콘텐츠(메일 제목) 수집
    - 결과 출력
    """  # 함수 설명
    user_id = os.environ.get('NAVER_ID', '')  # 환경변수에서 아이디 읽기(없으면 빈 문자열)
    user_pw = os.environ.get('NAVER_PW', '')  # 환경변수에서 비밀번호 읽기(없으면 빈 문자열)

    if not user_id or not user_pw:  # 필수 환경변수 누락 검사
        print(  # 오류 메시지 출력
            '[오류] 환경변수 NAVER_ID / NAVER_PW 를 설정해 주세요.',
            file=sys.stderr  # 표준 에러로 출력
        )  # print 종료
        sys.exit(1)  # 종료 코드 1로 비정상 종료

    driver: Optional[WebDriver] = None  # 드라이버 참조 초기화
    try:  # 정상 실행 블록
        driver = build_driver(headless=False)  # 드라이버 생성(헤드리스 비권장)

        print('[1] 비로그인 상태 공개 콘텐츠 수집 중...')  # 진행 안내
        public_texts = collect_public_content(driver)  # 공개 콘텐츠 수집 호출
        print(f'  - 공개 콘텐츠 예시 ({len(public_texts)}개):')  # 건수 출력
        for i, t in enumerate(public_texts, start=1):  # 번호 붙여 출력
            print(f'    {i:>2}. {t}')  # 정렬 출력

        print('\n[2] 네이버 로그인 시도...')  # 로그인 단계 안내
        login_naver(driver, user_id, user_pw)  # 로그인 수행
        print('  - 로그인 성공')  # 성공 메시지

        print('\n[3] 로그인 후 콘텐츠(메일 제목) 수집 중...')  # 수집 단계 안내
        mail_subjects = collect_mail_subjects(driver, limit=30)  # 메일 제목 최대 30개 수집

        aggregated: List[Tuple[str, str]] = []  # 카테고리 태깅된 결과 리스트
        for t in public_texts:  # 공개 텍스트 합치기
            aggregated.append(('public', t))  # ('public', 텍스트) 형태로 추가
        for t in mail_subjects:  # 메일 제목 합치기
            aggregated.append(('mail', t))  # ('mail', 제목) 형태로 추가

        print('\n[결과] 수집 텍스트 목록:')  # 결과 헤더 출력
        for i, (cat, text) in enumerate(aggregated, start=1):  # 결과 나열
            print(f'  {i:>2}. [{cat}] {text}')  # 카테고리와 함께 출력

        if not mail_subjects:  # 메일 제목을 하나도 못 찾은 경우
            print(  # 안내 메시지 출력
                '\n[안내] 메일 제목이 보이지 않는 경우:\n'
                ' - 보안/캡차가 뜬 경우 수동 인증 후 다시 실행\n'
                ' - 크롬/드라이버 버전 확인\n'
                ' - 메일 UI가 변경된 경우 CSS 셀렉터를 조정하세요.\n'
            )  # print 종료

    except LoginError as exc:  # 로그인 단계에서의 예외 처리
        print(f'[로그인 실패] {exc}', file=sys.stderr)  # 에러 메시지 출력
        sys.exit(2)  # 종료 코드 2로 종료
    except Exception as exc:  # pylint: disable=broad-except  # 그 외 모든 예외 처리
        print(f'[예기치 못한 오류] {exc}', file=sys.stderr)  # 예기치 못한 오류 출력
        sys.exit(3)  # 종료 코드 3으로 종료
    finally:  # 성공/실패와 무관하게 실행
        if driver:  # 드라이버가 생성된 경우
            try:  # 종료 시도
                driver.quit()  # 브라우저/세션 종료
            except Exception:  # 종료 중 오류 무시
                pass  # 조용히 무시

if __name__ == '__main__':  # 모듈이 아닌 스크립트로 직접 실행될 때
    main()  # main 함수 호출
