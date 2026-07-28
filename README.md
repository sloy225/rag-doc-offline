# RAG documentaire offline agentique

Application **RAG locale** développée avec **Python**, **Streamlit**, **Ollama**, **FAISS** et des modèles locaux.

Cette version fait évoluer un RAG documentaire classique vers un **assistant documentaire agentique** capable de choisir automatiquement l'action à effectuer selon la demande de l'utilisateur.

---

# Objectif

Ce projet permet d'interroger un corpus documentaire local **sans connexion Internet**, avec :

* indexation des documents ;
* recherche sémantique ;
* génération de réponses avec un LLM local ;
* affichage des passages sources ;
* mesure des performances ;
* **prise de décision via un agent** ;
* **mémoire conversationnelle** pour conserver le contexte des échanges.

---

# Fonctionnalités

## Recherche documentaire (RAG)

L'utilisateur peut poser une question sur le contenu des documents.

Le système :

* recherche les passages les plus pertinents dans FAISS ;
* construit un contexte documentaire ;
* interroge un modèle Ollama ;
* génère une réponse en français avec les sources.

---

## Agent documentaire

Une couche agentique a été ajoutée au-dessus du RAG.

Avant d'exécuter une action, un **router décisionnel** analyse la question et choisit automatiquement le bon outil.

Les actions actuellement disponibles sont :

* **RAG** : répondre à une question documentaire ;
* **Liste des documents** : afficher les fichiers présents dans le corpus ;
* **Réindexation** : reconstruire l'index FAISS après l'ajout de nouveaux documents ;
* **Métadonnées** : consulter les informations de l'index (nombre de documents, nombre de chunks, modèle d'embeddings utilisé...).

Cette première version utilise un **router basé sur des règles** (mots-clés), facilement extensible vers un routeur piloté par un LLM.

---

## Mémoire conversationnelle

L'application conserve l'historique récent de la conversation.

Cette mémoire permet :

* de garder le contexte des échanges ;
* de faciliter les questions de suivi ;
* de rendre l'interaction plus naturelle.

Exemple :

**Utilisateur**

> Qui est le responsable informatique ?

**Assistant**

> Jean Dupont est le responsable informatique.

**Utilisateur**

> Quel est son email ?

Grâce à la mémoire, l'agent comprend que **"son"** fait référence à **Jean Dupont**.

---

# Architecture

```text
                 Streamlit
                     |
                     v
            Agent documentaire
                     |
              Router décisionnel
                     |
      +--------------+--------------+
      |              |              |
      v              v              v
     RAG     Gestion du corpus   Métadonnées
      |
      v
     FAISS
      |
      v
 Ollama (LLM local)
```

---

# Modèles utilisés

* Modèle de génération : `llama3.2:3b`
* Modèle d'embeddings : `nomic-embed-text`

Le modèle `llama3.2:3b` a été retenu pour offrir un bon compromis entre qualité des réponses et temps de génération sur la machine de test.

---

# Arborescence

```text
rag_offline_app/
├── app.py
├── ingest.py
├── retriever.py
├── agent.py
├── router.py
├── tools.py
├── memory.py
├── data/
├── index_store/
└── requirements.txt
```

---

# Prérequis

* Python 3.10+
* Ollama installé localement

Modèles Ollama nécessaires :

* `llama3.2:3b`
* `nomic-embed-text`

Installation :

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

---

# Installation

Créer un environnement virtuel.

## Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

## Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

---

# Lancement

```bash
streamlit run app.py
```

---

# Utilisation

1. Déposer un ou plusieurs documents dans le dossier `data/` ou via l'interface.
2. Cliquer sur **Lancer l'indexation**.
3. Poser une question.
4. L'agent détermine automatiquement l'action à exécuter.
5. Consulter la réponse, les sources et les indicateurs de performance.

---

# Formats supportés

* PDF
* DOCX
* TXT
* MD
* CSV
* XLSX

---

# Fonctionnement

## 1. Indexation

Les documents sont :

* chargés depuis le dossier `data/` ;
* découpés en chunks ;
* transformés en embeddings avec `nomic-embed-text` ;
* enregistrés dans une base vectorielle FAISS.

---

## 2. Décision de l'agent

Avant toute recherche, le router analyse la demande utilisateur.

Exemples :

| Question                              | Action          |
| ------------------------------------- | --------------- |
| "Quelle est la procédure RH ?"        | RAG             |
| "Quels documents sont disponibles ?"  | Liste du corpus |
| "Réindexe les nouveaux documents."    | Réindexation    |
| "Combien de documents sont indexés ?" | Métadonnées     |

---

## 3. Recherche documentaire

Lorsque l'action choisie est **RAG** :

1. la question est transformée en embedding ;
2. FAISS récupère les chunks les plus pertinents ;
3. le contexte est envoyé à `llama3.2:3b` ;
4. le modèle génère une réponse sourcée.

---

# Mesure des performances

L'application affiche :

* temps de recherche dans FAISS ;
* temps d'appel au LLM ;
* temps total de traitement.

Dans les essais réalisés, la recherche vectorielle reste très rapide tandis que la génération de la réponse constitue la principale source de latence.

---

# Structure technique

| Fichier        | Rôle                                    |
| -------------- | --------------------------------------- |
| `app.py`       | Interface Streamlit                     |
| `agent.py`     | Orchestration des actions               |
| `router.py`    | Décision de l'action à exécuter         |
| `memory.py`    | Gestion de la mémoire conversationnelle |
| `tools.py`     | Outils de l'agent                       |
| `ingest.py`    | Chargement et indexation des documents  |
| `retriever.py` | Recherche sémantique et génération      |
| `data/`        | Corpus documentaire                     |
| `index_store/` | Stockage local de l'index FAISS         |

---

# Technologies utilisées

* Python
* Streamlit
* Ollama
* FAISS
* LangChain
* LangChain Community
* LangChain Ollama

---

# Dépannage

## Erreur

```text
ModuleNotFoundError: No module named 'docx2txt'
```

Installer la dépendance :

```bash
pip install docx2txt
```

---

## Temps de réponse élevé

Pour réduire la latence :

* diminuer la valeur de `top_k` ;
* réduire la taille du contexte envoyé au modèle ;
* utiliser un modèle plus léger ;
* vérifier que le GPU est correctement utilisé par Ollama.

---

# Évolutions possibles

* routeur basé sur un LLM ;
* comparaison automatique de documents ;
* résumé de documents ;
* reranker ;
* mémoire persistante ;
* historique des utilisateurs et des requêtes ;
* journalisation dans SQLite ;
* mode streaming des réponses ;
* Dockerisation ;
* orchestration avec LangGraph.
