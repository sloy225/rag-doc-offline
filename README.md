# 📚 RAG documentaire offline agentique

Application locale de **Retrieval-Augmented Generation (RAG)** développée avec **Python**, **Streamlit**, **Ollama**, **FAISS** et des modèles exécutés localement.

Le projet fait évoluer un RAG documentaire classique vers un **assistant documentaire agentique**. Celui-ci analyse la demande de l’utilisateur et sélectionne automatiquement l’action la plus adaptée : recherche dans les documents, consultation du corpus, réindexation ou affichage des métadonnées.

> L’application est conçue pour fonctionner localement, afin de limiter la dépendance à des services cloud et de préserver la confidentialité des documents manipulés.

---

## 🎯 Objectif

Cette application permet d’interroger un **corpus documentaire local** à travers une interface web simple, avec les capacités suivantes :

- ✅ Import et indexation de documents
- ✅ Recherche sémantique dans un corpus local
- ✅ Génération de réponses par un LLM local via Ollama
- ✅ Affichage des passages sources retrouvés
- ✅ Agent décisionnel pour router les demandes utilisateur
- ✅ Mémoire conversationnelle de court terme
- ✅ Historique persistant des interactions dans SQLite
- ✅ Journalisation des interactions au format CSV
- ✅ Mesure des performances du pipeline RAG
- ✅ Monitoring des ressources machine : CPU, RAM et espace disque

---

## 🚀 Fonctionnalités

### Recherche documentaire augmentée — RAG

L’utilisateur pose une question sur le contenu de ses documents. Le pipeline RAG :

1. Transforme la question en représentation vectorielle (*embedding*)
2. Recherche les passages les plus pertinents dans l’index FAISS
3. Construit un contexte documentaire à partir des résultats retrouvés
4. Envoie la question et le contexte au modèle de génération Ollama
5. Produit une réponse en français avec les sources associées

Cette approche réduit le risque de réponses non fondées, car le modèle s’appuie sur les passages extraits du corpus.

### Agent documentaire

Une couche agentique est placée au-dessus du pipeline RAG. Avant toute exécution, un **routeur décisionnel** analyse la demande de l’utilisateur et choisit l’outil approprié.

| Action | Description |
|---|---|
| **RAG** | Répond à une question à partir du contenu indexé |
| **Liste du corpus** | Affiche les documents disponibles dans le dossier `data/` |
| **Réindexation** | Reconstruit l’index FAISS après l’ajout ou la modification de documents |
| **Métadonnées** | Affiche les informations liées à l’index : documents, chunks et modèle d’embeddings |

> Cette première version repose sur un routeur basé sur des règles et des mots-clés. L’architecture est pensée pour permettre ultérieurement l’intégration d’un routeur piloté par LLM.

### Mémoire conversationnelle

L’application conserve l’historique récent de la conversation afin de maintenir le contexte des questions successives.

La mémoire permet notamment :

- De conserver le fil de l’échange
- De traiter plus naturellement les questions de suivi
- De résoudre certaines références contextuelles

**Exemple :**

```text
Utilisateur : Qui est le responsable informatique ?
Assistant   : Jean Dupont est le responsable informatique.
Utilisateur : Quel est son e-mail ?
```

Dans ce cas, la mémoire permet à l’agent d’interpréter « son e-mail » comme une référence à Jean Dupont.

### Historique et traçabilité

Chaque interaction est enregistrée dans :

- Une base SQLite pour consulter l’historique depuis l’interface
- Un fichier CSV pour faciliter l’analyse ultérieure des usages et performances

Les informations enregistrées incluent notamment :

- Date et heure de la requête
- Utilisateur
- Question posée
- Action sélectionnée par l’agent
- Temps de recherche FAISS
- Temps de génération Ollama
- Temps total de traitement
- Nombre et noms des documents sources
- Modèles utilisés
- Valeur de `top_k`

### Monitoring système

L’interface affiche dans la barre latérale les ressources de la machine utilisée :

- Utilisation processeur
- Utilisation de la mémoire vive
- Mémoire RAM disponible
- Utilisation du disque

Cela permet de suivre l’impact local du chargement, de l’indexation et de l’inférence des modèles Ollama.

---

## 🏗️ Architecture

```text
                         Streamlit
                             │
                             ▼
                  Agent documentaire
                             │
                     Routeur décisionnel
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
       RAG documentaire   Gestion corpus    Métadonnées
          │
          ▼
    Recherche vectorielle
          │
          ▼
        FAISS
          │
          ▼
  Ollama — LLM local / embeddings
          │
          ▼
 SQLite + CSV + mémoire conversationnelle
```

---

## 🤖 Modèles utilisés

| Usage | Modèle par défaut |
|---|---|
| Génération de réponses | `llama3.2:3b` |
| Création des embeddings | `nomic-embed-text` |

Le modèle `llama3.2:3b` offre un compromis adapté entre qualité de génération, consommation de ressources et temps de réponse pour une exécution locale.

Les modèles peuvent être modifiés directement dans l’interface Streamlit.

---

## 📁 Arborescence du projet

```text
rag-doc-offline/
├── app.py                 # Interface principale Streamlit
├── monitoring.py          # Collecte des métriques CPU, RAM et disque
├── ingest.py              # Chargement et indexation des documents
├── retriever.py           # Recherche vectorielle et génération RAG
├── agent.py               # Orchestration des actions de l'agent
├── router.py              # Sélection de l'action à exécuter
├── tools.py               # Outils disponibles pour l'agent
├── memory.py              # Mémoire conversationnelle
├── database.py            # Historique des interactions via SQLite
├── data/                  # Corpus documentaire et journal CSV
├── index_store/           # Stockage local de l'index FAISS
├── rag_history.db         # Base SQLite locale, ignorée par Git
├── requirements.txt       # Dépendances Python
└── README.md              # Documentation du projet
```

---

## 📋 Prérequis

- Python 3.10 ou version supérieure
- [Ollama](https://ollama.com/) installé et fonctionnel localement
- Git, facultatif mais recommandé pour cloner et versionner le projet

### Modèles Ollama requis

Télécharge les modèles nécessaires avant de lancer l’application :

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

Vérifie les modèles disponibles :

```bash
ollama list
```

---

## 🔧 Installation

### 1. Cloner le dépôt

```bash
git clone [https://github.com/sloy225/rag-doc-offline.git](https://github.com/sloy225/rag-doc-offline.git)
cd rag-doc-offline
```

### 2. Créer un environnement virtuel

**Windows — PowerShell :**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows — Invite de commandes :**

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux / macOS :**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## ▶️ Lancement

Démarre d’abord le service Ollama si nécessaire :

```bash
ollama serve
```

Puis, dans un second terminal avec l’environnement virtuel activé :

```bash
streamlit run app.py
```

Streamlit ouvre généralement l’interface dans le navigateur à l’adresse :

```text
http://localhost:8501
```

---

## 📖 Utilisation

1. Lance l’application Streamlit
2. Dépose un ou plusieurs documents via l’interface, ou ajoute-les dans `data/`
3. Clique sur **Lancer l’indexation**
4. Sélectionne, si nécessaire, le modèle LLM, le modèle d’embeddings et la valeur `top_k`
5. Pose une question dans la zone prévue
6. Clique sur **Interroger l’agent**
7. Consulte :
   - La décision prise par l’agent
   - La réponse générée
   - Les passages sources retrouvés
   - Les indicateurs de performance
   - L’historique des interactions

> Après l’ajout, la suppression ou la modification d’un document, relance l’indexation pour mettre à jour FAISS.

---

## 📄 Formats pris en charge

| Famille | Extensions |
|---|---|
| Documents texte | `.txt`, `.md` |
| Documents bureautiques | `.doc`, `.docx`, `.odt` |
| Feuilles de calcul | `.csv`, `.xls`, `.xlsx`, `.ods` |
| Présentations | `.ppt`, `.pptx`, `.odp` |
| Documents PDF | `.pdf` |

La qualité d’extraction dépend du format et de la structure du fichier. Les PDF scannés sans couche de texte nécessitent généralement une étape OCR, qui n’est pas incluse par défaut dans cette version.

---

## ⚙️ Fonctionnement détaillé

### 1. Indexation du corpus

Lors de l’indexation, l’application :

1. Charge les fichiers présents dans `data/`
2. Extrait leur contenu textuel
3. Découpe le contenu en fragments ou *chunks*
4. Génère les embeddings avec `nomic-embed-text`
5. Stocke les vecteurs et les métadonnées dans FAISS
6. Enregistre les informations d’indexation

### 2. Décision de l’agent

Avant toute recherche, le routeur examine la question de l’utilisateur.

| Exemple de demande | Action attendue |
|---|---|
| « Quelle est la procédure RH ? » | RAG |
| « Quels documents sont disponibles ? » | Liste du corpus |
| « Réindexe les nouveaux documents. » | Réindexation |
| « Combien de documents sont indexés ? » | Métadonnées |

### 3. Génération d’une réponse RAG

Pour une demande documentaire :

1. La question est vectorisée
2. FAISS sélectionne les `top_k` passages les plus proches
3. Les passages sont injectés dans le contexte du prompt
4. Ollama génère une réponse fondée sur ce contexte
5. L’interface affiche les extraits de documents utilisés

---

## 📊 Indicateurs de performance

Pour chaque requête, l’interface présente :

| Indicateur | Description |
|---|---|
| Recherche FAISS | Temps consacré à la récupération des passages pertinents |
| Génération Ollama | Temps d’inférence du modèle de langage |
| Temps total | Temps cumulé de traitement de la requête |

En pratique, la recherche vectorielle reste généralement rapide ; la génération par le LLM local est souvent la principale source de latence. Les performances dépendent principalement du modèle sélectionné, de la configuration CPU/GPU, de la mémoire disponible, de `top_k` et de la longueur du contexte.

---

## 🧱 Responsabilités des modules

| Fichier / dossier | Rôle |
|---|---|
| `app.py` | Interface utilisateur et orchestration de l’expérience Streamlit |
| `monitoring.py` | Collecte des métriques CPU, RAM et disque |
| `agent.py` | Orchestration globale et exécution de l’action sélectionnée |
| `router.py` | Routage de la requête vers l’action appropriée |
| `tools.py` | Implémentation des outils manipulés par l’agent |
| `memory.py` | Conservation du contexte conversationnel récent |
| `ingest.py` | Chargement, découpage et indexation des documents |
| `retriever.py` | Recherche sémantique FAISS et génération RAG |
| `database.py` | Persistance de l’historique dans SQLite |
| `data/` | Documents importés et fichier de journalisation CSV |
| `index_store/` | Index vectoriel FAISS et métadonnées associées |

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
- Pandas
- psutil

---

## 🔧 Dépannage

### Erreur : `ModuleNotFoundError: No module named 'docx2txt'`

Installe le module manquant dans l’environnement virtuel actif :

```bash
pip install docx2txt
```

Puis ajoute-le également au fichier `requirements.txt` afin que l’installation du projet reste reproductible :

```text
docx2txt
```

### Erreur : Ollama n’est pas accessible

Vérifie qu’Ollama est installé :

```bash
ollama --version
```

Puis démarre le service :

```bash
ollama serve
```

Dans un autre terminal, vérifie que les modèles sont disponibles :

```bash
ollama list
```

### Temps de réponse élevé

Pour réduire la latence :

- Diminue la valeur de `top_k`
- Utilise un modèle de génération plus léger
- Réduis la taille des chunks ou du contexte transmis au LLM
- Vérifie l’utilisation CPU, RAM et disque dans la barre latérale
- Vérifie que l’accélération GPU est correctement prise en charge par Ollama
- Ferme les applications consommatrices de mémoire avant une indexation importante

### Erreur `KeyError: 'disk_percent'`

Vérifie que le fichier `monitoring.py` retourné par `get_system_info()` contient bien la clé suivante :

```python
"disk_percent": disk.percent
```

Puis arrête et relance complètement Streamlit :

```bash
Ctrl + C
streamlit run app.py
```

---

## 🚀 Évolutions possibles

- [ ] Remplacer le routeur à règles par un routeur piloté par LLM
- [ ] Ajouter un système de score de confiance dans les réponses
- [ ] Ajouter un reranker pour améliorer la pertinence des passages récupérés
- [ ] Ajouter la comparaison multi-documents
- [ ] Ajouter le résumé automatique de documents
- [ ] Ajouter une mémoire conversationnelle persistante
- [ ] Ajouter une gestion complète des utilisateurs
- [ ] Ajouter une journalisation avancée et un tableau de bord analytique
- [ ] Ajouter la génération de réponses en streaming
- [ ] Ajouter le support OCR pour les PDF scannés
- [ ] Dockeriser l’application
- [ ] Ajouter une orchestration agentique avec LangGraph
- [ ] Ajouter des tests unitaires et d’intégration
- [ ] Mettre en place une chaîne CI/CD avec GitHub Actions

---

## 👤 Auteur

Projet développé dans le cadre d’un portfolio technique orienté **Data Engineering**, **Intelligence Artificielle**, **RAG**, **LLM** et **systèmes agentiques**.

---

## 📄 Licence

Ce projet est destiné à un usage pédagogique, expérimental et de démonstration.
