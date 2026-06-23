from __future__ import annotations

import time

import pandas as pd
import streamlit as st

from ingest import DATA_DIR, ensure_dirs, list_supported_files, build_vectorstore, load_metadata
from retriever import answer_question

st.set_page_config(page_title="RAG documentaire offline", page_icon="📚", layout="wide")
ensure_dirs()

st.title("📚 RAG documentaire offline")
st.caption("Python + Streamlit + Ollama + FAISS")

with st.sidebar:
    st.header("Configuration")
    llm_model = st.text_input("Modèle de génération Ollama", value="mistral:latest")
    embed_model = st.text_input("Modèle d'embeddings Ollama", value="nomic-embed-text")
    top_k = st.slider("Nombre de passages retrouvés", 1, 8, 4)

st.subheader("1. Déposer des documents")
uploaded_files = st.file_uploader(
    "Ajoute des documents (PDF, DOCX, TXT, MD, CSV, XLSX)",
    type=["pdf", "docx", "txt", "md", "csv", "xlsx"],
    accept_multiple_files=True,
)

if uploaded_files:
    for file in uploaded_files:
        target = DATA_DIR / file.name
        target.write_bytes(file.getbuffer())
    st.success(f"{len(uploaded_files)} fichier(s) enregistré(s) dans le corpus local.")

files = list_supported_files()
if files:
    st.write("### Corpus local")
    st.dataframe(
        pd.DataFrame(
            [{"fichier": f.name, "taille_ko": round(f.stat().st_size / 1024, 1)} for f in files]
        ),
        use_container_width=True,
    )
else:
    st.info("Aucun document dans le dossier data/ pour le moment.")

st.subheader("2. Indexer le corpus")
if st.button("Lancer l'indexation", type="primary"):
    with st.spinner("Indexation en cours..."):
        total_chunks, file_infos = build_vectorstore(embed_model)

    if total_chunks == 0:
        st.warning("Aucun document exploitable trouvé.")
    else:
        st.success(f"Index créé avec {total_chunks} chunks.")
        st.dataframe(pd.DataFrame(file_infos), use_container_width=True)

meta = load_metadata()
if meta:
    st.json(meta)

st.subheader("3. Poser une question")
question = st.text_area(
    "Question utilisateur",
    placeholder="Posez une question sur le corpus indexé...",
)

if st.button("Interroger le corpus"):
    if not question.strip():
        st.warning("Saisis une question.")
    else:
        with st.spinner("Recherche + génération en cours..."):
            answer, source_docs, retrieval_time, llm_time = answer_question(
                question, llm_model, embed_model, k=top_k
            )

        if answer is None:
            st.error("Aucun index trouvé. Lance d'abord l'indexation.")
        else:
            total_time = retrieval_time + llm_time

            col1, col2, col3 = st.columns(3)
            col1.metric("Récupération chunks", f"{retrieval_time:.2f} s")
            col2.metric("Appel Ollama", f"{llm_time:.2f} s")
            col3.metric("Temps total", f"{total_time:.2f} s")

            st.markdown("### Réponse")
            st.write(answer)

            st.markdown("### Passages retrouvés")
            for i, doc in enumerate(source_docs, start=1):
                with st.expander(f"Source {i} — {doc.metadata.get('source', 'inconnu')}"):
                    st.write(doc.page_content)
                    st.caption(doc.metadata)