# AI Startup Investment Evaluation Agent
본 프로젝트는 인공지능 스타트업에 대한 투자 가능성을 자동으로 평가하는 에이전트를 설계하고 구현한 실습 프로젝트입니다.

## Overview

- Objective : 생성형 AI 기반 의료 스타트업의 기술력, 시장 가능성, 리스크 분석을 통해 투자 적합성 자동 평가
- Method : LLM 기반 에이전트 + Agentic RAG 구조를 결합한 하이브리드 평가 시스템
- Tools : Tavily, Open AI, FAISS, LangChain

## Features

- AI 스타트업 정보 수집: 의료 분야 AI 스타트업 리스트를 자동으로 수집 밀 출력
- CEO 전문성 및 적합성 확인: CEO 이력과 전문성을 분석하여 창업자 역량 평가
- 스타트업의 기술력 핵심 요약: 기술 핵심 내용과 장단점을 정리하여 기술 경쟁력 요약
- 시장 성장성, 수요 분석: 기술과 시장 데이터를 바탕으로 성장 가능성과 수요, FDA 상태 평가
- 경쟁사 대비 경쟁 우위 및 약점 분석: 경쟁사와의 비교를 통해 차별화 요소와 리스크 도출
- 종합 투자 판단: 다각적 평가 기준을 종합하고, 의료 도메인에 특화된 체크 리스트를 기반으로 LLM을 사용하여 투자 여부 판단
- 결과 요약 보고서 작성: 분석 결과를 기반으로 구조화된 PDF 형태의 투자 평가 보고서 생성

## Tech Stack 

| Category   | Details                      |
|------------|------------------------------|
| Framework  | LangGraph, LangChain, Python |
| LLM        | GPT-4o-mini via OpenAI API   |
| Retrieval  | FAISS                        |

## Agents
 
- Agent startup_research : 스타트업 탐색, AI 스타트업 정보 수집 
- Agent technology_research: 기술 요약, 스타트업의 기술력 핵심
- Agent ceo : CEO 역량 평가, CEO의 전문성 및 적합성
- Agent competitor_analyze : 경쟁사 비교, 경쟁사 대비 경쟁 우위 및 약점 분석
- Agent investment : 투자 판단, 종합 판단 (List, ROI 등)
- Agent report_generator : 보고서 생성, 결과 요약 보고서 생성
- Agent market_evaluation : 시장 평가

## Architecture
![Screenshot 2025-04-23 at 3 27 07 PM (1)](https://github.com/user-attachments/assets/2deecbd6-1fa2-4ea7-8914-860162eec814)   

*자세한 버전   
 <img src="https://github.com/user-attachments/assets/73303236-32ff-4696-bf7f-b66e7bd985eb" width="700" />

## Directory Structure
├── app.py                           # 🚀 실행 진입점 (LangGraph 워크플로우 정의 및 실행)
├── graphState.py                    # 🧠 사용자 정의 GraphState 클래스 (state 타입 지정)
├── .env                             # 🔐 API 키 등 환경변수
├── README.md                        # 📘 프로젝트 설명 문서

├── data/                            # 입력 데이터 저장소 (예: PDF 문서)
│   ├── checklist.pdf
│   └──digital_health_success_factors.pdf
│
├── outputs/                         # 평가 결과 및 리포트 저장
│   └── final_report.pdf
│
└── agents/                          # 기능별 LangGraph Agent (노드 단위)
    ├── __init__.py
    ├── startup_research.py         # 스타트업 리스트 수집 (list_startups)
    ├── technology_research.py      # 기술 분석 (process_startups_concurrent)
    ├── ceo.py                      # CEO 평가 (evaluate_companies)
    ├── market_evaluation.py        # 시장성 분석 (market_eval_agent)
    ├── competitor_analyze.py       # 경쟁사 분석 (startups_competitor)
    ├── investment.py               # 투자 판단 (investment_judgement_async)
    └── report_generator.py         # 최종 보고서 작성 (generate_report_text)

## Contributors 
- 김가언 : Agent investment
- 김재현 : Agent market_evaluation
- 서찬영 : Agent ceo, Agent report_generator
- 유소영 : Agent technology_research
- 이현희 : Agent competitor_analyze
- 최헤정 : Agent startup_research
