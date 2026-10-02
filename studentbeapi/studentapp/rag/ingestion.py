from pathlib import Path

from studentapp.rag.extractor import extract_text_from_pdf
from studentapp.rag.chunker import split_text
from studentapp.rag.embeddings import embed_text
from studentapp.rag.vector_store import (
    store_chunks,
    delete_document_chunks,
)

def ingest_document(documents):
    file_path = Path(documents.file.path)

    if file_path.suffix.lower() != ".pdf":
        return {
            "status": "skipped",
            "message": "Only PDF files are supported currently",
        }

    text = extract_text_from_pdf(file_path)

    if not text:
        return {
            "status": "failed",
            "message": "No text could be extracted from the PDF",
        }

    chunks = split_text(text)

    if not chunks:
        return {
            "status": "failed",
            "message": "No chunks were created.",
        }

    try:
        embeddings = embed_text(chunks)
    except Exception as e:
        return {
            "status": "failed",
            "message": f"Embeddings failed: {str(e)}",
        }

    if len(embeddings) != len(chunks):
        return {
            "status": "failed",
            "message": (
                "Number of embeddings does not match "
                "number of chunks."
            ),
        }

    try:
        delete_document_chunks(documents.id)
    except Exception as e:
        return {
            "status": "failed",
            "message": f"Could not delete old chunks: {str(e)}",
        }

    try:
        store_chunks(
            chunks=chunks,
            embeddings=embeddings,
            student_id=documents.student_id,
            document_id=documents.id,
            source=documents.title,
        )
    except Exception as e:
        return {
            "status": "failed",
            "message": f"ChromaDB storage failed: {str(e)}",
        }

    return {
        "status": "success",
        "document_id": documents.id,
        "student_id": documents.student_id,
        "chunks": len(chunks),
    }
