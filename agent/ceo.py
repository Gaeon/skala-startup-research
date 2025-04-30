import os
import openai
from dotenv import load_dotenv
from tavily import TavilyClient

from graphState import GraphState

load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def get_ceo_name_from_web(company_name: str) -> str:
    query = f"{company_name} 대표이사"
    result = tavily.search(query=query, search_depth="basic", include_answer=True)
    answer = result.get("answer")
    if answer and ("대표" in answer or "CEO" in answer or "CTO" in answer):
        return answer.strip()
    return "알 수 없음"

def evaluate_ceo_with_name(company: str, ceo_name: str) -> str:
    prompt = f"""
    다음은 {company}의 CEO {ceo_name}입니다. 이 이름은 외부 웹 검색을 통해 수집된 객관적인 정보입니다.
    보도 자료, 뉴스 기사, 인터뷰 등을 기반으로 아래 항목을 각각 0~100점으로 평가하고,
    자연어 요약 코멘트를 작성한 후, A~F 등급을 제시해주세요.
    1. 산업 전문성
    2. 경력 다양성
    3. 실행력
    4. 신뢰도
    5. 레퍼런스 및 평판
    정보가 부족한 항목은 '정보 부족'으로 명시해도 좋습니다.
    """
    
    response = openai.chat.completions.create(
        model="gpt-4.1-2025-04-14",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def evaluate_companies(state:GraphState) -> GraphState :
    print("⭐️⭐️⭐️⭐️⭐️⭐️ CEO Start : ")
    # print(state)

    ceo_messages={}
    for company in state["startup_names"]:
        # state.select_startup = company
        state["select_startup"] = company
        #print(f"\n🔍 [{company}] 평가 시작")
        ceo_name = get_ceo_name_from_web(company)
        #print(f"👤 CEO 이름 추출 결과: {ceo_name}")
        if ceo_name == "알 수 없음":
            continue
        evaluation = evaluate_ceo_with_name(company, ceo_name)
        # state['ceo_messages'][company] = {
        #     "ceo_name": ceo_name,
        #     "evaluation": evaluation
        # }
        #print(f"✅ 평가 완료 요약: {evaluation[:100]}...")


        ceo_messages[company] = {
           "ceo_name": ceo_name,
            "evaluation": evaluation
        }
        

        
    print("⭐️⭐️⭐️⭐️⭐️⭐️ CEO End : ")
    # print(state)
    return {
        "ceo_messages": ceo_messages
    }