import asyncio
import nest_asyncio

from typing import Dict, List, TypedDict, Annotated
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages

from langchain.tools.tavily_search import TavilySearchResults
from langchain_teddynote.tools import GoogleNews 

from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool
from langchain.agents import tool

from graphState import GraphState

def without_startup_names(state: dict) -> dict:
    s = dict(state)
    s.pop("startup_names", None)
    return s







# TavilySearch 세팅 (Tool로 사용)
tavily_search = TavilySearchResults()

@tool
def google_search(query: str) -> List[Dict[str, str]]:
    """Search Google News by input keyword
    """
    news_tool = GoogleNews()

    return news_tool.search_by_keyword(query, k=5)


# ── 3) 1차: 원시 데이터 수집 ───────────────────────
async def fetch_raw(state: GraphState) -> Dict:
    raw_data = {}
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent_fetch = initialize_agent(
        tools=[tavily_search, google_search],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=20,
        max_execution_time=300,
    )
    prompt_template = """
    {name}의 핵심 기술 정보를 수집하세요:
    - 홈페이지 주요 기술 (1–2 문장)
    - 기술 스택 관련 최신 뉴스 5개 출처 없이 헤드라인만
    """
    for company in state["startup_names"]:
        raw = await agent_fetch.ainvoke(prompt_template.format(name=company))
        #state["raw_messages"][company] = raw
        raw_data[company] = raw

    return raw_data

# ── 4) 2차: 캐시된 원시 데이터 요약 ─────────────────
async def summarize_from_raw(state: GraphState, raw_data) -> GraphState:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    for company in state["startup_names"]:
        raw = raw_data.get(company, "")
        prompt = f"""
        아래 원시 데이터에 기반해 {company}의 기술 정보를 항목에 따라 5문장 정도씩으로 요약해주세요:
{raw}
"""
        summary = await llm.ainvoke(prompt)
        state["summary_messages"][company] = summary.content
    return state

# ── 5) 실행 함수 수정: state를 반환하도록 변경 ─────────
async def process_startups_tech(state: GraphState) -> GraphState:
    print("⭐️⭐️⭐️⭐️⭐️⭐️ Tech Start : ")
    # print(state)

    raw_data = await fetch_raw(state)
    state = await summarize_from_raw(state, raw_data)

    print("⭐️⭐️⭐️⭐️⭐️⭐️ Tech Start : ")
    # print(state)
    return without_startup_names(state) 


# 노트북에서 탑레벨 await로 실행 & 결과 확인
# state = await main()