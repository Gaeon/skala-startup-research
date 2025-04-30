import json
import asyncio
from langchain.agents import create_tool_calling_agent, AgentExecutor
# from langchain_openai import ChatOpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.prompts import PromptTemplate
from langchain.tools.retriever import create_retriever_tool
from langchain_opentutorial.rag.pdf import PDFRetrievalChain
from langchain_community.document_loaders import PDFPlumberLoader
import os
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI  # ✅ 이게 진짜 "bind_tools" 지원함!

from graphState import GraphState

from dotenv import load_dotenv

load_dotenv()

loader = PyPDFLoader(os.path.join(os.path.dirname(__file__), "data", "checklist.pdf"))
docs = loader.load()

vectorstore = FAISS.from_documents(docs, OpenAIEmbeddings())
retriever = vectorstore.as_retriever()


async def investment_judgement_async(state: GraphState) -> GraphState:
    print("⭐️⭐️⭐️⭐️⭐️⭐️ Invest Start : ")
    print(state)

	# ✅ 1. PDF 기반 retriever_tool 생성
    retriever_tool = create_retriever_tool(
        retriever=retriever,
        name="checklist_retriever",
        description="Search investment checklist from PDF for e-health startup evaluation.",
        document_prompt=PromptTemplate.from_template(
            "You are analyzing investment criteria for e-health AI startups.\n"
            "Refer to the checklist below:\n\n{page_content}\n\nAnswer the question accordingly:"
        )
    )

    tools = [retriever_tool]

    # ✅ 2. LLM & AgentExecutor 정의
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an investment expert for e-health startups."),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    # agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False) # 와라락출력 수정

    # ✅ 3. checklist 항목 JSON 추출
    checklist_prompt = (
        "From the investment checklist PDF, extract the 10 evaluation criteria "
        "along with their sub-points.\n\n"
        "Return the result in JSON format like this:\n\n"
        "[{\"title\": \"...\", \"details\": [\"...\", \"...\"]}, ...]"
    )
    checklist_items_raw = await agent_executor.ainvoke({"input": checklist_prompt})
    try:
        checklist_items = json.loads(checklist_items_raw.get("output", ""))
    except json.JSONDecodeError:
        print("❌ JSON 파싱 실패:\n", checklist_items_raw)
        checklist_items = []

    print("✅ Checklist 항목 수:", len(checklist_items))

    # ✅ 4. 비동기 스타트업 평가 함수 정의
    async def evaluate_startup(name: str):
        messages = [
            state["summary_messages"].get(name, ""),
            f'CEO: {state["ceo_messages"].get(name, {}).get("evaluation", "")}',
            f'Market: {state["market_messages"].get(name, {}).get("summary", "")}',
            f'Competitor: {state["competitor_messages"].get(name, "")}',
        ]
        context = " ".join(messages)
        row_score = []

        for item in checklist_items:
            title = item.get("title", "")
            details = item.get("details", [])
            detail_str = "\n".join(f"- {point}" for point in details)

            prompt = (
                f"Checklist Item: {title}\n"
                f"Sub-points:\n{detail_str}\n\n"
                f"Startup Info:\n{context}\n\n"
                f"Based on the sub-points, does this startup meet the above checklist criterion?"
            )

            result = await agent_executor.ainvoke({"input": prompt})
            score = 1 if "yes" in result.get("output", "").lower() else 0
            row_score.append(score)

        decision = "투자" if sum(row_score) / len(row_score) >= 0.1 else "보류"
        return row_score, decision

    # ✅ 5. 전체 기업 병렬 평가 실행
    tasks = [evaluate_startup(name) for name in state["startup_names"]]
    results = await asyncio.gather(*tasks)

    # ✅ 6. 결과 저장
    checklist_scores = []
    investment_decisions = []
    for score, decision in results:
        checklist_scores.append(score)
        investment_decisions.append(decision)

    state["checklist_scores"] = checklist_scores
    state["investment_decisions"] = investment_decisions

    print(checklist_scores)
    print(investment_decisions)

    # print(state)

    print("⭐️⭐️⭐️⭐️⭐️⭐️ Invest End : ")
    print(state)
    return state