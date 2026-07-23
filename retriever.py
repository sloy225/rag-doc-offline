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


@st.cache_resource(show_spinner=False)
def get_vectorstore(embed_model: str):

    return load_vectorstore(embed_model)


def search_documents(
    question: str,
    embed_model: str,
    k: int = 4,
):

    vs = get_vectorstore(embed_model)

    if vs is None:
        return [], 0.0

    start = time.perf_counter()

    docs = vs.similarity_search(
        question,
        k=k,
    )

    end = time.perf_counter()

    return docs, end - start


def generate_answer(
    question: str,
    docs,
    llm_model: str,
    memory: str = "",
):

    context = "\n\n".join(
        [
            f"[Source : {d.metadata.get('source','?')} | page : {d.metadata.get('page','-')}]\n{d.page_content}"
            for d in docs
        ]
    )

    prompt = f"""
Tu es un assistant documentaire.

Tu dois répondre UNIQUEMENT à partir des documents.

Si l'information n'existe pas,
réponds :

"Je n'ai pas trouvé cette information dans le corpus documentaire."

Historique :

{memory}

Question :

{question}

Contexte :

{context}

A la fin,
ajoute les sources utilisées.
"""

    start = time.perf_counter()

    llm = ChatOllama(
        model=llm_model,
        temperature=0,
    )

    response = llm.invoke(prompt)

    end = time.perf_counter()

    return response.content, end - start


def answer_question(
    question: str,
    llm_model: str,
    embed_model: str,
    k: int = 4,
    memory: str = "",
):

    docs, retrieval_time = search_documents(
        question,
        embed_model,
        k,
    )

    if not docs:
        return None, [], retrieval_time, 0.0

    answer, llm_time = generate_answer(
        question,
        docs,
        llm_model,
        memory,
    )

    return (
        answer,
        docs,
        retrieval_time,
        llm_time,
    )