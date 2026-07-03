# ABL Chatbot — Allied Bank RAG Chatbot

A locally-running AI chatbot for Allied Bank customers, built using Retrieval-Augmented Generation (RAG). It answers questions about Allied Bank's products and services using actual bank documents, without sending any data to external APIs.

---

## What it does

- Accepts a customer question via a REST API
- Searches a local vector database (ChromaDB) for the most relevant sections from Allied Bank's customer-facing documents
- Passes the retrieved context to a local AI model (DeepSeek-R1) via Ollama
- Returns a grounded answer based only on the bank's actual content
- Declines to answer questions outside its knowledge base, instead of hallucinating

---

## Tech Stack

| Component | Tool |
|---|---|
| Language Model | DeepSeek-R1 1.5B (via Ollama) |
| Embedding Model | nomic-embed-text (via Ollama) |
| Vector Database | ChromaDB |
| API Framework | FastAPI |
| PDF Extraction | pypdf |
| Language | Python 3.14 |

---

## Project Structure

```
ABL_Chatbot/
  core/
    config.py           # loads settings from .env
    ollama_client.py    # wraps Ollama chat calls
    embedder.py         # converts text to vectors
    loader.py           # PDF extraction + 3-tier chunking
    retriever.py        # embeds query + searches ChromaDB
    vectorstore.py      # ChromaDB connection + storage
    prompt_builder.py   # builds RAG prompt from chunks + question
    rag_pipeline.py     # orchestrates full question → answer flow
    tests/
      test_chat.py      # tests Ollama connection
      test_retrieval.py # tests chunk retrieval
      test_rag.py       # tests full RAG pipeline
  routers/
    chat.py             # POST /chat endpoint
    health.py           # GET /health endpoint
  data/raw/             # place your PDF documents here (gitignored)
  chroma_db/            # auto-generated vector store (gitignored)
  main.py               # FastAPI app entry point
  run_ingest.py         # run once to ingest documents into ChromaDB
  verify_ingest.py      # confirms ingestion was successful
  .env                  # your local config (gitignored)
  requirements.txt      # all Python dependencies
```

---

## Setup

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed and running

### 1. Clone the repo
```bash
git clone https://github.com/Maida-Adnan/ABL_Chatbot-.git
cd ABL_Chatbot-
```

### 2. Pull required Ollama models
```bash
ollama pull deepseek-r1:1.5b
ollama pull nomic-embed-text
```

### 3. Create and activate virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Create a `.env` file in the project root
```
OLLAMA_MODEL=deepseek-r1:1.5b
OLLAMA_HOST=http://localhost:11434
```

### 6. Add your documents
Place your PDF files inside `data/raw/`.

### 7. Run ingestion (once)
```bash
python run_ingest.py
```
This extracts, chunks, embeds, and stores your documents in ChromaDB. Takes a few minutes depending on document size.

### 8. Verify ingestion
```bash
python verify_ingest.py
```

---

## Running the API

```bash
uvicorn main:app --reload
```

Server runs at `http://127.0.0.1:8000`

---

## API Endpoints

### `GET /health`
Checks if Ollama and ChromaDB are reachable.

**Response:**
```json
{
  "ollama": "ok",
  "chromadb": "ok (247 chunks)"
}
```

### `POST /chat`
Accepts a question and returns a grounded answer.

**Request:**
```json
{
  "question": "How do I activate my Asaan Mobile Account?"
}
```

**Response:**
```json
{
  "answer": "To activate your Asaan Mobile Account (AMA), dial *2262# from your registered mobile number..."
}
```

**Out-of-scope question response:**
```json
{
  "answer": "That question doesn't fall under what I handle. I can help with Allied Bank's customer-facing products and services — accounts, cards, financing options, digital banking, and related processes."
}
```

---

## How it works

1. **Ingestion (one-time):** PDFs are extracted, split into chunks using a 3-tier strategy (section headers → numbered sub-headers → word-count fallback), embedded using `nomic-embed-text`, and stored in ChromaDB.

2. **Retrieval:** When a question arrives, it is embedded using the same model and compared against stored chunks using vector similarity search.

3. **Relevance check:** If the closest chunk's distance score exceeds a threshold (450), the question is considered out-of-scope and a fallback message is returned without calling the AI model.

4. **Generation:** Retrieved chunks are combined with the question into a prompt, sent to `deepseek-r1:1.5b` via Ollama, and the model generates a grounded answer.

---

## Testing

```bash
# Test Ollama connection
python -m core.tests.test_chat

# Test retrieval only
python -m core.tests.test_retrieval

# Test full RAG pipeline
python -m core.tests.test_rag
```

---

## Built by
Maida Adnan — AI Intern, Allied Bank Limited
