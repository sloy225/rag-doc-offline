from __future__ import annotations

import time
from pathlib import Path

import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama, OllamaEmbeddings

BASE_DIR = Path(__file__).parent
INDEX_DIR = BASE_DIR / "index_store"


def load_vectorstore(embed_model: str):
    index_file = INDEX_DIR / "index.faiss"
    if not index_file.exists():
        return None

    embeddings = OllamaEmbeddings(model=embed_model)
    return FAISS.load_local(
        str(INDEX_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )


@st.cache_resource
def get_vectorstore(embed_model: str):
    return load_vectorstore(embed_model)


def answer_question(question: str, llm_model: str, embed_model: str, k: int = 4):
    vs = get_vectorstore(embed_model)
    if vs is None:
        return None, [], 0.0, 0.0

    retrieve_start = time.perf_counter()
    docs = vs.similarity_search(question, k=k)
    retrieve_end = time.perf_counter()

    context = "\n\n".join(
        [
            f"[Source: {d.metadata.get('source', 'inconnu')}, page: {d.metadata.get('page', 'n/a')}]\n{d.page_content}"
            for d in docs
        ]
    )

    llm_start = time.perf_counter()
    prompt = f"""
Tu es un assistant documentaire local.
Réponds uniquement à partir du contexte fourni.
Si l'information n'est pas présente, dis-le clairement.
Réponse en français.
Cite les sources à la fin sous la forme : Sources: fichier (page x).

Question:
{question}

Contexte:
{context}
"""
    llm = ChatOllama(model=llm_model, temperature=0)
    response = llm.invoke(prompt)
    llm_end = time.perf_counter()

    retrieval_time = retrieve_end - retrieve_start
    llm_time = llm_end - llm_start

    return response.content, docs, retrieval_time, llm_time