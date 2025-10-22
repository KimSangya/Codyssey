#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sendmail_csv_html.py

요구사항 반영:
- HTML 형식 메일 전송 지원 (--html 또는 --body-file 로 HTML 본문 사용)
- 수신자 CSV 파일(mail_target_list.csv: '이름, 이메일')을 읽어 전체 발송
- 두 가지 방식 모두 지원:
  1) bulk : 한 통에 여러 명을 'To'로 열거하여 전송
  2) each : 한 명씩 개별 메일 반복 전송 (개인화/주소노출 방지)
- 표준 라이브러리만 사용 (csv, smtplib, ssl, email, argparse, mimetypes, os, sys, pathlib, typing)
- PEP 8 및 네이밍 가이드 준수(함수: snake_case, 클래스: CapWords; 본 스크립트는 함수 위주)
- 보너스: 네이버 SMTP 발송 옵션 지원(--provider naver)

환경변수:
- Gmail:  GMAIL_ADDRESS, GMAIL_APP_PASSWORD
- Naver:  NAVER_ADDRESS, NAVER_APP_PASSWORD

사용 예시:
  # 1) CSV 기반, 한 명씩 HTML 발송(권장)
  python sendmail_csv_html.py \
      --csv mail_target_list.csv \
      --subject 'Dr. Han – Status Update' \
      --body '<h2>Dear {name},</h2><p>We received your message…</p>' \
      --html \
      --send-strategy each

  # 2) CSV 기반, 한 통에 모두 발송(bulk)
  python sendmail_csv_html.py \
      --csv mail_target_list.csv \
      --subject 'Dr. Han – Status Update' \
      --body '<h2>Hello all,</h2><p>We received the message…</p>' \
      --html \
      --send-strategy bulk

  # 3) 본문을 파일로 로드(HTML 템플릿), 네이버 SMTP 사용
  python sendmail_csv_html.py \
      --csv mail_target_list.csv \
      --subject '소식 전합니다' \
      --body-file ./template.html \
      --html \
      --provider naver

CSV 형식:
  이름, 이메일
  홍길동, hong@example.com
  Jane Doe, jane@example.org
"""

from __future__ import annotations

import argparse
import csv
import mimetypes
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

# SMTP 서버 설정
GMAIL_SMTP = ('smtp.gmail.com', 587, 465)
NAVER_SMTP = ('smtp.naver.com', 587, 465)


def load_credentials(provider: str) -> Tuple[str, str]:
    """환경변수에서 자격증명을 읽어 반환한다."""
    if provider == 'naver':
        addr = os.getenv('NAVER_ADDRESS', '').strip()
        pwd = os.getenv('NAVER_APP_PASSWORD', '').strip()
        if not addr or not pwd:
            raise RuntimeError(
                'NAVER_ADDRESS 또는 NAVER_APP_PASSWORD 환경변수가 비어 있습니다.'
            )
        return addr, pwd
    # default: gmail
    addr = os.getenv('GMAIL_ADDRESS', '').strip()
    pwd = os.getenv('GMAIL_APP_PASSWORD', '').strip()
    if not addr or not pwd:
        raise RuntimeError(
            'GMAIL_ADDRESS 또는 GMAIL_APP_PASSWORD 환경변수가 비어 있습니다. '
            'Gmail 계정에 2단계 인증을 활성화하고 앱 비밀번호를 생성해 설정하세요.'
        )
    return addr, pwd


def which_smtp(provider: str) -> Tuple[str, int, int]:
    """프로바이더에 맞는 SMTP 서버 정보를 반환한다."""
    if provider == 'naver':
        host, port_starttls, port_ssl = NAVER_SMTP
    else:
        host, port_starttls, port_ssl = GMAIL_SMTP
    return host, port_starttls, port_ssl


def read_csv_targets(csv_path: Path) -> List[Tuple[str, str]]:
    """CSV('이름, 이메일')을 읽어 (name, email) 목록을 반환한다."""
    targets: List[Tuple[str, str]] = []
    with csv_path.open('r', encoding='utf-8') as fp:
        reader = csv.reader(fp)
        header = next(reader, None)
        # 헤더가 '이름','이메일'일 것으로 기대하되, 아닌 경우도 유연 처리
        for row in reader:
            if not row:
                continue
            name = (row[0] if len(row) > 0 else '').strip()
            email = (row[1] if len(row) > 1 else '').strip()
            if email:
                targets.append((name, email))
    return targets


def load_body(body_arg: Optional[str], body_file: Optional[Path]) -> str:
    """본문 문자열을 직접 받거나 파일에서 읽어 반환한다."""
    if body_file:
        if not body_file.exists() or not body_file.is_file():
            raise FileNotFoundError(f'본문 파일을 찾을 수 없습니다: {body_file}')
        return body_file.read_text(encoding='utf-8')
    if body_arg is None:
        raise ValueError('본문이 비어 있습니다. --body 또는 --body-file 중 하나를 지정해야 합니다.')
    return body_arg


def is_probably_html(text: str) -> bool:
    """간단한 휴리스틱으로 HTML 여부를 추정한다."""
    snippet = text.strip().lower()
    return snippet.startswith('<!doctype') or snippet.startswith('<html') or ('<' in snippet and '>' in snippet)


def build_message(
    mail_from: str,
    rcpt_to: Iterable[str],
    subject: str,
    body: str,
    is_html: bool,
    attachments: Optional[List[Path]] = None,
    cc: Optional[Iterable[str]] = None,
) -> EmailMessage:
    """본문(HTML 가능)과 첨부파일을 포함한 EmailMessage를 생성한다."""
    msg = EmailMessage()
    msg['From'] = mail_from
    to_list = list(rcpt_to)
    if to_list:
        msg['To'] = ', '.join(to_list)
    if cc:
        cc_list = list(cc)
        if cc_list:
            msg['Cc'] = ', '.join(cc_list)
    msg['Subject'] = subject

    if is_html:
        msg.add_alternative(body, subtype='html')
    else:
        msg.set_content(body)

    for path in attachments or []:
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f'첨부파일을 찾을 수 없습니다: {path}')
        ctype, encoding = mimetypes.guess_type(str(path))
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        data = path.read_bytes()
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=path.name)

    return msg


def send_via_starttls(
    host: str,
    port: int,
    username: str,
    password: str,
    msg: EmailMessage,
    all_recipients: List[str],
) -> None:
    """STARTTLS로 메일을 전송한다."""
    context = ssl.create_default_context()
    with smtplib.SMTP(host, port, timeout=30) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(username, password)
        server.send_message(msg, from_addr=username, to_addrs=all_recipients)


def send_via_ssl(
    host: str,
    port: int,
    username: str,
    password: str,
    msg: EmailMessage,
    all_recipients: List[str],
) -> None:
    """SSL(465)로 메일을 전송한다."""
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=context, timeout=30) as server:
        server.login(username, password)
        server.send_message(msg, from_addr=username, to_addrs=all_recipients)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """CLI 인자를 파싱한다."""
    parser = argparse.ArgumentParser(
        prog='sendmail_csv_html.py',
        description='CSV 대상자에게 HTML 이메일을 발송합니다 (Gmail/Naver, bulk/each 모드).'
    )
    parser.add_argument('--csv', dest='csv_path', required=True, help='수신자 CSV 경로 (이름, 이메일).')
    parser.add_argument('--subject', dest='subject', required=True, help='메일 제목.')
    parser.add_argument('--body', dest='body', help='메일 본문(텍스트 또는 HTML; {name} 치환 가능).')
    parser.add_argument('--body-file', dest='body_file', help='메일 본문 파일 경로(HTML 템플릿 권장).')
    parser.add_argument('--html', dest='is_html', action='store_true', help='본문을 HTML 형식으로 전송.')
    parser.add_argument('--attach', dest='attach', nargs='*', default=[], help='첨부파일 경로(선택).')
    parser.add_argument('--cc', dest='cc', nargs='*', default=[], help='참조(CC) 이메일 주소(선택).')
    parser.add_argument('--ssl', dest='force_ssl', action='store_true', help='SSL(465) 강제; 기본은 STARTTLS(587).')
    parser.add_argument('--provider', dest='provider', choices=['gmail', 'naver'], default='gmail',
                        help='SMTP 제공자 선택 (기본: gmail).')
    parser.add_argument('--send-strategy', dest='strategy', choices=['bulk', 'each'], default='each',
                        help='전송 방식 선택: bulk(한 통에 여러명) / each(한 명씩, 기본).')
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """엔트리 포인트."""
    try:
        args = parse_args(argv)

        provider = args.provider
        host, port_starttls, port_ssl = which_smtp(provider)
        username, password = load_credentials(provider)

        csv_path = Path(args.csv_path).expanduser().resolve()
        targets = read_csv_targets(csv_path)
        if not targets:
            print('수신자 CSV가 비어 있습니다.', file=sys.stderr)
            return 2

        body_src = load_body(args.body, Path(args.body_file).expanduser().resolve() if args.body_file else None)
        is_html = args.is_html or is_probably_html(body_src)
        subject = args.subject
        cc_list = args.cc or []
        attachments = [Path(p).expanduser().resolve() for p in (args.attach or [])]

        # 전략 1) bulk: 한 통에 모든 수신자를 열거
        if args.strategy == 'bulk':
            # bulk는 개인화가 어려우므로 치환 없이 사용
            msg = build_message(
                mail_from=username,
                rcpt_to=[email for _, email in targets],
                subject=subject,
                body=body_src,
                is_html=is_html,
                attachments=attachments,
                cc=cc_list
            )
            all_recipients = [email for _, email in targets] + cc_list
            all_recipients = list(dict.fromkeys(all_recipients))  # 중복 제거

            if args.force_ssl:
                send_via_ssl(host, port_ssl, username, password, msg, all_recipients)
            else:
                try:
                    send_via_starttls(host, port_starttls, username, password, msg, all_recipients)
                except (smtplib.SMTPException, OSError):
                    send_via_ssl(host, port_ssl, username, password, msg, all_recipients)

            print(f'메일 발송 성공(bulk): 총 {len(all_recipients)}명')
            return 0

        # 전략 2) each: 수신자별 개인화(권장)
        success = 0
        fail = 0
        for name, email in targets:
            try:
                # {name} 치환(없으면 영향 없음)
                personalized_body = body_src.format(name=name or '')
                msg = build_message(
                    mail_from=username,
                    rcpt_to=[email],
                    subject=subject,
                    body=personalized_body,
                    is_html=is_html,
                    attachments=attachments,
                    cc=cc_list
                )
                all_recipients = [email] + cc_list

                if args.force_ssl:
                    send_via_ssl(host, port_ssl, username, password, msg, all_recipients)
                else:
                    try:
                        send_via_starttls(host, port_starttls, username, password, msg, all_recipients)
                    except (smtplib.SMTPException, OSError):
                        send_via_ssl(host, port_ssl, username, password, msg, all_recipients)

                print(f'✅ 전송 성공: {name} <{email}>')
                success += 1
            except Exception as e:
                print(f'❌ 전송 실패: {name} <{email}> - {e}', file=sys.stderr)
                fail += 1

        print(f'완료(each): 성공 {success} / 실패 {fail} / 총 {len(targets)}')
        return 0 if fail == 0 else 6

    except FileNotFoundError as e:
        print(f'파일 오류: {e}', file=sys.stderr)
        return 2
    except smtplib.SMTPAuthenticationError as e:
        print('인증 실패: 주소 또는 앱 비밀번호를 확인하세요.', file=sys.stderr)
        print(str(e), file=sys.stderr)
        return 3
    except smtplib.SMTPRecipientsRefused as e:
        print('수신자 거부: 대상 주소 확인 필요.', file=sys.stderr)
        print(str(e), file=sys.stderr)
        return 4
    except smtplib.SMTPException as e:
        print('SMTP 오류가 발생했습니다.', file=sys.stderr)
        print(str(e), file=sys.stderr)
        return 5
    except Exception as e:
        print('예상치 못한 오류가 발생했습니다.', file=sys.stderr)
        print(str(e), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
