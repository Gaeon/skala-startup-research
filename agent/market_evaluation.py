from dotenv import load_dotenv
from typing import Dict, List, Any, TypedDict
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.tools.retriever import create_retriever_tool
import re

from graphState import GraphState

from dotenv import load_dotenv

load_dotenv()

# 상태 정의
class MarketEvalState(TypedDict):
    startup_names: List[str]
    startup_technics_summary: Dict[str, str]
    market_evaluation: Dict[str, str]
    fda_approval_status: Dict[str, str]
    evaluation_reasons: Dict[str, str]

# PDF 파일 로드 및 처리
def load_pdf_and_create_retriever():
    # PDF 파일 로드
    loader = PyPDFLoader("./digital_health_success_factors.pdf")
    documents = loader.load()
    
    # 텍스트 스플리팅 (내용은 제공되지 않았으나 필요할 것으로 예상)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    document_chunks = text_splitter.split_documents(documents)
    
    # 벡터 저장소 생성
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(document_chunks, embeddings)
    retriever = vector_store.as_retriever()
    
    # 도구 형태로 정의
    retriever_tool = create_retriever_tool(
        retriever,
        name="pdf_search",
        description="Search for market viability assessment criteria and success factors of digital health companies from the PDF document. Use this tool when you need specific information about evaluating the market potential of growth-stage digital health startups, market demand indicators, scalability factors, competitive positioning, user adoption metrics, regulatory impacts on market growth, and other aspects that would influence the market viability assessment of digital health technologies.",
    )
    
    return retriever, retriever_tool

# 의료 AI 시장성 평가 에이전트
def market_eval_agent(state: GraphState)-> GraphState:
    # 리트리버 생성
    retriever, _ = load_pdf_and_create_retriever()
    
    # LLM 모델 설정
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # 현재 상태에서 정보 추출
    startup_names = state["startup_names"]
    tech_summaries = state["summary_messages"]
    
    # RetrievalQA 체인 설정 - PDF 문서 기반 검색 활용
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    
    # 시장성 평가 프롬프트 - FDA 승인 여부 명확하게 요청
    market_eval_prompt = """당신은 의료 AI 스타트업 시장성 평가 전문가입니다. 
    다음 스타트업의 기술 내용을 분석하고, 디지털 헬스 분야의 성공 요인을 바탕으로 시장성을 평가해주세요.
    
    ## 스타트업 정보:
    스타트업 이름: {startup_name}
    기술 요약: {tech_summary}
    
    ## 평가를 위한 배경 정보:
    {context}
    
    ## 평가 지침:
    1. 위 배경 정보에 언급된 디지털 헬스 성공 요인과 연관성 분석
    2. 현재 의료 AI 트렌드와의 부합성 평가
    3. 해결하려는 의료 문제의 중요성과 범위 평가
    4. 기술적 혁신성과 차별점 분석
    5. 규제 및 인증 획득 가능성 고려
    6. FDA 승인 여부 확인 (승인됨/진행중/해당없음/정보없음 중 하나로 명시)
    
    ## 평가 등급:
    - 상(high): 시장성이 높고 성공 가능성이 큼
    - 중(medium): 일정 수준 가능성은 있으나 추가적인 검토 필요
    - 하(low): 시장성이 낮고 성공 가능성이 낮음
    
    명확한 형식으로 응답해주세요:
    
    평가 등급: [상(high)/중(medium)/하(low) 중 하나만 선택]
    
    FDA 승인 상태: [승인됨/진행중/해당없음/정보없음 중 하나]
    
    평가 이유:
    [상세한 평가 이유를 3-5문장으로 작성]
    """
    
    # 결과 저장용 변수
    market_evaluation = {}
    evaluation_reasons = {}
    fda_approval_status = {}  # FDA 승인 상태 저장용 변수 추가
    
    # 각 스타트업에 대한 평가 진행
    result_dict = {}
    for name in startup_names:
        tech_summary = tech_summaries.get(name, "정보 없음")
        
        # 관련 성공 요인 검색
        query = f"디지털 헬스 분야의 스타트업 성공 요인, 특히 {tech_summary} 관련 내용"
        search_result = qa_chain({"query": query})
        
        # 프롬프트 포맷팅
        formatted_prompt = market_eval_prompt.format(
            startup_name=name,
            tech_summary=tech_summary,
            context=search_result['result']
        )
        
        # LLM에 질의
        response = llm.invoke(formatted_prompt)
        response_text = response.content
        
        # 응답 파싱 - 정규식 활용하여 더 정확하게
        
        # 평가 등급 추출
        grade_match = re.search(r'평가\s*등급\s*:\s*(상\(high\)|중\(medium\)|하\(low\))', response_text)
        if grade_match:
            grade = grade_match.group(1)
        elif "상(" in response_text or "상:" in response_text or "high" in response_text.lower():
            grade = "상(high)"
        elif "중(" in response_text or "중:" in response_text or "medium" in response_text.lower():
            grade = "중(medium)"
        else:
            grade = "하(low)"
        
        # FDA 승인 상태 추출
        fda_match = re.search(r'FDA\s*승인\s*상태\s*:\s*(승인됨|진행중|해당없음|정보없음)', response_text)
        if fda_match:
            fda_status = fda_match.group(1)
        elif "승인됨" in response_text:
            fda_status = "승인됨"
        elif "진행중" in response_text:
            fda_status = "진행중"
        elif "해당없음" in response_text:
            fda_status = "해당없음"
        else:
            fda_status = "정보없음"
        
        # 평가 이유 추출
        reason_match = re.search(r'평가\s*이유\s*:(.*?)(?=\n\n|$)', response_text, re.DOTALL)
        reason = reason_match.group(1).strip() if reason_match else response_text

        result_dict[market_evaluation] = grade
        result_dict[fda_approval_status] = fda_status  # FDA 승인 상태 저장
        result_dict[evaluation_reasons] = reason

        state['market_messages'][name] = result_dict
    # 상태 업데이트 및 반환
    return state