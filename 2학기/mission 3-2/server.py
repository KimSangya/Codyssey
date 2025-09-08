import socket
import threading

clients = {}  # {conn: username}

def broadcast(message, sender=None):
    """모든 클라이언트에게 메시지 전송"""
    for conn in clients:
        try:
            conn.sendall(message.encode('utf-8'))
        except Exception:
            conn.close()
            remove_client(conn)

def remove_client(conn):
    """클라이언트 연결 해제"""
    if conn in clients:
        username = clients[conn]
        del clients[conn]
        broadcast(f'⚠️ {username} 님이 퇴장하셨습니다.')

def handle_client(conn, addr):
    """각 클라이언트별 스레드 함수"""
    try:
        conn.sendall('사용자명을 입력하세요: '.encode('utf-8'))
        username = conn.recv(1024).decode('utf-8').strip()
        clients[conn] = username
        broadcast(f'✅ {username} 님이 입장하셨습니다.')
        while True:
            msg = conn.recv(1024).decode('utf-8')
            if not msg:
                break
            if msg.strip() == '/종료':
                conn.sendall('연결을 종료합니다.'.encode('utf-8'))
                break
            broadcast(f'{username}> {msg}')
    except Exception:
        pass
    finally:
        remove_client(conn)
        conn.close()

def start_server(host='127.0.0.1', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f'💡 서버 시작됨 {host}:{port}')

    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.daemon = True
        thread.start()

if __name__ == '__main__':
    start_server()
