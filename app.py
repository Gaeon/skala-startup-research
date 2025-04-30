from dotenv import load_dotenv
from graphState import GraphState
from langgraph.graph import END, StateGraph, START

from agent.report_generator import generate_report_text
# from agent.technology_research import process_startups_concurrent
from agent.technology_research import process_startups_tech
from agent.ceo import evaluate_companies
from agent.competitor_analyze import startups_competitor
from agent.investment import investment_judgement_async
from agent.startup_research import list_startups
from agent.market_evaluation import market_eval_agent


load_dotenv()


def create_initial_state(user_message="유망한 AI 의료 스타트업을 조사합니다."):
    """초기 상태 생성"""
    return {
        "startup_names": [],
        "select_startup": "",
        "summary_messages": {},
        "ceo_messages": {},
        "market_messages": {},
        "competitor_messages": {},
        "startup_scores": [],
        "messages": [
            {"role": "user", "content": "유망한 AI 의료 스타트업을 조사합니다."}
        ]
    }

workflow = StateGraph(GraphState)

workflow.add_node("startup_researcher", list_startups)       
# workflow.add_node("technology_researcher", process_startups_concurrent)       
workflow.add_node("technology_researcher", process_startups_tech)       
workflow.add_node("market_evaluation", market_eval_agent)       
workflow.add_node("ceo_evaluation", evaluate_companies)         
workflow.add_node("competitor_analyzation", startups_competitor)       
workflow.add_node("investment_judgement", investment_judgement_async)       
workflow.add_node("report_generator", generate_report_text)       
# workflow.add_node("report_generator", generate_pdf_report_from_text)       



# workflow.add_edge("startup_researcher", "technology_researcher")
# workflow.add_edge("technology_researcher", "market_evaluation")
workflow.add_edge("startup_researcher", "market_evaluation")

workflow.add_edge("startup_researcher", "ceo_evaluation")
workflow.add_edge("startup_researcher", "competitor_analyzation")

workflow.add_edge("market_evaluation", "investment_judgement")
workflow.add_edge("ceo_evaluation", "investment_judgement")
workflow.add_edge("competitor_analyzation", "investment_judgement")

workflow.add_edge("investment_judgement", "report_generator")

workflow.add_edge(START, "startup_researcher")
workflow.add_edge("report_generator", END)

graph = workflow.compile()

# graph.get_graph().print_ascii()

initial_state = create_initial_state()
# final_state = graph.run(initial_state)
# result = graph.invoke(initial_state)
# result = graph.invoke(initial_state)





import asyncio

async def main():
    result = await graph.ainvoke(initial_state)
    print(result)

asyncio.run(main())


# print(result)
