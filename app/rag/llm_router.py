from .llm_client import query_local_llm, query_via_openrouter
from .prompt_type import Prompt
from .preprocessor import preprocess_pipeline
from .embedder import embedding_pipeline, generate_embeddings
from .vector_store import ContentStore
import torch


content_store = None


def prepare_doc_retrieval(doc_path):
    if (doc_path == ""):
        return
    
    global content_store
    
    print(f"[RAG] Starting document retrieval for: {doc_path}")
    processed_chunks = preprocess_pipeline(doc_path)
    chunk_entries = embedding_pipeline(processed_chunks)

    content_store = ContentStore(chunk_entries)
    print(f"[RAG] Content store initialized with {len(chunk_entries)} chunks")


def query_llm(
    question,
    mode: str,
    model=None
):
    prompt = Prompt("", question)
    response = ""

    if content_store is None:
        return

    query = prompt.question
    query_embedding_tensor = generate_embeddings([query])
    query_embedding = query_embedding_tensor[0].cpu().numpy().astype("float32")

    retrieved_chunks = content_store.query(query_embedding)
    prompt.context = "\n\n".join(retrieved_chunks)

    if mode == "offline":
        raise NotImplementedError

    else:
        response = query_via_openrouter(prompt)
    
    return response