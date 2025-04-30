from fpdf import FPDF
from langchain.schema import SystemMessage
# from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
from graphState import GraphState

from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")


# 보고서 생성
def generate_report_text(state: dict, output_path: str = "./startup_report.pdf") -> dict:
    print("⭐️⭐️⭐️⭐️⭐️⭐️ PDF Start : ")
    print(state)
    # 1. state 내용을 문자열로 변환
    state_text = str(state)

    # 2. 보고서 프롬프트 구성
    prompt = f"""
        당신은 벤처캐피탈 분석가입니다. 다음은 스타트업에 대한 다양한 평가 정보입니다.
        이 정보를 기반으로 다음 항목을 포함한 투자 평가 보고서를 작성해주세요:

        1. 스타트업 개요
        2. 기술 및 제품 소개
        3. 창업자 및 팀 역량
        4. 시장 환경 및 성장 가능성
        5. 경쟁 우위 및 차별화 요소
        6. 평가 항목 분석
        7. 종합 의견 및 투자 판단

        명료하고 전문적인 투자 보고서 스타일로 작성하십시오.

        다음은 상태 데이터입니다:
        {state_text}
        """
    # 3. LLM 호출
    response = llm.invoke([SystemMessage(content=prompt)])
    report_text = response.content

    # 4. PDF 생성
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("malgun", "", "C:/Windows/Fonts/malgun.ttf", uni=True)
    pdf.set_font("malgun", size=12)
    pdf.multi_cell(0, 8, report_text)
    # pdf.multi_cell(0, 8, report_text[:1000])

    pdf.output(output_path)

    print("⭐️⭐️⭐️⭐️⭐️⭐️ PDF END : ")
    print(state)

    # 5. 결과 반환
    return {
        **state,
        "report_text": report_text,
        "report_file": output_path
    }

#=========================================
def generate_pdf_report_from_text(report_text: str, output_path: str = "./startup_report.pdf") -> str:
    print("⭐️⭐️⭐️⭐️⭐️⭐️ PDF Start : ")
    print(state)
    

    if not report_text:
        raise ValueError("🚫 report_text가 비어 있습니다.")

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("malgun", "", "./malgun-gothic.ttf", uni=True)
    pdf.set_font("malgun", size=12)

    pdf.multi_cell(0, 8, report_text)
    pdf.output(output_path)





    print("⭐️⭐️⭐️⭐️⭐️⭐️ PDF END : ")
    print(state)

    return {
        **state,
        "report_text": report_text,
        "report_file": output_path
    }
