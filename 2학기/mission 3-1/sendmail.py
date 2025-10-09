#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sendmail.py

Gmail SMTP 서버를 통해 이메일을 발송하는 스크립트.
- 표준 라이브러리만 사용 (smtplib, ssl, email, argparse 등)
- PEP 8 스타일, 기본적으로 단일 인용부호 사용
- 환경변수에서 자격증명 읽기: GMAIL_ADDRESS, GMAIL_APP_PASSWORD
- STARTTLS(587) 기본, 실패 시 SSL(465)로 재시도
- 첨부파일 옵션 지원
- 예외 처리 및 명확한 종료 코드

사용 예:
    python sendmail.py --to you@example.com \
        --subject '테스트' --body '본문입니다.' \
        --attach ./path/to/file.pdf

참고 포트:
    - SMTP 기본 포트: 25
    - SMTP + STARTTLS: 587  (권장)
    - SMTP over SSL: 465
"""

from __future__ import annotations

import argparse
import mimetypes
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path
from typing import List, Optional, Tuple

SMTP_SERVER = 'smtp.gmail.com'
PORT_STARTTLS = 587
PORT_SSL = 465


def load_credentials() -> Tuple[str, str]:
    """환경변수에서 Gmail 자격증명을 읽어 반환한다."""
    addr = os.getenv('GMAIL_ADDRESS', '').strip()
    pwd = os.getenv('GMAIL_APP_PASSWORD', '').strip()
    if not addr or not pwd:
        raise RuntimeError(
            '환경변수 GMAIL_ADDRESS 또는 GMAIL_APP_PASSWORD 가 비어 있습니다. '
            'Gmail 계정에 2단계 인증을 활성화하고 앱 비밀번호를 생성해 설정하세요.'
        )
    return addr, pwd


def build_message(
    mail_from: str,
    rcpt_to: List[str],
    subject: str,
    body: str,
    attachments: Optional[List[Path]] = None,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
) -> EmailMessage:
    """본문과 첨부파일을 포함한 EmailMessage 객체를 생성한다."""
    msg = EmailMessage()
    msg['From'] = mail_from
    msg['To'] = ', '.join(rcpt_to)
    if cc:
        msg['Cc'] = ', '.join(cc)
    msg['Subject'] = subject

    # 본문 설정 (plain text)
    msg.set_content(body)

    # 첨부파일 처리
    for path in attachments or []:
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f'첨부파일을 찾을 수 없습니다: {path}')
        ctype, encoding = mimetypes.guess_type(str(path))
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        with path.open('rb') as fp:
            data = fp.read()
        msg.add_attachment(
            data,
            maintype=maintype,
            subtype=subtype,
            filename=path.name,
        )

    # BCC는 헤더에 표시하지 않음
    if bcc:
        # email.message 자체에는 Bcc 헤더를 넣지 않고, 전송 단계에서 수신자 목록에만 포함
        pass

    return msg


def send_via_starttls(
    username: str,
    password: str,
    msg: EmailMessage,
    all_recipients: List[str],
) -> None:
    """STARTTLS(587)로 메일을 전송한다."""
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, PORT_STARTTLS, timeout=30) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(username, password)
        server.send_message(msg, from_addr=username, to_addrs=all_recipients)


def send_via_ssl(
    username: str,
    password: str,
    msg: EmailMessage,
    all_recipients: List[str],
) -> None:
    """SSL(465)로 메일을 전송한다."""
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, PORT_SSL, context=context, timeout=30) as server:
        server.login(username, password)
        server.send_message(msg, from_addr=username, to_addrs=all_recipients)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """CLI 인자를 파싱한다."""
    parser = argparse.ArgumentParser(
        prog='sendmail.py',
        description='Gmail SMTP를 이용해 이메일을 발송합니다.'
    )
    parser.add_argument(
        '--to',
        dest='to',
        required=True,
        nargs='+',
        help='수신자 이메일 주소(공백으로 여러 개).'
    )
    parser.add_argument(
        '--cc',
        dest='cc',
        nargs='*',
        default=[],
        help='참조(CC) 이메일 주소(선택).'
    )
    parser.add_argument(
        '--bcc',
        dest='bcc',
        nargs='*',
        default=[],
        help='숨은참조(BCC) 이메일 주소(선택).'
    )
    parser.add_argument(
        '--subject',
        dest='subject',
        required=True,
        help='메일 제목.'
    )
    parser.add_argument(
        '--body',
        dest='body',
        required=True,
        help='메일 본문(일반 텍스트).'
    )
    parser.add_argument(
        '--attach',
        dest='attach',
        nargs='*',
        default=[],
        help='첨부파일 경로(공백으로 여러 개, 선택).'
    )
    parser.add_argument(
        '--ssl',
        dest='force_ssl',
        action='store_true',
        help='SSL(465) 강제 사용; 기본은 STARTTLS(587).'
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """엔트리 포인트."""
    try:
        args = parse_args(argv)
        username, password = load_credentials()

        to_list = args.to
        cc_list = args.cc or []
        bcc_list = args.bcc or []
        attachments = [Path(p).expanduser().resolve() for p in args.attach or []]

        msg = build_message(
            mail_from=username,
            rcpt_to=to_list,
            subject=args.subject,
            body=args.body,
            attachments=attachments,
            cc=cc_list,
            bcc=bcc_list
        )

        all_recipients = list(dict.fromkeys(to_list + cc_list + bcc_list))

        if not all_recipients:
            raise ValueError('수신자 목록이 비어 있어 메일을 보낼 수 없습니다.')

        if args.force_ssl:
            send_via_ssl(username, password, msg, all_recipients)
        else:
            try:
                send_via_starttls(username, password, msg, all_recipients)
            except (smtplib.SMTPException, OSError):
                # 네트워크 또는 서버 정책 문제 시 SSL로 재시도
                send_via_ssl(username, password, msg, all_recipients)

        print('메일 발송 성공')
        return 0

    except FileNotFoundError as e:
        print(f'파일 오류: {e}', file=sys.stderr)
        return 2
    except smtplib.SMTPAuthenticationError as e:
        print('인증 실패: Gmail 주소 또는 앱 비밀번호를 확인하세요.', file=sys.stderr)
        print(str(e), file=sys.stderr)
        return 3
    except smtplib.SMTPRecipientsRefused as e:
        print('수신자가 거부되었습니다: 대상 주소를 확인하세요.', file=sys.stderr)
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
