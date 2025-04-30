from typing import TypedDict, List, Dict
from typing import Annotated
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
    # startup_names: Annotated[List[str], add_messages]  # 메시지 누적처럼 업데이트 허용
    startup_names: List[str]
    select_startup: str  # 현재 탐색 중인 기업명

    # *_messages의 형태: {"기업명" : "해당 결과값"} 와 같이 dict type
    summary_messages: dict  # 기술 요약 정보
    ceo_messages: dict      # CEO 평가 정보
    market_messages: dict   # 시장 평가 정보
    competitor_messages: dict  # 경쟁사 정보

    # 투자판단 결과 저장을 위한 필드
    checklist_scores: List[List[str]]  # startup별 checklist 점수 배열
    investment_decisions: List[str]    # 각 startup의 투자 판단 결과 ('투자'/'보류')
