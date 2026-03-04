# DocQuery — RAG-Powered Documentation Chatbot
## End-to-End Project Plan

---

## Executive Summary

**Project name:** DocQuery
**Tagline:** Your documentation, answering questions. With citations.
**What it is:** A chatbot that ingests your documentation sites (HTML, Markdown, OpenAPI specs), chunks and embeds the content into a vector database, and answers user questions using Retrieval-Augmented Generation — with source citations, confidence scores, and a "content gap" detector that tells you what's missing from your docs.

**Why this project:**
Every enterprise company is asking: "How will our documentation be consumed by AI?" Companies building RAG pipelines over their docs need technical writers who understand both the content AND the retrieval infrastructure. DocQuery proves you understand both sides — you're not just writing docs that humans read, you're writing docs that AI can retrieve and reason over.

**What makes it best-in-class:**
- Ingests your own live documentation sites (not generic PDFs)
- Source citations with clickable links back to the original doc page
- Content gap detection — surfaces questions users ask that your docs can't answer
- Chunking strategy designed by a documentation architect (section-aware, not naive)
- Confidence scoring — the chatbot says "I'm not sure" when retrieval quality is low
- Works as a widget embeddable in any documentation site
- Fully open-source, deployable on Vercel

---

## Strategic Positioning

### Why this matters for your career

| Signal | What it tells hiring managers |
|--------|------------------------------|
| RAG pipeline built | "She understands how docs get consumed by AI systems" |
| Section-aware chunking | "She thinks about information architecture at the data layer" |
| Content gap detection | "She treats docs as a product with measurable coverage gaps" |
| Source citations | "She cares about accuracy and traceability" |
| Embeddable widget | "She builds tooling that integrates into real doc sites" |

This is the project that moves you from "Senior Technical Writer" to "Documentation Engineer who understands AI infrastructure."

### Competitive landscape

| Tool | What it does | DocQuery advantage |
|------|-------------|-------------------|
| ChatGPT over docs | Generic RAG, no structure awareness | DocQuery uses section-aware chunking designed for documentation |
| Mendable / Inkeep | SaaS doc chatbots | DocQuery is free, open-source, self-hostable |
| Algolia DocSearch | Search, not conversational | DocQuery provides conversational answers with citations |
| ReadMe AI chatbot | Tied to ReadMe platform | DocQuery works with any documentation site |
| Custom GPTs | No content gap detection, no analytics | DocQuery surfaces what's missing, not just what's there |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      INGESTION PIPELINE                      │
│                                                              │
│  Documentation Sources                                       │
│  ├── HTML sites (crawl via URL)                              │
│  ├── Markdown files (GitHub repo)                            │
│  ├── OpenAPI specs (YAML/JSON)                               │
│  └── Confluence/Wiki export (HTML)                           │
│                                                              │
│         ▼                                                    │
│  Section-Aware Chunker                                       │
│  ├── Splits by heading hierarchy (H1 → H2 → H3)            │
│  ├── Preserves code blocks as atomic units                   │
│  ├── Keeps tables intact                                     │
│  ├── Attaches metadata: source URL, section path, doc type   │
│  └── Overlap: 100 tokens between chunks                      │
│                                                              │
│         ▼                                                    │
│  Embedding Model                                             │
│  └── OpenAI text-embedding-3-small (1536 dims)              │
│      or open-source: all-MiniLM-L6-v2 (384 dims)           │
│                                                              │
│         ▼                                                    │
│  Vector Database                                             │
│  └── ChromaDB (local/dev) or Pinecone (production)          │
│      Stored: embedding + chunk text + metadata               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      QUERY PIPELINE                          │
│                                                              │
│  User Question                                               │
│         ▼                                                    │
│  Query Reformulation (optional)                              │
│  └── Rephrase for better retrieval (LLM-assisted)           │
│                                                              │
│         ▼                                                    │
│  Vector Similarity Search                                    │
│  └── Top-k retrieval (k=5) + metadata filtering             │
│                                                              │
│         ▼                                                    │
│  Re-ranking (optional)                                       │
│  └── Cross-encoder re-rank for precision                     │
│                                                              │
│         ▼                                                    │
│  Context Assembly                                            │
│  └── Retrieved chunks + system prompt + conversation history │
│                                                              │
│         ▼                                                    │
│  LLM Generation (GPT-4o / Claude)                           │
│  └── Answer + source citations + confidence score            │
│                                                              │
│         ▼                                                    │
│  Response                                                    │
│  ├── Answer text                                             │
│  ├── Sources: [{ title, url, section, relevance_score }]    │
│  ├── Confidence: high / medium / low                         │
│  └── If low confidence → logged as "content gap"            │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Language** | Python 3.11+ | LangChain ecosystem is Python-first |
| **RAG Framework** | LangChain + LCEL | Industry standard, composable chains, well-documented |
| **Vector DB (dev)** | ChromaDB | Local, zero-config, free, perfect for demos |
| **Vector DB (prod)** | Pinecone (free tier) | Managed, scalable, 100K vectors free |
| **Embeddings** | OpenAI `text-embedding-3-small` | Best cost/quality ratio, 1536 dims |
| **LLM** | OpenAI GPT-4o-mini (default), GPT-4o (optional) | Cost-effective, high quality |
| **Web Crawler** | `beautifulsoup4` + `httpx` | Crawl your own doc sites for ingestion |
| **Text Splitter** | Custom section-aware splitter (LangChain base) | Documentation-optimized chunking |
| **Backend API** | FastAPI | You already know it from PPT2Video |
| **Frontend** | Next.js 14 (chat UI) + embeddable React widget | Consistent with DocCraft / SpecFlow stack |
| **Conversation Memory** | SQLite (via LangChain) | Persistent chat history, multi-session |
| **Deployment** | Vercel (frontend) + Railway/Render (API) | Free tiers, easy deploy |

---

## Feature Breakdown (Phased)

### Phase 1: Ingestion Pipeline (Weeks 1–2)
*Goal: Crawl a documentation site, chunk it intelligently, store embeddings.*

**1.1 Documentation Crawler**
- Input: base URL of a documentation site (e.g., `sulagnasasmal.github.io/vaultpay-api-docs/`)
- Crawl all pages within the domain using `httpx` + `beautifulsoup4`
- Extract: page title, heading hierarchy, body content, code blocks, tables
- Respect: `robots.txt`, rate limiting (1 req/sec), max depth (configurable)
- Also support: direct Markdown file ingestion from a GitHub repo path
- Also support: OpenAPI YAML/JSON file → parse into endpoint descriptions
- Output: list of `Document` objects with content + rich metadata

**1.2 Section-Aware Chunker**
This is the key differentiator. Naive chunking (split every 500 tokens) destroys documentation structure. DocQuery's chunker understands docs.

```
Strategy: Hierarchical Section Splitting

Document: "VaultPay API — Authentication"
├── H1: Authentication                          → Chunk boundary
│   ├── H2: API Key Authentication              → Chunk boundary
│   │   ├── paragraph text                      → Part of H2 chunk
│   │   └── code block (curl example)           → Kept atomic, part of H2 chunk
│   ├── H2: OAuth 2.0                           → Chunk boundary
│   │   ├── H3: Authorization Code Flow         → Sub-chunk boundary
│   │   └── H3: Client Credentials Flow         → Sub-chunk boundary
│   └── H2: Token Refresh                       → Chunk boundary
```

Rules:
- Split on heading boundaries (H1, H2, H3)
- Never split inside a code block or table — keep them atomic
- Max chunk size: 800 tokens (with 100-token overlap)
- If a section exceeds 800 tokens, split at paragraph boundaries within section
- Each chunk gets metadata:
  - `source_url`: full URL of the page
  - `section_path`: e.g., "Authentication > OAuth 2.0 > Client Credentials Flow"
  - `doc_type`: api-reference | admin-guide | tutorial | conceptual
  - `heading_level`: 1, 2, or 3
  - `has_code`: boolean
  - `has_table`: boolean

**1.3 Embedding & Storage**
- Embed each chunk using `text-embedding-3-small`
- Store in ChromaDB with metadata for filtering
- Collection structure:
  - One collection per documentation site
  - Metadata filters: `doc_type`, `heading_level`, `has_code`
- Build index: ~2-5 seconds for a typical 50-page doc site
- Provide CLI command: `python ingest.py --url https://your-docs-site.com`

**1.4 Re-ingestion & Freshness**
- Content hash per page — only re-embed if content changed
- CLI: `python ingest.py --url ... --refresh` (incremental update)
- Timestamp tracking: know when each chunk was last updated

---

### Phase 2: Query Pipeline & Chat (Weeks 3–4)
*Goal: Ask a question, get an answer with citations from your docs.*

**2.1 Retrieval Chain**
Using LangChain's LCEL (LangChain Expression Language):

```python
# Simplified pipeline
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt_template
    | llm
    | output_parser
)
```

Detailed flow:
1. **Query reformulation** — LLM rewrites the user's question for better retrieval
   - "How do I authenticate?" → "VaultPay API authentication methods API key OAuth"
2. **Vector search** — top-k=5 similarity search in ChromaDB
3. **Metadata filtering** — optional: restrict to specific doc type or section
4. **Context assembly** — concatenate retrieved chunks with source metadata
5. **LLM generation** — GPT-4o-mini generates answer using ONLY retrieved context

**2.2 System Prompt (Critical for Quality)**
```
You are DocQuery, a documentation assistant for {site_name}.

Rules:
1. Answer ONLY using the provided context. Never use prior knowledge.
2. If the context doesn't contain enough information, say:
   "I couldn't find a clear answer in the documentation for this."
3. Always cite your sources using [Source: page_title](url) format.
4. If multiple sections are relevant, synthesize them into a coherent answer.
5. For code examples, reproduce them exactly as they appear in the docs.
6. Be concise. Match the tone of the documentation.
```

**2.3 Source Citations**
Every answer includes:
- Inline citations: `[Source: Authentication Guide](https://...#oauth)`
- Footer sources list with relevance scores
- Clickable links that deep-link to the specific section (using URL anchors)

**2.4 Confidence Scoring**
- Based on retrieval similarity scores:
  - Top chunk similarity > 0.85 → HIGH confidence
  - Top chunk similarity 0.70–0.85 → MEDIUM confidence
  - Top chunk similarity < 0.70 → LOW confidence
- LOW confidence triggers:
  - Visual indicator in chat (amber warning)
  - Answer prefixed with: "I'm not fully confident in this answer..."
  - Question logged to content gap tracker (Phase 3)

**2.5 Conversation Memory**
- Multi-turn chat with context carry-over
- LangChain's `SQLiteMessageHistory` for persistent storage
- History-aware retriever: reformulates follow-up questions using context
  - User: "How does authentication work?" → [answer about OAuth]
  - User: "What about refresh tokens?" → reformulated to "OAuth refresh token flow in VaultPay API"

**2.6 FastAPI Backend**
```
POST /api/chat
  Body: { "question": "...", "session_id": "...", "collection": "vaultpay" }
  Response: {
    "answer": "...",
    "sources": [{ "title": "...", "url": "...", "section": "...", "score": 0.89 }],
    "confidence": "high",
    "session_id": "..."
  }

POST /api/ingest
  Body: { "url": "https://...", "collection_name": "..." }
  Response: { "status": "success", "chunks_created": 142, "pages_crawled": 28 }

GET /api/collections
  Response: [{ "name": "vaultpay", "chunks": 142, "last_updated": "..." }]

GET /api/gaps
  Response: [{ "question": "...", "timestamp": "...", "confidence": "low" }]
```

---

### Phase 3: Content Gap Detection (Week 5)
*Goal: Surface what users ask that your docs can't answer. This is the killer feature.*

**3.1 Gap Logging**
Every LOW confidence query is automatically logged:
```json
{
  "question": "How do I handle 3D Secure authentication for EU cards?",
  "timestamp": "2026-03-15T14:22:00Z",
  "confidence_score": 0.42,
  "top_retrieval_score": 0.38,
  "nearest_section": "Authentication > OAuth 2.0",
  "collection": "vaultpay",
  "session_id": "abc123"
}
```

**3.2 Gap Dashboard**
- Table view: all unanswered/low-confidence questions
- Sortable by: frequency (if same question asked multiple times), recency, confidence score
- Grouping: cluster similar questions (e.g., "3D Secure" questions grouped together)
- Action buttons per gap:
  - "Create doc section" → suggests a heading + outline for the missing content
  - "Mark as out of scope" → removes from active gaps
  - "Assign to writer" → (conceptual — demonstrates team workflow thinking)

**3.3 Gap Report Export**
- Export as Markdown or CSV
- Format:
```markdown
# Documentation Content Gaps — VaultPay API Docs
Generated: 2026-03-15

## High Priority (asked 3+ times)
| Question | Times Asked | Nearest Section | Suggested Action |
|----------|-------------|-----------------|-----------------|
| How to handle 3D Secure for EU cards? | 5 | Authentication | Add "3D Secure" subsection |
| What are the webhook retry policies? | 3 | Webhooks | Add retry/backoff documentation |

## Medium Priority (asked 1–2 times)
...
```

**3.4 Why This Matters**
This feature reframes documentation as a measurable product. In an interview, you can say: "I built a system that tells documentation teams exactly what content is missing, prioritized by how often users ask for it." That's a documentation strategy conversation, not a tooling conversation.

---

### Phase 4: Chat UI & Embeddable Widget (Week 6)
*Goal: Beautiful chat interface + a widget you can embed in any doc site.*

**4.1 Standalone Chat UI (Next.js)**
- Clean, minimal chat interface
- Left sidebar: collection selector (switch between doc sites)
- Chat area: messages with source citation cards
- Source cards: expandable, show section preview + link
- Confidence indicator: green/amber/red dot per answer
- "Ask about your docs" placeholder text
- Dark/light mode
- Mobile responsive

**4.2 Embeddable Widget**
- `<script>` tag that any documentation site can drop in
- Floating chat bubble (bottom-right corner)
- Expands to a slide-in chat panel
- Configuration via data attributes:
```html
<script
  src="https://docquery.vercel.app/widget.js"
  data-collection="vaultpay"
  data-api="https://docquery-api.railway.app"
  data-theme="dark"
  data-position="bottom-right"
></script>
```
- Embed it on your own VaultPay docs site as a live demo

**4.3 Search vs. Chat Toggle**
- Quick search mode: type a question, get top 3 relevant doc sections (no LLM)
- Chat mode: full conversational RAG with multi-turn context
- User can switch between modes

---

### Phase 5: Showcase & Polish (Week 7)
*Goal: Make it demo-ready and portfolio-worthy.*

**5.1 Pre-Loaded Demo Collections**
Ship with 3 of your own doc sites pre-indexed:
1. **VaultPay API Docs** — API reference, authentication, webhooks
2. **FraudShield AI Engine** — risk scoring, model explainability, compliance
3. **US Payments Hub** — ACH, Fedwire, SWIFT, payment rail operations

Users can also paste any URL to ingest their own docs.

**5.2 Demo Scenarios (for interviews & LinkedIn)**
Prepare these conversation flows:
- "How does OAuth authentication work in VaultPay?" → [detailed answer with code + citations]
- "What regulations apply to the /payments/initiate endpoint?" → [compliance-aware answer]
- "How do I verify webhook signatures?" → [step-by-step from docs with code block]
- "What's the difference between RTP and FedNow settlement?" → [cross-doc synthesis]
- "How do I set up 3D Secure for EU cards?" → [LOW confidence → content gap detected]

**5.3 README & Repository**
```
docquery/
├── ingestion/
│   ├── crawler.py              # Web crawler for doc sites
│   ├── chunker.py              # Section-aware text splitter
│   ├── embedder.py             # Embedding + ChromaDB storage
│   └── openapi_loader.py       # OpenAPI spec → doc chunks
├── query/
│   ├── retriever.py            # Vector search + re-ranking
│   ├── chain.py                # LangChain RAG chain
│   ├── confidence.py           # Confidence scoring logic
│   └── memory.py               # Conversation history (SQLite)
├── gaps/
│   ├── tracker.py              # Content gap logger
│   ├── clusterer.py            # Question clustering
│   └── reporter.py             # Gap report generator
├── api/
│   ├── main.py                 # FastAPI app
│   ├── routes/
│   │   ├── chat.py             # Chat endpoint
│   │   ├── ingest.py           # Ingestion endpoint
│   │   └── gaps.py             # Gap analytics endpoint
├── frontend/                    # Next.js chat UI
│   ├── app/
│   │   ├── page.tsx            # Main chat interface
│   │   ├── gaps/page.tsx       # Content gap dashboard
│   │   └── components/
│   │       ├── ChatMessage.tsx
│   │       ├── SourceCard.tsx
│   │       ├── ConfidenceBadge.tsx
│   │       └── GapTable.tsx
├── widget/                      # Embeddable chat widget
│   └── widget.js
├── examples/                    # Pre-indexed doc collections
├── ingest.py                    # CLI entrypoint
├── requirements.txt
├── .env.example
└── README.md
```

---

## Timeline

| Week | Phase | Deliverable | Hours |
|------|-------|------------|-------|
| 1 | Ingestion | Crawler + section-aware chunker | 15–20 |
| 2 | Ingestion | Embedding pipeline + ChromaDB storage + CLI | 10–15 |
| 3 | Query | RAG chain + system prompt + citations | 15–20 |
| 4 | Query | Confidence scoring + conversation memory + FastAPI | 15–20 |
| 5 | Gaps | Content gap tracker + dashboard + export | 12–15 |
| 6 | UI | Chat frontend + embeddable widget | 15–20 |
| 7 | Showcase | Demo collections + README + LinkedIn posts | 10–12 |
| **Total** | | | **~92–122 hrs** |

---

## LinkedIn Content Strategy

| Week | Post | Hook |
|------|------|------|
| 2 | "I built a chunker that actually understands documentation structure" | Show naive vs. section-aware chunking side by side |
| 4 | "My docs now answer questions. With citations." | Demo GIF: question → answer → source link |
| 5 | "The chatbot told me what's missing from my documentation" | Content gap detection reveal — the differentiator |
| 7 | "Technical writers who understand RAG will lead the next decade" | Thought leadership post tying it all together |

---

## Cost Estimate (Running the Project)

| Service | Monthly cost | Notes |
|---------|-------------|-------|
| OpenAI API (embeddings) | ~$0.50 | text-embedding-3-small, one-time per ingestion |
| OpenAI API (chat) | ~$2–5 | GPT-4o-mini at ~$0.15/1M input tokens |
| ChromaDB | $0 | Local, open-source |
| Pinecone (if used) | $0 | Free tier: 100K vectors |
| Vercel (frontend) | $0 | Free tier |
| Railway (API) | $0–5 | Free tier or $5/mo hobby plan |
| **Total** | **$2–10/mo** | |

---

## Minimum Viable Demo (If Time-Constrained)

If you have only 2 weeks before an interview:

Build Phases 1 + 2 only. A Python CLI that ingests your VaultPay docs, stores embeddings in ChromaDB, and answers questions in the terminal with source citations. That's it. No frontend, no widget, no gap detection. Just:

```bash
$ python ingest.py --url https://sulagnasasmal.github.io/vaultpay-api-docs/
Crawled 12 pages. Created 142 chunks. Stored in ChromaDB.

$ python query.py "How does OAuth authentication work?"

Answer: VaultPay uses OAuth 2.0 with two supported flows: Authorization Code
(for user-facing apps) and Client Credentials (for server-to-server)...

Sources:
  [1] Authentication > OAuth 2.0 (score: 0.91)
      https://sulagnasasmal.github.io/vaultpay-api-docs/#oauth
  [2] Authentication > Token Refresh (score: 0.84)
      https://sulagnasasmal.github.io/vaultpay-api-docs/#token-refresh

Confidence: HIGH
```

That terminal output alone is a powerful interview talking point.

---

*Plan created: March 2026*
*Project: DocQuery — RAG-Powered Documentation Chatbot*
*Author: Sulagna Sasmal*
