import socket
import threading
import sys

def receive_messages(sock):
    """서버로부터 메시지 수신"""
    while True:
        try:
            msg = sock.recv(1024).decode('utf-8')
            if not msg:
                break
            print(msg)
        except Exception:
            print('⚠️ 서버 연결이 종료되었습니다.')
            break

def start_client(host='127.0.0.1', port=12345):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # 서버로부터 메시지 받는 스레드 실행
    thread = threading.Thread(target=receive_messages, args=(sock,))
    thread.daemon = True
    thread.start()

    try:
        while True:
            msg = input()
            sock.sendall(msg.encode('utf-8'))
            if msg.strip() == '/종료':
                break
    except KeyboardInterrupt:
        sock.sendall('/종료'.encode('utf-8'))
    finally:
        sock.close()
        sys.exit()

if __name__ == '__main__':
    start_client()
