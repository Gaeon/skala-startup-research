import asyncio
import nest_asyncio

from typing import Dict, List

from langchain.tools.tavily_search import TavilySearchResults
from langchain_teddynote.tools import GoogleNews 

from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.agents import tool

from graphState import GraphState

from dotenv import load_dotenv

load_dotenv()

# Prompt 정의
prompt_template = """

You are a 20-year veteran investment expert. 
To assess the investment potential of the Korea startup {company_name}, research its core technologies and summarize them.

Using TavilySearch and Google Search, investigate the following for {company_name} and provide the summary in Korean:

1. Homepage summary: One or two sentences describing the main technology
2. Technology stack: Collect the 5 most recent news articles related to their tech stack

**Format your answer in Korean.**

"""

# Tool 정의
   # TavilySearch 세팅
tavily_search = TavilySearchResults()
   # GoogleSearch 세팅 
@tool
def google_search(query: str) -> List[Dict[str, str]]:
    """Search Google News by input keyword
    """
    news_tool = GoogleNews()

    return news_tool.search_by_keyword(query, k=5)

# LLM 세팅 
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 에이전트 구성
tech_search_agent = initialize_agent(
    tools=[tavily_search, google_search],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=50,           # 반복 사이클 허용 횟수 증가
    max_execution_time=600       # 최대 실행 시간(초) 증가
)

# 비동기 처리 함수 정의
async def process_startups_async(state: GraphState) -> GraphState:
    for company in state["startup_names"]:
        state["select_startup"] = company
        prompt = prompt_template.format(company_name=company)
        try:
            summary = await tech_search_agent.arun(prompt)
        except Exception as e:
            summary = f"Error during search: {e}"
        state["summary_messages"][company] = summary
    return state


nest_asyncio.apply()  # 이미 실행 중인 루프 대응

# 하나의 회사만 담당하는 fetch() 함수
async def fetch_tech_search(company: str) -> tuple[str, str]:
    # 매번 새 에이전트 인스턴스 생성
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = initialize_agent(
        tools=[tavily_search, google_search],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=50,
        max_execution_time=600,
    )
    prompt = prompt_template.format(company_name=company)
    result = await agent.arun(prompt)
    return company, result

async def process_startups_concurrent(state: GraphState) -> GraphState:
    # 3-1) 각 스타트업에 대한 coroutine 태스크 리스트 생성
    tasks = []
    for company in state["startup_names"]:
        prompt = prompt_template.format(company_name=company)
        # tech_search_agent.arun() 은 coroutine 이므로 바로 create_task 가능
        tasks.append(asyncio.create_task(tech_search_agent.arun(prompt)))

    # 3-2) 모든 태스크 병렬 실행
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 3-3) 결과 매핑
    for company, result in zip(state["startup_names"], results):
        if isinstance(result, Exception):
            state["summary_messages"][company] = f"Error: {result}"
        else:
            state["summary_messages"][company] = result

    return state