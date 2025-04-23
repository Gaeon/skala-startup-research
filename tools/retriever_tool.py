from langchain_opentutorial.rag.pdf import PDFRetrievalChain
from langchain_core.tools.retriever import create_retriever_tool
from langchain_core.prompts import PromptTemplate

def load_pdf_retriever_tool(pdf_path: str = "data/checklist.pdf"):
    # 1. PDF retriever 생성
    pdf_chain = PDFRetrievalChain([pdf_path]).create_chain()
    pdf_retriever = pdf_chain.retriever

    # 2. Tool 생성
    retriever_tool = create_retriever_tool(
        pdf_retriever,
        name="checklist_retriever",
        description="Search and retrieve investment criteria for e-health startup evaluation from the checklist PDF.",
        document_prompt=PromptTemplate.from_template(
            "You are analyzing whether a healthcare AI startup meets investment criteria.\n"
            "Refer to the following checklist items from the investment evaluation PDF:\n\n"
            "{page_content}\n\n"
            "Answer the following question based only on this checklist:"
        )
    )

    return retriever_tool