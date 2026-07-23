# RAG documentaire offline

Application RAG locale développée avec **Python**, **Streamlit**, **Ollama**, **FAISS** et des modèles locaux.

## Objectif

Ce projet permet d’interroger un corpus documentaire local sans connexion Internet, avec :
- indexation des documents,
- recherche sémantique,
- réponse générée par un LLM local,
- affichage des passages sources retrouvés,
- mesure des temps de traitement.

## Modèles utilisés

- Modèle de génération : `llama3.2:3b`
- Modèle d'embeddings : `nomic-embed-text`

`llama3.2:3b` a été retenu car il donne une latence plus acceptable que Mistral sur le matériel de test.

## Arborescence

```text
rag_offline_app/
├── app.py
├── ingest.py
├── retriever.py
├── data/
├── index_store/
└── requirements.txt
```

## Prérequis

- Python 3.10+.
- Ollama installé en local.
- Les modèles suivants disponibles dans Ollama :
  - `llama3.2:3b`
  - `nomic-embed-text`

Si besoin :

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

## Installation

Créer et activer un environnement virtuel :

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

## Lancement

Démarrer l’application Streamlit :

```bash
streamlit run app.py
```

## Utilisation

1. Déposer un ou plusieurs documents dans le dossier `data/`, ou les importer via l’interface.
2. Cliquer sur **Lancer l’indexation**.
3. Poser une question en français.
4. Lire la réponse générée, les passages sources et les temps de traitement.

## Formats supportés

- PDF
- DOCX
- TXT
- MD
- CSV
- XLSX

## Fonctionnement

### 1. Indexation
Les documents sont :
- chargés depuis `data/`,
- découpés en chunks,
- transformés en embeddings avec `nomic-embed-text`,
- stockés dans une base vectorielle FAISS.

### 2. Question / réponse
Quand l’utilisateur pose une question :
- la question est transformée en embedding,
- les chunks les plus pertinents sont récupérés,
- le contexte est envoyé à `llama3.2:3b`,
- la réponse est affichée avec les sources et les temps mesurés.

## Mesure des performances

L’application affiche :
- le temps de récupération des chunks,
- le temps d’appel au modèle,
- le temps total.

Dans les tests réalisés, la récupération était rapide et la génération représentait l’essentiel de la latence.

## Structure technique

- `app.py` : interface Streamlit.
- `ingest.py` : chargement et indexation des documents.
- `retriever.py` : recherche sémantique et génération.
- `index_store/` : stockage local de l’index FAISS.
- `data/` : corpus documentaire.

## Remarques

- `accept_multiple_files=True` dans Streamlit permet d’envoyer plusieurs fichiers d’un coup .
- `Document` doit être importé depuis `langchain_core.documents`.
- Le chargement local de FAISS nécessite `allow_dangerous_deserialization=True` lorsque tu relis ton propre index.

## Dépannage

### Erreur `ModuleNotFoundError: No module named 'docx2txt'`
Installe la dépendance :

```bash
pip install docx2txt
```

### Latence trop élevée
Si la réponse est trop lente :
- baisse `top_k`,
- réduis la taille du prompt,
- teste un modèle encore plus léger,
- vérifie si Ollama utilise bien le GPU.

## Évolution possible

- bouton de réindexation incrémentale,
- meilleure gestion des citations page par page,
- ajout d’un reranker,
- journalisation des requêtes,
- mode streaming de la réponse,
- Dockerisation du projet.
