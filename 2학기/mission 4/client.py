import sys
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = 'http://127.0.0.1:8000'


def http_get(path: str) -> None:
    try:
        with urlopen(BASE + path) as resp:
            data = resp.read().decode('utf-8')
            print(data)
    except HTTPError as e:
        print(f'HTTPError: {e.code} {e.reason}')
        print(e.read().decode('utf-8'))
    except URLError as e:
        print(f'URLError: {e.reason}')


def http_json(method: str, path: str, payload: dict) -> None:
    try:
        body = json.dumps(payload).encode('utf-8')
        req = Request(BASE + path, data=body, method=method)
        req.add_header('Content-Type', 'application/json')
        with urlopen(req) as resp:
            data = resp.read().decode('utf-8')
            print(data)
    except HTTPError as e:
        print(f'HTTPError: {e.code} {e.reason}')
        print(e.read().decode('utf-8'))
    except URLError as e:
        print(f'URLError: {e.reason}')


def http_delete(path: str) -> None:
    try:
        req = Request(BASE + path, method='DELETE')
        with urlopen(req) as resp:
            data = resp.read().decode('utf-8')
            print(data)
    except HTTPError as e:
        print(f'HTTPError: {e.code} {e.reason}')
        print(e.read().decode('utf-8'))
    except URLError as e:
        print(f'URLError: {e.reason}')


def usage() -> None:
    print('Usage:')
    print('  python client.py list')
    print('  python client.py get <id>')
    print('  python client.py add "<task>" [status]')
    print('  python client.py update <id> [task="<task>"] [status=<status>]')
    print('  python client.py delete <id>')


def main() -> None:
    if len(sys.argv) < 2:
        usage()
        return

    cmd = sys.argv[1]

    if cmd == 'list':
        http_get('/todos')
        return

    if cmd == 'get':
        if len(sys.argv) != 3:
            usage()
            return
        todo_id = sys.argv[2]
        http_get(f'/todos/{todo_id}')
        return

    if cmd == 'add':
        if len(sys.argv) < 3:
            usage()
            return
        task = sys.argv[2]
        status = 'pending' if len(sys.argv) < 4 else sys.argv[3]
        http_json('POST', '/todos', {'task': task, 'status': status})
        return

    if cmd == 'update':
        if len(sys.argv) < 3:
            usage()
            return
        todo_id = sys.argv[2]
        payload: dict = {}
        for arg in sys.argv[3:]:
            if arg.startswith('task='):
                payload['task'] = arg[len('task='):]
            elif arg.startswith('status='):
                payload['status'] = arg[len('status='):]
        http_json('PUT', f'/todos/{todo_id}', payload)
        return

    if cmd == 'delete':
        if len(sys.argv) != 3:
            usage()
            return
        todo_id = sys.argv[2]
        http_delete(f'/todos/{todo_id}')
        return

    usage()


if __name__ == '__main__':
    main()
