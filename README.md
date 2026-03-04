# DocQuery — RAG-Powered Documentation Chatbot

> Your documentation, answering questions. With citations.

DocQuery ingests your documentation sites, chunks content intelligently using section-aware splitting, stores embeddings in a vector database, and answers questions using Retrieval-Augmented Generation — with source citations, confidence scores, and content gap detection.

## Features

- **Section-Aware Chunking** — Splits by heading hierarchy, preserves code blocks and tables
- **Source Citations** — Every answer includes clickable links back to the original doc page
- **Confidence Scoring** — HIGH / MEDIUM / LOW based on retrieval quality
- **Content Gap Detection** — Surfaces questions users ask that your docs can't answer
- **Conversation Memory** — Multi-turn chat with context carry-over
- **Embeddable Widget** — Drop-in chat bubble for any documentation site
- **CLI + API** — Terminal interface and REST API for integration

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

### 3. Ingest Your Documentation

```bash
python ingest.py --url https://your-docs-site.com --collection my-docs
```

Output:
```
Crawled 12 pages. Created 142 chunks. Stored in ChromaDB.
```

### 4. Query Your Docs (CLI)

```bash
python query_cli.py --collection my-docs
```

```
You: How does OAuth authentication work?

Answer: VaultPay uses OAuth 2.0 with two supported flows...

Sources:
  [1] Authentication > OAuth 2.0 (score: 0.91)
      https://docs.example.com/authentication#oauth
  [2] Authentication > Token Refresh (score: 0.84)
      https://docs.example.com/authentication#token-refresh

Confidence: HIGH (0.88)
```

### 5. Start the API

```bash
uvicorn api.main:app --reload --port 8000
```

### 6. Embed Widget on Any Doc Site

```html
<script
  src="https://your-docquery.vercel.app/widget.js"
  data-collection="my-docs"
  data-api="https://your-docquery-api.railway.app"
  data-theme="light"
></script>
```

## Architecture

```
Documentation Site → Crawler → Section-Aware Chunker → Embeddings → ChromaDB
                                                                        ↓
User Question → Query Reformulation → Vector Search → Context Assembly → LLM → Answer + Citations
                                                                                    ↓
                                                                        Low confidence? → Content Gap Log
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| RAG Framework | LangChain + LCEL |
| Vector DB | ChromaDB (local) / Pinecone (prod) |
| Embeddings | OpenAI text-embedding-3-small |
| LLM | GPT-4o-mini (default) |
| Web Crawler | BeautifulSoup4 + httpx |
| Backend | FastAPI |
| Memory | SQLite |

## API Endpoints

```
POST /api/chat          — Ask a question (RAG pipeline)
POST /api/ingest        — Crawl and index a doc site
GET  /api/collections   — List indexed collections
GET  /api/gaps          — View content gaps
GET  /api/gaps/report   — Generate gap report (Markdown)
```

## Content Gap Detection

DocQuery automatically logs questions it can't answer confidently:

```markdown
# Documentation Content Gaps — VaultPay

## High Priority (asked 3+ times)
| Question                              | Times Asked | Nearest Section |
|---------------------------------------|-------------|-----------------|
| How to handle 3D Secure for EU cards? | 5           | Authentication  |
| What are webhook retry policies?      | 3           | Webhooks        |
```

## Project Structure

```
docquery/
├── ingestion/
│   ├── crawler.py          # Web crawler for doc sites
│   ├── chunker.py          # Section-aware text splitter
│   └── embedder.py         # Embedding + ChromaDB storage
├── query/
│   ├── retriever.py        # Vector search
│   ├── chain.py            # RAG chain (retrieval + generation)
│   ├── confidence.py       # Confidence scoring
│   └── memory.py           # Conversation history (SQLite)
├── gaps/
│   └── tracker.py          # Content gap logger + reporter
├── api/
│   ├── main.py             # FastAPI app
│   └── routes/             # Chat, ingest, gaps endpoints
├── widget/
│   └── widget.js           # Embeddable chat widget
├── ingest.py               # CLI: ingest docs
├── query_cli.py            # CLI: interactive query
├── requirements.txt
└── README.md
```

## License

MIT
