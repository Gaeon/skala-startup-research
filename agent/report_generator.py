from fpdf import FPDF
from langchain.schema import SystemMessage
from langchain.chat_models import ChatOpenAI
from graphState import GraphState

from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

# Report_Compiler
report_system_prompt = """ 
당신은 벤처캐피탈 분석가로, AI 기반 헬스케어 스타트업 3곳에 대한 투자 평가 보고서를 작성해야 합니다. 다음은 각 스타트업에 대한 요약 정보, CEO 정보, 시장 상황, 경쟁사 비교, 체크리스트 기반 평가 점수, 그리고 투자 판단입니다.

이 데이터를 기반으로 다음 조건을 충족하는 투자 평가 보고서를 작성하세요:

1. 보고서 형식:
   - [1] 스타트업 개요
   - [2] 기술 및 제품 소개
   - [3] 창업자 및 팀 역량
   - [4] 시장 환경 및 성장 가능성
   - [5] 경쟁 우위 및 차별화 요소
   - [6] 평가 항목 분석 (checklist_scores 기반)
   - [7] 종합 의견 및 투자 판단

2. 각 항목은 구체적이고 정량적 혹은 정성적 근거를 포함해야 하며, 데이터에 기반한 분석이 포함되어야 합니다.

3. 문체는 전문적이되, 투자 위원회 보고서 형식을 따르세요. 각 항목은 간결하지만 명확한 논리 전개로 서술합니다.

다음은 평가에 사용할 데이터입니다:

{input}
"""

# 보고서 생성
def generate_report_text(state: GraphState) -> str:
    messages = [SystemMessage(content=report_system_prompt.format(input=GraphState))]
    response = llm.invoke(messages)
    return response.content


def generate_pdf_report_from_text(report_text: str, output_path: str = "./startup_report.pdf") -> str:
    if not report_text:
        raise ValueError("🚫 report_text가 비어 있습니다.")

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("malgun", "", "./malgun-gothic.ttf", uni=True)
    pdf.set_font("malgun", size=12)

    pdf.multi_cell(0, 8, report_text)
    pdf.output(output_path)

    return output_path
