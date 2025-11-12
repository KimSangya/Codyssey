from typing import Optional
from pydantic import BaseModel


class TodoItem(BaseModel):
    """수정(UPDATE) 시 사용하는 모델.
    - 문제 명세: '모델은 TodoItem, BaseModel 상속' 요구 충족
    - task/status 둘 중 최소 1개를 전달해야 하며, 검증은 엔드포인트에서 수행
    """
    task: Optional[str] = None
    status: Optional[str] = None
