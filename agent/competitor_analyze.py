from tavily import TavilyClient
from pydantic import BaseModel
from typing import List
from langchain_openai import ChatOpenAI

from graphState import GraphState

from dotenv import load_dotenv

load_dotenv()

tavily_client = TavilyClient()

llm = ChatOpenAI(model="gpt-4o-mini",temperature=0)

def search_news_for_subtheme(startup_list):
    response = tavily_client.search(
        query= f"{startup_list} AI 의료 스타트업",
        max_results=5,
        topic="news",
        region="kr",
        days=14,
        include_images=True,     
        include_raw_content=True,
    )
    results = response['results']
    competitors_info = []
    
    for i, result in enumerate(results):
        competitors_info.append({
            'title': result['title'],
            'raw_content': result['raw_content']
        })
    
    return {startup_list: competitors_info}

def search_news_by_subthemes(startup_list):
    search_results = {}
    for subtheme in startup_list:
        result = search_news_for_subtheme(subtheme)
        search_results.update(result)
    return search_results

class PromptInstructions(BaseModel):
    """Instructions on how to prompt the LLM."""
    objective: str
    variables: List[str]
    constraints: List[str]
    requirements: List[str]


# 프롬프트를 LLM에 전달하여 강점과 약점 도출
def extract_strengths_and_weaknesses(news_articles, startup):
    # PromptInstructions 설정
    prompt_instructions = PromptInstructions(
        objective="경쟁사 대비 경쟁 우위 및 약점 작성",
        variables=["advantages", "weakness"],
        constraints=["500자 이내", "한글로 작성"],
        requirements=["경쟁사와 비교"]
    )
    
    prompt = f"""
    Objective: {prompt_instructions.objective}
    Variables: {', '.join(prompt_instructions.variables)}
    Constraints: {', '.join(prompt_instructions.constraints)}
    Requirements: {', '.join(prompt_instructions.requirements)}

    뉴스 요약을 바탕으로 다음을 한국어로 작성해 주세요:
    스타트업: {startup}
    뉴스 내용: {news_articles}
    """
    
    # 'content' 필드가 포함된 메시지 형식으로 변환
    messages = [
        {"role": "system", "content": "You are a helpful assistant.", "type": "Text"},
        {"role": "user", "content": prompt, "type": "Text"}
    ]
    
    # LLM을 사용하여 강점과 약점 분석
    response = llm.invoke(messages)
    result = response.content if response else "결과를 생성할 수 없습니다."
    # result = response['choices'][0]['message']['content'] if response else "결과를 생성할 수 없습니다."
    # result = response[0]['text'] if response else "결과를 생성할 수 없습니다."

    return result

# 스타트업 뉴스 및 강점/약점 분석 결과 출력
result = {}

def startups_competitor(state: GraphState) -> GraphState:
    # 뉴스 검색
    startup_list = state['startup_names']
    news_results = search_news_by_subthemes(startup_list)
    
    for startup, articles in news_results.items():
        #print(f"🔍 스타트업: {startup}")
        combined_news = "\n\n".join(
            [f"[{i+1}] {article['title']}\n{article['raw_content']}" for i, article in enumerate(articles)]
        )

        strengths_and_weaknesses = extract_strengths_and_weaknesses(combined_news, startup)
        #print(f"    🧠 경쟁 우위 및 약점 요약:\n{strengths_and_weaknesses}")
        state['competitor_messages'][startup] = strengths_and_weaknesses

    return state

