from typing import TypedDict, Annotated, List, Dict
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
    startup_names: Annotated[list, "names"] # 탐색할 스타트업 기업명 리스트
    select_startup : Annotated[str, "current_startup"] # 현재 탐색 중인 기업명
        
    # *_messages의 형태: {"기업명" : "해당 결과값"} 와 같이 dict type
    summary_messages: Annotated[dict, add_messages] # 누적으로 저장할 기술 요약 정보 
    ceo_messages: Annotated[dict, add_messages] # 누적으로 저장할 CEO 평가 정보  
    market_messages: Annotated[dict, add_messages] # 누적으로 저장할 시장 평가 정보 
    competitor_messages: Annotated[dict, add_messages] # 누적으로 저장할 경쟁사 정보

    # 투자판단 결과 저장을 위한 필드
    checklist_scores: Annotated[list[list[str]], "startup별 checklist 점수 배열"]
    investment_decisions: Annotated[list[str], "각 startup의 투자 판단 결과 ('투자'/'보류')"]