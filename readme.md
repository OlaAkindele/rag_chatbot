# Database Assistant Chatbot (RAG (Graph + Vector Search) + Neo4j + RAG-Evaluation)

A full-stack, production-ready Retrieval-Augmented Generation (RAG) chatbot leveraging Neo4j, LangChain, OpenAI, and React. Query an enterprise-scale email database with natural language and receive context-aware, confidence-scored responses.

---

## ⚠️ Requirements and Platform Notes

- **Docker Desktop**: Required for Mac and Windows ([download here](https://www.docker.com/products/docker-desktop))
- **Linux**: Install Docker Engine and Docker Compose directly.
- **Tested Platforms:**
    - Ubuntu 22.04.3 LTS (native or WSL2 on Windows)
    - Windows 11 (with WSL2: Ubuntu backend)
- **Neo4j Data Import:** For best results, use Linux or WSL2. Plain Windows setups may have issues with Neo4j import file access.

If you are on Windows, we strongly recommend enabling [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install) and using Ubuntu as your WSL distribution for the smoothest experience.

---

## ✨ Features

- **RAG Chatbot:** Combines LLM reasoning with semantic vector search and graph querying.
- **Neo4j Backend:** Powerful knowledge graph & vector search over emails.
- **OpenAI LLMs:** Flexible, configurable language models (default: GPT-4o).
- **ReAct Agent:** Structured agent reasoning with tool use (Cypher, semantic search, fallback chat ).
- **Web Frontend:** Fast, simple React UI with confidence scoring.
- **Dockerized:** One-command setup for local or cloud environments.
- **Evaluation:** Built-in RAG response evaluation (RAG-Eval) for research/experimentation.

---

## 🏗️ Architecture


- **Frontend:** React + Nginx (port 3000/80)
- **Backend:** FastAPI + LangChain agent (port 8000)
- **Database:** Neo4j Enterprise (graph & vector index, ports 7474/7687)
- **All services run via Docker Compose**

---

## 🚀 Quick Start

### Prerequisites

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (required for Windows and Mac)
- [WSL2 (Windows Subsystem for Linux 2)](https://learn.microsoft.com/en-us/windows/wsl/install) with Ubuntu, if on Windows for smooth Neo4j file import
- [Docker Engine & Compose](https://docs.docker.com/engine/install/) (for Linux users)
- [Neo4j](https://neo4j.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [Git](https://git-scm.com/)

> **Note:**  
> - Neo4j's data import (via `/import`) and Docker volume mounting are tested and reliable on Ubuntu Linux (**Windows with WSL2** for Windows users).  
> - Running on native Windows (without WSL2) may cause file access issues for Neo4j.



### 1. Clone the Repo

```bash
git clone https://github.com/OlaAkindele/rag_chatbot.git
cd rag_chatbot
```

### 2. Configure Environment
- Create .env file in the project root directory

- Fill in the OpenAI API key and custom Neo4j credentials as seen below:

```env
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o
```


### 3. Import Data into Neo4j
Place email CSV file in the /import directory (default: Clean_Emails.csv).

The import Cypher is preconfigured in import/load_emails.cql.

### 4. Launch Everything (Frontend, Backend API, Neo4j Browser)
Frontend: http://localhost:3000

Backend API: http://localhost:8000/docs (FastAPI docs)

Neo4j Browser: http://localhost:7474

```bash
docker-compose up --build
```

*If you run **docker-compose up --build** (without -d), your current terminal will be locked showing the live logs of your containers, so you can't type new commands there. So, to continue with the further steps, you might need to open another terminal*

```bash
docker-compose up --build -d
```

*If you used **docker-compose up --build -d**, the containers run in the background and your terminal is free for more commands. But you can always check logs or stream separately using  **docker-compose logs -f** after step 5-7 to see live logs*

### 5. Load Email Data (Graph data based on the project schema)
```bash
docker-compose exec neo4j bin/cypher-shell -u neo4j -p password -f /import/load_emails.cql
```

#### OR

Open Neo4j Browser at http://localhost:7474, log in, and run:

```arduino
:play import/load_emails.cql
```

### 6. Recreate the Vector Index (for vector search)
Linux/macOS shells (bash/zsh)
```bash
docker-compose exec neo4j bin/cypher-shell -u neo4j -p password "CALL db.index.vector.createNodeIndex('emailEmbeddings','Email','embedding',1536,'cosine');" && docker-compose exec neo4j bin/cypher-shell -u neo4j -p password "CALL db.awaitIndexes();"
```

Or Windows powershell
```bash
docker-compose exec neo4j bin/cypher-shell -u neo4j -p password "CALL db.index.vector.createNodeIndex('emailEmbeddings','Email','embedding',1536,'cosine');"
; docker-compose exec neo4j bin/cypher-shell -u neo4j -p password "CALL db.awaitIndexes();"
```

### 7. Restart the Backend
```bash
docker-compose restart backend
```

### 8. Open the React App
Go to http://localhost:3000 and chat with React app (RAG Chatbot).


#### 🛠️ Development
Backend (FastAPI/LangChain)

```bash
cd backend
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend (React)
```bash
cd frontend
npm install
npm start
```


## Need help?
- **Open an issue or pull request on GitHub**  