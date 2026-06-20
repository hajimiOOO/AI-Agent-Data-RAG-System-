import os
import shutil

import chromadb
from chromadb.utils import embedding_functions


def load_document(file_path: str) -> str:
    """
    读取 txt / md 文档。
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def split_text(text: str, chunk_size: int = 300) -> list[str]:
    """
    将长文本切分为多个 chunk。
    """
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size].strip()
        if chunk:
            chunks.append(chunk)

    return chunks


def build_vector_db(chunks: list[str], persist_path: str = "./rag_chroma_db"):
    """
    使用 Chroma 构建本地向量数据库。
    """
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )

    if os.path.exists(persist_path):
        shutil.rmtree(persist_path)

    chroma_client = chromadb.PersistentClient(path=persist_path)

    collection = chroma_client.create_collection(
        name="rag_knowledge",
        embedding_function=embedding_function,
    )

    ids = [f"chunk_{i}" for i in range(len(chunks))]

    collection.add(
        documents=chunks,
        ids=ids,
    )

    return collection


def retrieve_chunks(collection, question: str, top_k: int = 3) -> list[str]:
    """
    从 Chroma 中检索与问题最相关的 chunk。
    """
    results = collection.query(
        query_texts=[question],
        n_results=top_k,
    )

    return results["documents"][0]