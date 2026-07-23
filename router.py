from __future__ import annotations


def detect_action(question: str) -> str:

    q = question.lower().strip()


    # -----------------------------
    # Réindexation
    # -----------------------------
    reindex_keywords = [
        "réindex",
        "réindexer",
        "reconstruire l'index",
        "mettre à jour l'index",
        "actualiser la base",
        "indexe",
    ]

    for word in reindex_keywords:

        if word in q:
            return "reindex"


    # -----------------------------
    # Liste documents
    # -----------------------------
    list_keywords = [
        "liste",
        "documents disponibles",
        "fichiers disponibles",
        "quels documents",
        "quels fichiers",
        "voir les documents",
        "afficher les fichiers",
    ]


    for word in list_keywords:

        if word in q:
            return "list"


    # -----------------------------
    # Métadonnées
    # -----------------------------
    metadata_keywords = [
        "métadonnées",
        "information index",
        "statistiques",
        "nombre de documents",
        "nombre de chunks",
    ]


    for word in metadata_keywords:

        if word in q:
            return "metadata"


    # -----------------------------
    # Par défaut
    # -----------------------------
    return "rag"