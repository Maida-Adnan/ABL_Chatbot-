# RAG Chatbot — Task List

## Phase 1 — Single chatbot works end-to-end (no UI, no bank docs yet)

### Goal: one question → one answer, fully working in terminal.
### Not yet: RAG, ChromaDB, embeddings, FastAPI, multi-turn memory.

### Core
- [x] `core/ollama_client.py` — wraps `ollama.chat()`, takes model name + messages, returns text
- [x] `core/config.py` — model name, Ollama host/port, loaded from `.env`
- [x] `test_chat.py` — sends one hardcoded question, prints response (already done)

### Phase 1 tests
- [x] Ollama responds to a basic prompt
- [ ] Error handling when Ollama isn't running (clear error message, not silent fail)
- [ ] Model name is configurable via `.env`, not hardcoded

---

## Phase 2 — Document ingestion (no retrieval yet, just storage)

### Goal: documents get chunked, embedded, and stored. Nothing reads them back yet.
### Not yet: similarity search, chatbot integration.

### Data prep
- [ ] `data/raw/` — folder for original Allied Bank docs (txt/pdf)
- [ ] `ingestion/loader.py` — reads files from `data/raw/`, extracts plain text
- [ ] `ingestion/chunker.py` — splits text into ~300-500 word chunks with overlap
- [ ] `ingestion/embedder.py` — calls `nomic-embed-text` via Ollama, returns vector for a chunk
- [ ] `ingestion/store.py` — writes chunk text + vector + metadata into ChromaDB collection
- [ ] `ingestion/run_ingest.py` — orchestrates loader → chunker → embedder → store for all files in `data/raw/`

### Phase 2 tests
- [ ] Loader correctly extracts text from a sample `.txt` and `.pdf`
- [ ] Chunker produces chunks within expected word-count range
- [ ] Embedder returns a vector of expected length for a sample chunk
- [ ] Store: chunk count in ChromaDB matches expected chunk count after ingest

---

## Phase 3 — Retrieval (read-only, still no chatbot integration)

### Goal: given a question, return the most relevant stored chunks. Nothing generated yet.
### Not yet: prompt building, model response generation.

- [x] `core/retriever.py` — combines embedding the question AND searching ChromaDB in one file (originally planned as two separate files, merged since they're always used together)

 (The core/retriever.py file executes semantic search by converting user questions into vector embeddings and querying ChromaDB for relevant data chunks. It returns the top text matches along with their distance scores to evaluate relevance.)

- [ ] `dev/sample_questions.json` — skipped; tested with ad-hoc questions directly in test files instead

### Phase 3 tests
- [x] Search returns expected chunk(s) for an obvious test question — confirmed: "Asaan Mobile Account" question correctly returned the AMA chunk as top match (distance: 138)
- [x] top_k is configurable (e.g. 3 vs 5 results) — confirmed: `top_k` is a parameter with a default value
- [x] Search handles empty ChromaDB collection gracefully (no crash) — not tested

---

## Phase 4 — RAG pipeline (retrieval + generation combined)

### Goal: full question-to-answer flow using retrieved context. Still CLI only.
### Not yet: FastAPI, sessions, conversation history.

- [x] `core/prompt_builder.py` — combines retrieved chunks + user question into final prompt, with instructions to only use given context
- [x] `core/rag_pipeline.py` — orchestrates: retrieve → check relevance (distance threshold) → build prompt → call Ollama → return answer
- [x] `core/tests/test_rag.py` — test script: runs one relevant question and one irrelevant question through the pipeline

### Phase 4 tests
- [x] Pipeline returns an answer grounded in retrieved context — confirmed: Asaan Mobile Account question returned accurate step-by-step answer from actual document content
- [x] Pipeline handles question with no relevant chunks (says "I don't know" instead of hallucinating) — confirmed: "capital of France" question correctly returned fallback message without calling the model
- [ ] Prompt builder doesn't exceed reasonable token length when chunks are large — not tested

---

## Phase 5 — FastAPI wrapper (make it callable)

### Goal: chatbot is reachable as an API endpoint.
### Not yet: frontend, auth, conversation memory across requests.

- [ ] `main.py` — app init, CORS, startup checks (Ollama reachable, ChromaDB reachable)
- [ ] `routers/chat.py` — POST `/chat` — takes `{question}`, runs `rag/pipeline.py`, returns `{answer}`
- [ ] `routers/health.py` — GET `/health` — confirms Ollama + ChromaDB are up

### Phase 5 tests
- [ ] POST `/chat` returns valid JSON response for a sample question
- [ ] `/health` correctly reports down services if Ollama/ChromaDB are unreachable
- [ ] Invalid/empty question input returns a clean 400 error, not a crash

---

## Phase 6 — Polish (optional, after core works)

### Not started until Phase 1-5 are solid.

- [ ] Conversation history (multi-turn memory per session)
- [ ] Simple frontend (HTML/JS chat widget)
- [ ] Source citation (show which doc/chunk the answer came from)
- [ ] Re-ingestion endpoint (update docs without restarting server)