from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.chat_models import ChatOpenAI
import ast
from langchain_core.prompts import PromptTemplate
import requests
from bs4 import BeautifulSoup

from graphState import GraphState

from dotenv import load_dotenv

load_dotenv()

def fetch_full_text(url: str, max_length: int = 2000) -> str:
    """주어진 URL에서 본문 텍스트를 크롤링해 최대 max_length만큼 반환"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # 스크립트/스타일 제거
        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        return text[:max_length]
    except Exception as e:
        return f"크롤링 실패: {e}"


def list_startups(state: GraphState) -> GraphState:
    print("⭐️⭐️⭐️⭐️⭐️⭐️List Startups")
    """검색 결과에서 스타트업 이름 추출"""
    search_tool = TavilySearchResults()
    result = search_tool.run("의료 생성형AI 스타트업")

    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = PromptTemplate.from_template("""
    다음 텍스트는 유망한 스타트업 관련 웹 검색 결과입니다.
    여기서 언급된 회사 이름만 리스트로 추출하시오.
    ```파이썬 코드 블럭 없이 순수한 리스트 형식으로만 출력하세요.```                                      

    # Output :
    ['기업명1', '기업명2', '기업명3', ...]   

    # Input :                                                                         
    {raw_text}
    """)

    response = llm.invoke(prompt.format(raw_text=result))
    names = ast.literal_eval(response.content)

    state["startup_names"] = names

    return state
