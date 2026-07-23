from router import detect_action

from tools import (
    rag_search,
    list_documents,
    corpus_information,
    rebuild_index,
)

from memory import ConversationMemory


class DocumentAgent:

    def __init__(self):

        self.memory = ConversationMemory()

    def run(
        self,
        question,
        llm_model,
        embed_model,
        top_k,
    ):

        self.memory.add_user(question)

        action = detect_action(question)

        if action == "list":

            docs = list_documents()

            answer = "Documents disponibles :\n\n"

            answer += "\n".join(docs)

            self.memory.add_assistant(answer)

            return {
                "answer": answer,
                "docs": [],
                "retrieval": 0,
                "llm": 0,
            }

        if action == "metadata":

            meta = corpus_information()

            answer = str(meta)

            self.memory.add_assistant(answer)

            return {
                "answer": answer,
                "docs": [],
                "retrieval": 0,
                "llm": 0,
            }

        if action == "reindex":

            nb_chunks, infos = rebuild_index(embed_model)

            answer = (
                f"Index reconstruit.\n\n"
                f"Nombre de chunks : {nb_chunks}"
            )

            self.memory.add_assistant(answer)

            return {
                "answer": answer,
                "docs": [],
                "retrieval": 0,
                "llm": 0,
            }

        answer, docs, retrieval, llm = rag_search(
            question,
            llm_model,
            embed_model,
            top_k,
        )

        self.memory.add_assistant(answer)

        return {
            "answer": answer,
            "docs": docs,
            "retrieval": retrieval,
            "llm": llm,
        }