from __future__ import annotations

from database import (
    init_db,
    save_history,
    load_history,
)

import csv
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from ingest import (
    DATA_DIR,
    ensure_dirs,
    list_supported_files,
    build_vectorstore,
    load_metadata,
)

# <<< nouveau >>>
from agent import DocumentAgent

# -----------------------------
# Configuration Streamlit
# -----------------------------
st.set_page_config(
    page_title="RAG documentaire offline",
    page_icon="📚",
    layout="wide",
)

ensure_dirs()
init_db()

# Chemin du fichier de log CSV
LOG_FILE = DATA_DIR / "interactions.csv"

# -----------------------------
# Initialisation Agent
# -----------------------------
if "agent" not in st.session_state:
    st.session_state.agent = DocumentAgent()

# -----------------------------
# Interface
# -----------------------------
st.title("📚 RAG documentaire agentique")

st.caption(
    "Python • Streamlit • Ollama • FAISS • Agent IA"
)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("Configuration")

    llm_model = st.text_input(
        "Modèle de génération",
        value="llama3.2:3b",
    )

    embed_model = st.text_input(
        "Modèle d'embeddings",
        value="nomic-embed-text",
    )

    top_k = st.slider(
        "Top K",
        1,
        8,
        4,
    )

    st.sidebar.subheader("Utilisateur")

    user_name = st.sidebar.text_input(
        "Nom d'utilisateur",
        value="Invité",
    )

# -----------------------------
# Upload
# -----------------------------
st.subheader("1. Déposer des documents")

uploaded_files = st.file_uploader(
    "Ajoute des documents",
    type=[
        "pdf",
        "docx",
        "txt",
        "md",
        "csv",
        "xlsx",
        "doc",
        "xls",
        "ppt",
        "pptx",
        "odt",
        "ods",
        "odp",
    ],
    accept_multiple_files=True,
)

if uploaded_files:
    for file in uploaded_files:
        target = DATA_DIR / file.name
        target.write_bytes(file.getbuffer())
    st.success(f"{len(uploaded_files)} fichier(s) ajouté(s).")

# -----------------------------
# Corpus
# -----------------------------
files = list_supported_files()

if files:
    st.subheader("Corpus documentaire")
    df = pd.DataFrame(
        [
            {
                "Nom": f.name,
                "Taille (Ko)": round(f.stat().st_size / 1024, 1),
            }
            for f in files
        ]
    )
    st.dataframe(df, use_container_width=True)
else:
    st.info("Aucun document disponible.")

# -----------------------------
# Indexation
# -----------------------------
st.subheader("2. Indexer le corpus")

if st.button("Lancer l'indexation", type="primary"):
    with st.spinner("Indexation..."):
        total_chunks, infos = build_vectorstore(embed_model)

    if total_chunks == 0:
        st.warning("Aucun document exploitable.")
    else:
        st.success(f"Index créé ({total_chunks} chunks).")
        st.dataframe(pd.DataFrame(infos), use_container_width=True)

meta = load_metadata()
if meta:
    with st.expander("Métadonnées de l'index"):
        st.json(meta)

# -----------------------------
# Questions utilisateur
# -----------------------------
st.subheader("3. Assistant documentaire agentique")

question = st.text_area(
    "Question utilisateur",
    placeholder=(
        "Exemples :\n"
        "- Quelle est la procédure RH ?\n"
        "- Liste les documents disponibles.\n"
        "- Réindexe le corpus."
    ),
)

if st.button("Interroger l'agent"):
    if not question.strip():
        st.warning("Saisis une question.")
    else:
        with st.spinner("L'agent analyse la demande..."):
            result = st.session_state.agent.run(
                question=question,
                llm_model=llm_model,
                embed_model=embed_model,
                top_k=top_k,
            )

        # -----------------------------
        # Vérification résultat
        # -----------------------------
        if result is None:
            st.error("Impossible d'exécuter la demande.")
        else:
            answer = result["answer"]
            source_docs = result.get("docs", [])
            retrieval_time = result.get("retrieval", 0)
            llm_time = result.get("llm", 0)
            total_time = retrieval_time + llm_time

            # -----------------------------
            # Affichage action agent
            # -----------------------------
            st.markdown("### Décision de l'agent")

            action = result.get("action", "rag")

            if action == "rag":
                st.info("🔎 Recherche documentaire FAISS + génération LLM")
            elif action == "list":
                st.info("📂 Consultation du corpus local")
            elif action == "reindex":
                st.info("🔄 Reconstruction de l'index FAISS")
            elif action == "metadata":
                st.info("📊 Consultation des métadonnées")

            # -----------------------------
            # Log CSV
            # -----------------------------
            source_names = "; ".join(
                [
                    doc.metadata.get("source", "inconnu")
                    for doc in source_docs
                ]
            )

            with open(
                LOG_FILE,
                "a",
                newline="",
                encoding="utf-8",
            ) as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        datetime.now().isoformat(),
                        user_name,
                        question,
                        action,
                        round(retrieval_time, 3),
                        round(llm_time, 3),
                        round(total_time, 3),
                        len(source_docs),
                        source_names,
                        llm_model,
                        embed_model,
                        top_k,
                    ]
                )

            # -----------------------------
            # Sauvegarde dans la DB
            # -----------------------------
            save_history(
                user_name=user_name,
                question=question,
                action=action,
                answer=answer,
                sources=source_names,
                retrieval_time=retrieval_time,
                llm_time=llm_time,
                total_time=total_time,
            )

            # -----------------------------
            # KPI performances
            # -----------------------------
            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Recherche FAISS",
                f"{retrieval_time:.2f} s",
            )

            col2.metric(
                "Génération Ollama",
                f"{llm_time:.2f} s",
            )

            col3.metric(
                "Temps total",
                f"{total_time:.2f} s",
            )

            # -----------------------------
            # Réponse finale
            # -----------------------------
            st.markdown("### Réponse de l'agent")
            st.write(answer)

            # -----------------------------
            # Sources utilisées
            # -----------------------------
            if source_docs:
                st.markdown("### Sources retrouvées")

                for i, doc in enumerate(source_docs, start=1):
                    source_name = doc.metadata.get("source", "inconnu")
                    with st.expander(f"Source {i} — {source_name}"):
                        st.write(doc.page_content)
                        st.caption(doc.metadata)

# -----------------------------
# Historique conversation
# -----------------------------
st.sidebar.divider()
st.sidebar.subheader("Mémoire conversationnelle")

if hasattr(st.session_state.agent, "memory"):
    history = st.session_state.agent.memory.get_context()
    if history:
        st.sidebar.text(history)
    else:
        st.sidebar.info("Aucune conversation.")

st.divider()
st.subheader("Historique des interactions")

history = load_history()
if history:
    df = pd.DataFrame(
        history,
        columns=[
            "Date",
            "Utilisateur",
            "Question",
            "Action",
            "Temps (s)",
        ],
    )
    st.dataframe(df, use_container_width=True)
else:
    st.info("Aucune interaction enregistrée.")