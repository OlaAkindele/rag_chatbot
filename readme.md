# Experimental Database Assistant Chatbot (RAG (Graph + Vector Search) + Neo4j + RAG-Evaluation)

A full-stack, production-ready Retrieval-Augmented Generation (RAG) chatbot leveraging Neo4j, LangChain, OpenAI, and React. Query an enterprise-scale email database with natural language and receive context-aware, confidence-scored responses. Built for experimentation and extensibility!

---

## ✨ Features

- **RAG Chatbot:** Combines LLM reasoning with semantic vector search and graph querying.
- **Neo4j Backend:** Powerful knowledge graph & vector search over emails.
- **OpenAI LLMs:** Flexible, configurable language models (default: GPT-4o-mini).
- **ReAct Agent:** Structured agent reasoning with tool use (Cypher, semantic search, fallback chat).
- **Web Frontend:** Fast, simple React UI with confidence scoring.
- **Dockerized:** One-command setup for local or cloud environments.
- **Evaluation:** Built-in RAG response evaluation for research/experimentation.

---

## 🏗️ Architecture


- **Frontend:** React + Nginx (port 3000/80)
- **Backend:** FastAPI + LangChain agent (port 8000)
- **Database:** Neo4j Enterprise (graph & vector index, ports 7474/7687)
- **All services run via Docker Compose**

---

## 🚀 Quick Start

### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop) & [Docker Compose](https://docs.docker.com/compose/)
- [Git](https://git-scm.com/)

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/rag_chatbot.git
cd rag_chatbot
```

### 2. Configure Environment
Create .env file in the project root directory

Fill in your OpenAI API key and (optionally) custom Neo4j credentials as seen below:
---------------------------------------------
NEO4J_URI=bolt://neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o
---------------------------------------------

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



### 3. Import Data into Neo4j
Place your email CSV file in the /import directory (default: Clean_Emails.csv).

The import Cypher is preconfigured in import/load_emails.cql.

### 4. Launch Everything (Frontend, Backend API, Neo4j Browser)
Frontend: http://localhost:3000

Backend API: http://localhost:8000/docs (FastAPI docs)

Neo4j Browser: http://localhost:7474

```bash
docker-compose up --build
```

### 5. Load Email Data (You can always replace with your data)
```bash
docker-compose exec neo4j bin/cypher-shell -u neo4j -p password -f /import/load_emails.cql
```

#### OR

Open Neo4j Browser at http://localhost:7474, log in, and run:

:play import/load_emails.cql

### 6. Recreate the Vector Index (for vector search)
```bash
docker-compose exec neo4j bin/cypher-shell -u neo4j -p password "CALL db.index.vector.createNodeIndex('emailEmbeddings','Email','embedding',1536,'cosine');" && docker-compose exec neo4j bin/cypher-shell -u neo4j -p password "CALL db.awaitIndexes();"

```

### 7. Restart the Backend
```bash
docker-compose restart backend
```

### 8. Open the React App
Go to http://localhost:3000 and chat with React app (RAG Chatbot).