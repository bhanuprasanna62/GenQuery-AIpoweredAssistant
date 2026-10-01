import chromadb
from pathlib import Path
from studentapp.rag.embeddings import embed_texts

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHROMA_PATH = BASE_DIR / "chroma_db"

client = chromadb.PersistentClient(
    path = str(CHROMA_PATH)
)

#create or connect to the collections used for student documents
collection = client.get_or_create_collection(
    name="student_documents",
    embedding_function=None
)
def store_chunk(
        chunk_id,
        text,
        embedding,
        student_id,
        document_id,
        source,
        chunk_index
):
    collection.add(
        ids=[chunk_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[
            {
                "student_id":student_id,
                "document_id":document_id,
                "source":source,
                "chunk_index": chunk_index

            }
        ]
    )
def store_chunks(
        chunks,
        embeddings,
        student_id,
        document_id,
        source
):
    #nothing to store if there are no chunks
    if not chunks:
        return  

    #make  sure every chunk has exactky one embedding
    if len(chunks)!= len(embeddings):
        raise ValueError(
            "number of embeddings does not match"
            "number of chunks"
        )  

    #store each chunk with its cooresponding vector and metadata
    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        store_chunk(
            chunk_id=f"{document_id}{index}",
            text=chunk,
            embedding=embedding,
            student_id=student_id,
            document_id=document_id,
            source=source,
            chunk_index=index

        )

def delete_document_chunks(document_id):
    existing = collection.get(
        where={
            "document_id":document_id
        }
    )  
    existing_ids = existing["ids"] 

    #delete the matching chunks from chromadb
    if existing_ids:
        collection.delete(
            ids=existing_ids
        )  
    return len(existing_ids)       

def search_chunks(
        query_embedding,
        student_id,
        n_results=3
):   
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,

        #only search doc belonging to this student
        where={
            "student_id":student_id
        },

        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )  
    return results