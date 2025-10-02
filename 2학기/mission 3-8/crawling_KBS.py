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

import os
import sys
import time
from typing import List, Optional, Tuple

from selenium import webdriver  # 허용 라이브러리(과제 지시에 따라 사용)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


NAVER_HOME = 'https://www.naver.com/'
NAVER_LOGIN_PAGE = (
    'https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com/'
)
NAVER_MAIL = 'https://mail.naver.com/'


class LoginError(Exception):
    """네이버 로그인 실패 시 사용되는 예외 클래스."""
    pass


def build_driver(headless: bool = False) -> WebDriver:
    """
    크롬 WebDriver를 생성한다.

    Args:
        headless: 헤드리스 모드 사용 여부.

    Returns:
        생성된 WebDriver 객체.
    """
    chrome_options = Options()
    if headless:
        # 로그인 과정에서 캡차/보안 경고가 나올 수 있으므로
        # 과제 시연 때는 가능하면 헤드리스 비권장.
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--window-size=1280,900')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--lang=ko-KR')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')

    # ChromeDriver가 PATH에 있다고 가정
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(2)
    return driver


def wait_for(
    driver: WebDriver,
    by: By,
    selector: str,
    timeout: int = 10
):
    """
    특정 요소가 나타날 때까지 대기한다.

    Args:
        driver: WebDriver
        by: By 타입
        selector: CSS/XPath 등 셀렉터 문자열
        timeout: 최대 대기 초

    Returns:
        찾은 요소(WebElement)
    """
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, selector))
    )


def collect_public_content(driver: WebDriver) -> List[str]:
    """
    비로그인 상태에서 네이버 메인에서 확인 가능한 공개 콘텐츠 일부를 수집한다.
    (예: 메인 뉴스·쇼핑/엔터테인먼트 블록 타이틀 텍스트 등)

    Returns:
        공개 콘텐츠 텍스트 리스트
    """
    driver.get(NAVER_HOME)
    time.sleep(1)

    texts: List[str] = []

    # 메인 '뉴스스탠드' 섹션 제목 후보들
    candidates = [
        (By.CSS_SELECTOR, 'h2.NM_THEME_META_title'),
        (By.CSS_SELECTOR, 'div.header_area h2'),
        (By.CSS_SELECTOR, 'h2#NM_THEME_META'),
    ]

    for by, sel in candidates:
        try:
            elems = driver.find_elements(by, sel)
            for e in elems:
                t = e.text.strip()
                if t:
                    texts.append(t)
        except Exception:
            continue

    # 메인에 걸린 큰 타이틀/섹션들 일부 더 수집 (안 보이면 skip)
    more_candidates = [
        (By.CSS_SELECTOR, 'section h2'),
        (By.CSS_SELECTOR, 'div.group_title'),
        (By.CSS_SELECTOR, 'h3'),
    ]
    for by, sel in more_candidates:
        try:
            elems = driver.find_elements(by, sel)
            for e in elems[:5]:
                t = e.text.strip()
                if t and t not in texts:
                    texts.append(t)
        except Exception:
            continue

    # 중복 제거, 상위 몇 개만
    dedup = []
    for t in texts:
        if t and t not in dedup:
            dedup.append(t)
    return dedup[:10]


def login_naver(driver: WebDriver, user_id: str, user_pw: str) -> None:
    """
    네이버에 로그인한다.

    Args:
        driver: WebDriver
        user_id: 네이버 아이디
        user_pw: 네이버 비밀번호

    Raises:
        LoginError: 로그인 실패 시
    """
    driver.get(NAVER_LOGIN_PAGE)
    # 로그인 페이지 로드 대기
    wait_for(driver, By.TAG_NAME, 'body', timeout=10)

    # 네이버는 보안상 자동화 차단 로직/캡차가 있을 수 있음
    # 기본 id/pw 필드 ID 시도 + 대체 셀렉터 시도
    filled = False
    selectors: List[Tuple[By, str]] = [
        (By.ID, 'id'),
        (By.NAME, 'id'),
        (By.CSS_SELECTOR, 'input#id'),
        (By.CSS_SELECTOR, 'input[name="id"]'),
    ]
    pw_selectors: List[Tuple[By, str]] = [
        (By.ID, 'pw'),
        (By.NAME, 'pw'),
        (By.CSS_SELECTOR, 'input#pw'),
        (By.CSS_SELECTOR, 'input[name="pw"]'),
    ]

    # 아이디/비밀번호 입력
    for by1, sel1 in selectors:
        for by2, sel2 in pw_selectors:
            try:
                id_box = wait_for(driver, by1, sel1, timeout=6)
                pw_box = wait_for(driver, by2, sel2, timeout=6)
                id_box.clear()
                id_box.send_keys(user_id)
                pw_box.clear()
                pw_box.send_keys(user_pw)
                filled = True
                break
            except Exception:
                continue
        if filled:
            break

    if not filled:
        # 동적으로 가려놓은 필드가 있을 수 있어 JS로 입력 보조
        try:
            driver.execute_script(
                'document.querySelector("#id").value = arguments[0];', user_id
            )
            driver.execute_script(
                'document.querySelector("#pw").value = arguments[0];', user_pw
            )
            filled = True
        except Exception as exc:
            raise LoginError('로그인 필드를 찾을 수 없습니다.') from exc

    # 로그인 버튼 클릭 시도
    clicked = False
    login_btn_candidates: List[Tuple[By, str]] = [
        (By.ID, 'log.login'),
        (By.CSS_SELECTOR, 'button.btn_login'),
        (By.CSS_SELECTOR, 'input.btn_login'),
        (By.CSS_SELECTOR, 'button[type="submit"]'),
        (By.XPATH, '//button[contains(@class,"btn_login")]'),
    ]
    for by, sel in login_btn_candidates:
        try:
            btn = driver.find_element(by, sel)
            btn.click()
            clicked = True
            break
        except Exception:
            continue

    if not clicked:
        # JS로 submit
        try:
            driver.execute_script(
                'document.querySelector("form").submit();'
            )
            clicked = True
        except Exception as exc:
            raise LoginError('로그인 버튼 클릭 실패') from exc

    # 로그인 처리 대기 (리다이렉트 후 메인 노출)
    time.sleep(2)
    # 로그인 여부 간단 체크: 상단 우측 프로필 버튼/메일 메뉴 여부 등
    try:
        driver.get(NAVER_HOME)
        time.sleep(1)
        # 프로필/알림 벨/메일 아이콘 등 요소 중 하나라도 보이면 성공으로 간주
        any_logged_marker = False
        probes: List[Tuple[By, str]] = [
            (By.CSS_SELECTOR, 'a#NM_mail_icon'),       # 메일
            (By.CSS_SELECTOR, 'a#NM_ly_la'),           # 프로필/알림
            (By.CSS_SELECTOR, 'a#NM_MY'),              # MY 네이버
            (By.CSS_SELECTOR, 'a[href*="mail.naver.com"]'),
        ]
        for by, sel in probes:
            elems = driver.find_elements(by, sel)
            if elems:
                any_logged_marker = True
                break
        if not any_logged_marker:
            raise LoginError('로그인 표시 요소를 찾지 못했습니다.')
    except Exception as exc:
        raise LoginError('로그인 확인 실패') from exc


def collect_mail_subjects(driver: WebDriver, limit: int = 20) -> List[str]:
    """
    로그인된 세션으로 네이버 메일함 제목을 수집한다.

    Args:
        driver: WebDriver
        limit: 최대 수집 개수

    Returns:
        메일 제목 리스트
    """
    driver.get(NAVER_MAIL)
    # 메일 페이지 로드 대기
    wait_for(driver, By.TAG_NAME, 'body', timeout=15)
    time.sleep(2)

    subjects: List[str] = []

    # 다양한 DOM 구조를 대비한 다중 셀렉터 시도
    sel_candidates: List[Tuple[By, str]] = [
        # 신규 UI 예시
        (By.CSS_SELECTOR, 'a.mail_title, a.subject_title, a.subject'),
        # role/grid 기반
        (By.CSS_SELECTOR, '[role="grid"] a'),
        # 예전 UI 대비
        (By.CSS_SELECTOR, 'div.mailList a'),
        # 스팸/프로모션 등 기타 탭도 포함될 수 있으므로 포괄
        (By.CSS_SELECTOR, 'a[href*="read"]'),
    ]

    for by, sel in sel_candidates:
        elems = driver.find_elements(by, sel)
        for e in elems:
            t = (e.text or '').strip()
            if t and t not in subjects:
                subjects.append(t)
        if subjects:
            break

    # 불필요한 항목 필터링(예: 체크박스 대체 텍스트나 공백성 텍스트)
    cleaned = []
    for t in subjects:
        if len(t) >= 2 and '삭제' not in t and '중요' not in t:
            cleaned.append(t)

    return cleaned[:limit]


def main() -> None:
    """
    스크립트 엔트리 포인트.
    - 비로그인 상태 공개 콘텐츠 수집
    - 로그인
    - 로그인 전용 콘텐츠(메일 제목) 수집
    - 결과 출력
    """
    user_id = os.environ.get('NAVER_ID', '')
    user_pw = os.environ.get('NAVER_PW', '')

    if not user_id or not user_pw:
        print(
            '[오류] 환경변수 NAVER_ID / NAVER_PW 를 설정해 주세요.',
            file=sys.stderr
        )
        sys.exit(1)

    driver: Optional[WebDriver] = None
    try:
        driver = build_driver(headless=False)

        print('[1] 비로그인 상태 공개 콘텐츠 수집 중...')
        public_texts = collect_public_content(driver)
        print(f'  - 공개 콘텐츠 예시 ({len(public_texts)}개):')
        for i, t in enumerate(public_texts, start=1):
            print(f'    {i:>2}. {t}')

        print('\n[2] 네이버 로그인 시도...')
        login_naver(driver, user_id, user_pw)
        print('  - 로그인 성공')

        print('\n[3] 로그인 후 콘텐츠(메일 제목) 수집 중...')
        mail_subjects = collect_mail_subjects(driver, limit=30)

        # 결과를 하나의 리스트로 합쳐서(과제 지시: 리스트 객체에 담아 출력)
        # [("category","text"), ...] 형태로 구분 출력
        aggregated: List[Tuple[str, str]] = []
        for t in public_texts:
            aggregated.append(('public', t))
        for t in mail_subjects:
            aggregated.append(('mail', t))

        print('\n[결과] 수집 텍스트 목록:')
        for i, (cat, text) in enumerate(aggregated, start=1):
            print(f'  {i:>2}. [{cat}] {text}')

        if not mail_subjects:
            print(
                '\n[안내] 메일 제목이 보이지 않는 경우:\n'
                ' - 보안/캡차가 뜬 경우 수동 인증 후 다시 실행\n'
                ' - 크롬/드라이버 버전 확인\n'
                ' - 메일 UI가 변경된 경우 CSS 셀렉터를 조정하세요.\n'
            )

    except LoginError as exc:
        print(f'[로그인 실패] {exc}', file=sys.stderr)
        sys.exit(2)
    except Exception as exc:  # pylint: disable=broad-except
        print(f'[예기치 못한 오류] {exc}', file=sys.stderr)
        sys.exit(3)
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


if __name__ == '__main__':
    main()
