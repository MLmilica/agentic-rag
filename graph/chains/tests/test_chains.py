from dotenv import load_dotenv
load_dotenv()

from graph.chains.retraival_grader import GradeDocuments, retrieval_grader

from ingestion import retriever

def test_retrival_grader_answer_yes()->None:
    question = "agent memory"
    docs = retriever.invoke(question)
    doc_txt = docs[1].page_content

    res:GradeDocuments = retrieval_grader.invoke({
        "document": doc_txt,
        "question": question
    })

    assert res.binary_score == "yes"


def test_retrival_grader_answer_no()->None:
    question = "agent memory"
    docs = retriever.invoke(question)
    doc_txt = docs[1].page_content

    res:GradeDocuments = retrieval_grader.invoke({
        "document": doc_txt,
        "question": "how to make a pizza"
    })

    assert res.binary_score == "no"