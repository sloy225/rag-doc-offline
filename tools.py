from ingest import (
    list_supported_files,
    build_vectorstore,
    load_metadata,
)

from retriever import answer_question


def rag_search(question, llm_model, embed_model, top_k):
    return answer_question(
        question,
        llm_model,
        embed_model,
        k=top_k,
    )


def list_documents():

    files = list_supported_files()

    return [f.name for f in files]


def corpus_information():

    return load_metadata()


def rebuild_index(embed_model):

    return build_vectorstore(embed_model)