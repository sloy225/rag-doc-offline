
# 📚 RAG documentaire offline agentique

Application RAG locale développee avec **Python**, **Streamlit**, **Ollama**, **FAISS** et des modèles locaux.

Cette version fait évoluer un RAG documentaire classique vers un **assistant documentaire agentique** capable de choisir automatiquement l'action à effectuer selon la demande de l'utilisateur.

---

## 🎯 Objectif

Ce projet permet d'interroger un **corpus documentaire local** sans connexion Internet, avec :

- ✅ Indexation des documents
- ✅ Recherche sémantique
- ✅ Génération de réponses avec un LLM local
- ✅ Affichage des passages sources
- ✅ Mesure des performances
- ✅ Prise de décision via un agent
- ✅ Mémoire conversationnelle pour conserver le contexte des échanges

---

## 🚀 Fonctionnalités

### Recherche documentaire (RAG)

L'utilisateur peut poser une question sur le contenu des documents. Le système :

1. Recherche les passages les plus pertinents dans FAISS
2. Construit un contexte documentaire
3. Interroge un modèle Ollama
4. Génère une réponse en franÃ§ais avec les sources

### Agent documentaire

Une couche agentique a été ajoutée au-dessus du RAG. Avant d'exécuter une action, un **router décisionnel** analyse la question et choisit automatiquement le bon outil.

**Actions disponibles :**

| Action | Description |
|--------|-------------|
| **RAG** | Répondre à une question documentaire |
| **Liste des documents** | Afficher les fichiers présents dans le corpus |
| **Réindexation** | Reconstruire l'index FAISS après l'ajout de nouveaux documents |
| **Métadonnées** | Consulter les informations de l'index (nombre de documents, chunks, modèle d'embeddings...) |

> Cette première version utilise un **router basé sur des règles** (mots-clés), facilement extensible vers un routeur piloté par un LLM.

### Mémoire conversationnelle

L'application conserve l'historique récent de la conversation. Cette mémoire permet :

- De garder le contexte des échanges
- De faciliter les questions de suivi
- De rendre l'interaction plus naturelle

**Exemple :**

```
Utilisateur : Qui est le responsable informatique ?
Assistant   : Jean Dupont est le responsable informatique.
Utilisateur : Quel est son email ?
```

Grâce à la mémoire, l'agent comprend que *"son"* fait référence à *Jean Dupont*.

---

## 🏗️ Architecture

```
                 Streamlit
                     │
                     ▼
            Agent documentaire
                     │
              Router décisionnel
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
       RAG    Gestion du corpus   Métadonnées
        │
        ▼
      FAISS
        │
        ▼
  Ollama (LLM local)
```

---

## 🤖 Modèles utilisés

| Type | Modèle |
|------|--------|
| **Génération** | `llama3.2:3b` |
| **Embeddings** | `nomic-embed-text` |

Le modèle `llama3.2:3b` a été retenu pour offrir un bon compromis entre qualité des réponses et temps de génération sur la machine de test.

---

## 📁 Arborescence

```
rag_offline_app/
├── app.py              # Interface Streamlit
├── ingest.py           # Chargement et indexation des documents
├── retriever.py        # Recherche sémantique et génération
├── agent.py            # Orchestration des actions
├── router.py           # Décision de l'action à exécuter
├── tools.py            # Outils de l'agent
├── memory.py           # Gestion de la mémoire conversationnelle
├── database.py         # Historique des interactions (SQLite)
├── data/               # Corpus documentaire
├── index_store/        # Stockage local de l'index FAISS
├── rag_history.db      # Base de données (ignorée par Git)
└── requirements.txt    # Dépendances Python
```

---

## 📋 Prérequis

- Python 3.10+
- Ollama installé localement

**Modèles Ollama nécessaires :**

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

---

## 🔧 Installation

### 1. Créer un environnement virtuel

**Windows :**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS :**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## ▶️ Lancement

```bash
streamlit run app.py
```

---

## 📖 Utilisation

1. **Déposer** un ou plusieurs documents dans le dossier `data/` ou via l'interface
2. **Cliquer** sur *Lancer l'indexation*
3. **Poser** une question
4. L'agent **détermine automatiquement** l'action à exécuter
5. **Consulter** la réponse, les sources et les indicateurs de performance

---

## 📄 Formats supportés

- PDF
- DOCX
- TXT
- MD
- CSV
- XLSX
- DOC
- PPT
- PPTX
- ODT
- ODS
- ODP

---

## ⚙️ Fonctionnement

### 1. Indexation

Les documents sont :

1. Chargés depuis le dossier `data/`
2. Découpés en chunks
3. Transformés en embeddings avec `nomic-embed-text`
4. Enregistrés dans une base vectorielle FAISS

### 2. Décision de l'agent

Avant toute recherche, le router analyse la demande utilisateur.

| Question | Action |
|----------|--------|
| *"Quelle est la procédure RH ?"* | RAG |
| *"Quels documents sont disponibles ?"* | Liste du corpus |
| *"Réindexe les nouveaux documents."* | Réindexation |
| *"Combien de documents sont indexés ?"* | Métadonnées |

### 3. Recherche documentaire

Lorsque l'action choisie est **RAG** :

1. La question est transformée en embedding
2. FAISS récupère les chunks les plus pertinents
3. Le contexte est envoyé à `llama3.2:3b`
4. Le modèle génère une réponse sourcée

---

## 📊 Mesure des performances

L'application affiche :

- ⏱️ Temps de recherche dans FAISS
- ⏱️ Temps d'appel au LLM
- ⏱️ Temps total de traitement

> Dans les essais réalisés, la recherche vectorielle reste très rapide tandis que la génération de la réponse constitue la principale source de latence.

---

## 🧱 Structure technique

| Fichier | Rôle |
|---------|------|
| `app.py` | Interface Streamlit |
| `agent.py` | Orchestration des actions |
| `router.py` | Décision de l'action à exécuter |
| `memory.py` | Gestion de la mémoire conversationnelle |
| `tools.py` | Outils de l'agent |
| `ingest.py` | Chargement et indexation des documents |
| `retriever.py` | Recherche sémantique et génération |
| `database.py` | Historique des interactions (SQLite) |
| `data/` | Corpus documentaire |
| `index_store/` | Stockage local de l'index FAISS |

---

## 🛠️ Technologies utilisées

- Python
- Streamlit
- Ollama
- FAISS
- LangChain
- LangChain Community
- LangChain Ollama
- SQLite

---

## 🔧 Dépannage

### Erreur : `ModuleNotFoundError: No module named 'docx2txt'`

```bash
pip install docx2txt
```

### Temps de réponse élevé

Pour réduire la latence :

- Diminuer la valeur de `top_k`
- Réduire la taille du contexte envoyé au modèle
- Utiliser un modèle plus léger
- Vérifier que le GPU est correctement utilisé par Ollama

---

## 🚀 évolutions possibles

- [ ] Routeur basé sur un LLM
- [ ] Comparaison automatique de documents
- [ ] Résumé de documents
- [ ] Reranker
- [ ] Mémoire persistante
- [ ] Historique des utilisateurs et des requÃªtes
- [ ] Journalisation avancée dans SQLite
- [ ] Mode streaming des réponses
- [ ] Dockerisation
- [ ] Orchestration avec LangGraph

---
