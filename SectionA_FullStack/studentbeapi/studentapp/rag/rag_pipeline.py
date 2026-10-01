from .embeddings import embed_text # type: ignore
from .generator import generate_answer
from .vector_store import search_chunks
from .structured_retriever import (
    get_student_data,
    student_data_to_context
)
#main rag pipeline:
#connect student data, document retrieval and gemini to generate final answer

def ask_rag(question, user):
    student_data = get_student_data(user)
    structured_context = student_data_to_context(
        student_data
        )
    query_vector = embed_text([question])

    results = search_chunks(
        query_vector,
        student_id=student_data["student_id"],
        n_results=3
    )

    documents = results["documents"][0]
    metadata = results["metadata"][0]

    document_context = "\n\n".join(
        documents
    )


    context = f"""
STRUCTURED STUDENTDATA:

{structured_context}

UNSTRUCTURED DOCUMENTS:

{document_context}
"""
    result = generate_answer(
        question, 
        context
        )

    sources = []
    for metadata in metadata:
        source = metadata.get("source")
        if source:
            sources.append({
                "document_id": metadata.get("document_id"),
                "source": source,
                "chunk_index": metadata.get("chunk_index")
            })
    response = result.model_dump()
    response["sources"]= sources
    return response