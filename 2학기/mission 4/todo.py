from fastapi import FastAPI, APIRouter, HTTPException
from typing import Dict, List, Tuple
import csv
import os

from model import TodoItem


app = FastAPI(title='CSV Todo API', version='1.0.0')
router = APIRouter()

# 내부 메모리 저장소 (서버 구동 중 동기화)
# 각 항목: {'id': int, 'task': str, 'status': str}
todo_list: List[Dict[str, object]] = []

# CSV 파일 경로
CSV_FILE = 'todo.csv'


# ---------------------------
# 유틸리티
# ---------------------------
def ensure_csv_header() -> None:
    """CSV 파일이 없거나 비어 있으면 헤더를 생성한다."""
    need_header = False
    if not os.path.exists(CSV_FILE):
        need_header = True
    else:
        # 파일은 있지만 비어 있거나 헤더가 없는 경우 대비
        try:
            with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
                first = f.readline()
                if not first or 'id' not in first:
                    need_header = True
        except FileNotFoundError:
            need_header = True

    if need_header:
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'task', 'status'])
            writer.writeheader()


def read_all_from_csv() -> List[Dict[str, object]]:
    """CSV에서 모든 항목을 읽어 리스트로 반환한다.
    - 기존 4-1 과제의 'task,status'만 있던 CSV도 자동으로 id 부여해 마이그레이션함.
    """
    ensure_csv_header()
    items: List[Dict[str, object]] = []
    with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        temp: List[Tuple[int, str, str]] = []
        next_id = 1
        for row in reader:
            if 'id' in row and row['id']:
                try:
                    rid = int(row['id'])
                except ValueError:
                    rid = next_id
                    next_id += 1
            else:
                rid = next_id
                next_id += 1
            task = row.get('task', '') or ''
            status = row.get('status', '') or 'pending'
            temp.append((rid, task, status))

    # id 중복/정렬 정돈
    temp.sort(key=lambda x: x[0])
    items = [{'id': rid, 'task': task, 'status': status} for rid, task, status in temp]
    return items


def write_all_to_csv(items: List[Dict[str, object]]) -> None:
    """리스트 전체를 CSV에 덮어쓴다."""
    ensure_csv_header()
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'task', 'status'])
        writer.writeheader()
        for it in items:
            writer.writerow({
                'id': it['id'],
                'task': it['task'],
                'status': it['status'],
            })


def get_next_id(items: List[Dict[str, object]]) -> int:
    """다음에 사용할 auto-increment id를 계산한다."""
    if not items:
        return 1
    return int(max(int(x['id']) for x in items)) + 1


def find_index_by_id(items: List[Dict[str, object]], todo_id: int) -> int:
    """id로 리스트 인덱스를 찾는다. 없으면 -1."""
    for i, it in enumerate(items):
        if int(it['id']) == todo_id:
            return i
    return -1


# ---------------------------
# 앱 수명주기: 시작 시 CSV 로드
# ---------------------------
@app.on_event('startup')
def on_startup() -> None:
    todo_list.clear()
    todo_list.extend(read_all_from_csv())


# ---------------------------
# 엔드포인트
# ---------------------------
@app.get('/')
def root() -> Dict[str, str]:
    return {'message': f'FastAPI TODO 서버 실행 중! 현재 할 일 개수: {len(todo_list)}개'}


@router.post('/todos')
def add_todo(item: Dict[str, str]) -> Dict[str, object]:
    """새로운 TODO 추가 (POST)
    - 입력 딕셔너리가 비었거나 task가 없으면 400
    - status 미지정 시 'pending'
    """
    if not item or 'task' not in item or not item['task']:
        raise HTTPException(status_code=400, detail='입력값이 비어 있거나 task가 없습니다.')

    task = item['task']
    status = item.get('status', 'pending')
    new_id = get_next_id(todo_list)
    new_item = {'id': new_id, 'task': task, 'status': status}
    todo_list.append(new_item)
    write_all_to_csv(todo_list)
    return {'message': '할 일이 추가되었습니다.', 'todo': new_item}


@router.get('/todos')
def retrieve_todo() -> Dict[str, List[Dict[str, object]]]:
    """전체 조회 (GET)"""
    return {'todo_list': todo_list}


@router.get('/todos/{todo_id}')
def get_single_todo(todo_id: int) -> Dict[str, object]:
    """개별 조회 (GET)"""
    idx = find_index_by_id(todo_list, todo_id)
    if idx == -1:
        raise HTTPException(status_code=404, detail='해당 id의 TODO가 존재하지 않습니다.')
    return todo_list[idx]


@router.put('/todos/{todo_id}')
def update_todo(todo_id: int, item: TodoItem) -> Dict[str, object]:
    """수정 (PUT) — 문제 명세의 TodoItem 모델 사용
    - task/status 둘 중 하나라도 있어야 함
    """
    idx = find_index_by_id(todo_list, todo_id)
    if idx == -1:
        raise HTTPException(status_code=404, detail='해당 id의 TODO가 존재하지 않습니다.')

    # 최소 한 필드 존재 검증
    if item.task is None and item.status is None:
        raise HTTPException(status_code=400, detail='수정할 필드가 없습니다. task 또는 status 중 하나는 필요합니다.')

    if item.task is not None:
        todo_list[idx]['task'] = item.task
    if item.status is not None:
        todo_list[idx]['status'] = item.status

    write_all_to_csv(todo_list)
    return {'message': '할 일이 수정되었습니다.', 'todo': todo_list[idx]}


@router.delete('/todos/{todo_id}')
def delete_single_todo(todo_id: int) -> Dict[str, str]:
    """삭제 (DELETE)"""
    idx = find_index_by_id(todo_list, todo_id)
    if idx == -1:
        raise HTTPException(status_code=404, detail='해당 id의 TODO가 존재하지 않습니다.')
    deleted = todo_list.pop(idx)
    write_all_to_csv(todo_list)
    return {'message': f'Todo {deleted["id"]}이(가) 삭제되었습니다.'}


# 라우터 등록
app.include_router(router)
