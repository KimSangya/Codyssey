# FastAPI와 필요한 모듈들을 불러온다.
# FastAPI → 서버 프레임워크
# APIRouter → 엔드포인트 분리용
# HTTPException → 오류 메시지 반환용
from fastapi import FastAPI, APIRouter, HTTPException

# Dict와 List 타입 힌트를 사용하기 위해 typing 모듈을 불러온다.
from typing import Dict, List

# CSV 파일로 데이터를 저장/불러오기 위해 csv 모듈을 사용한다.
import csv

# 파일 존재 여부를 확인하기 위해 os 모듈을 사용한다.
import os


# FastAPI 애플리케이션 객체 생성
app = FastAPI()

# 라우터 객체 생성 (엔드포인트를 모아 관리하기 위함)
router = APIRouter()

# 할 일(TODO)들을 저장할 리스트 객체
# 이 리스트에는 {'task': '내용', 'status': '상태'} 형태의 딕셔너리가 들어감
todo_list: List[Dict[str, str]] = []

# CSV 파일 이름 정의 (데이터 저장용)
csv_file = 'todo.csv'


def load_todo() -> None:
    """CSV 파일에서 todo_list 데이터를 불러오는 함수"""
    # 파일이 존재하지 않으면 그냥 함수 종료
    if not os.path.exists(csv_file):
        return
    # CSV 파일을 읽기 모드로 열어서 DictReader를 사용해 각 행을 딕셔너리로 읽는다.
    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        # 한 줄씩 todo_list에 추가
        for row in reader:
            todo_list.append(row)


def save_todo() -> None:
    """현재 todo_list 데이터를 CSV 파일로 저장하는 함수"""
    # 리스트가 비어 있으면 저장할 필요 없으므로 종료
    if not todo_list:
        return
    # CSV 파일을 쓰기 모드로 열기 (기존 내용은 덮어씀)
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        # CSV 헤더 정의
        fieldnames = ['task', 'status']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        # 헤더 작성
        writer.writeheader()
        # todo_list 내용을 한 줄씩 CSV에 작성
        writer.writerows(todo_list)


@router.post('/add_todo')
def add_todo(item: Dict[str, str]) -> Dict[str, str]:
    """새로운 TODO 항목을 추가하는 API (POST 요청)"""
    # 입력된 딕셔너리가 비어 있거나, 'task' 키가 없거나, 값이 비어 있으면 에러 반환
    # → 보너스 과제 조건 충족 ✅
    if not item or 'task' not in item or not item['task']:
        # 400 Bad Request 에러와 함께 메시지 반환
        raise HTTPException(status_code=400, detail='입력값이 비어 있습니다.')
    # 기본 상태값을 'pending'으로 설정
    todo = {'task': item['task'], 'status': item.get('status', 'pending')}
    # 새 항목을 리스트에 추가
    todo_list.append(todo)
    # CSV 파일에 저장
    save_todo()
    # 결과를 딕셔너리 형태로 반환
    return {'message': '할 일이 추가되었습니다.', 'todo': todo}


@router.get('/retrieve_todo')
def retrieve_todo() -> Dict[str, List[Dict[str, str]]]:
    """현재 저장된 TODO 목록을 반환하는 API (GET 요청)"""
    # todo_list 내용을 그대로 반환 (JSON 형태로 자동 변환됨)
    return {'todo_list': todo_list}


# 루트 페이지('/') 추가 (선택 사항)
# 브라우저에서 127.0.0.1:8000 접속 시 간단한 메시지를 보여줌
@app.get('/')
def root() -> Dict[str, str]:
    """서버가 정상적으로 실행 중인지 확인하는 루트 경로"""
    return {'message': f'FastAPI TODO 서버 실행 중! 현재 할 일 개수: {len(todo_list)}개'}


# 라우터를 앱에 등록 (add_todo, retrieve_todo 엔드포인트 포함)
app.include_router(router)


# 프로그램이 직접 실행될 때만 load_todo()를 호출해서 기존 데이터 불러오기
# (다른 모듈에서 import될 경우에는 실행되지 않음)
if __name__ == '__main__':
    load_todo()
