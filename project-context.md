#AI Knowledge Platform --- Project Context

## 1. Project Identity

**Project:** AI Knowledge Platform

**Goal:** Build a production-oriented AI-powered personal knowledge
platform that allows users to store, search, and interact with their own
knowledge.

The project is being developed as a serious portfolio project for
internship/full-time opportunities, with an iOS/UIKit client and a
backend capable of evolving into a complete AI/RAG system.

## 2. Product Vision

The platform allows users to:

-   Register and authenticate securely
-   Create, view, update, and delete notes
-   Search their own notes
-   Use PostgreSQL full-text search
-   Use semantic/vector search
-   Later ask an AI assistant questions grounded in their own knowledge
-   Access the platform through an iOS/UIKit client

Long-term AI pipeline:

``` text
User Knowledge
      ↓
Notes / Documents
      ↓
Chunking
      ↓
Embeddings
      ↓
pgvector
      ↓
Semantic Search
      ↓
RAG
      ↓
LLM
      ↓
AI Knowledge Assistant
```

## 3. Technology Stack

### Backend

-   Python
-   FastAPI
-   Pydantic
-   Pydantic Settings
-   SQLAlchemy
-   PostgreSQL
-   Alembic
-   Redis
-   pgvector
-   Ollama
-   `nomic-embed-text`
-   LLM API
-   REST APIs

### Client

-   Swift
-   UIKit
-   MVVM
-   REST API integration

### Infrastructure / Engineering

-   Git
-   GitHub
-   Docker
-   Testing
-   Logging
-   Security
-   Deployment

## 4. Architecture

Current backend architecture:

``` text
FastAPI
   ↓
API Routes
   ↓
Services
   ↓
Repositories
   ↓
PostgreSQL
```

AI retrieval architecture:

``` text
Note
 ↓
ChunkingService
 ↓
EmbeddingService
 ↓
NoteChunk
 ↓
pgvector
 ↓
Semantic Retrieval
```

Redis is coordinated at the service layer:

``` text
FastAPI
   ↓
API Routes
   ↓
NoteService
   ├──────────────→ RedisService → Redis
   │
   └──────────────→ NoteRepository → PostgreSQL
```

Future RAG architecture:

``` text
User Question
      ↓
Query Embedding
      ↓
Semantic Search
      ↓
Relevant NoteChunks
      ↓
Context Assembly
      ↓
LLM
      ↓
Grounded Answer
      ↓
Sources / Citations
```

**Architecture principle:** Technologies are introduced because the
product requires them, not merely to make the stack look impressive.

## 5. Repository Structure

``` text
ai-knowledge-platform/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── repositories/
│   └── db/
├── tests/
├── alembic/
├── .env
├── .gitignore
├── requirements.txt
├── README.md
└── .git/
```

Important backend files include:

``` text
app/
├── api/routes/
│   ├── auth.py
│   ├── users.py
│   └── notes.py
├── core/
│   ├── config.py
│   └── security.py
├── models/
│   ├── user.py
│   ├── note.py
│   └── note_chunk.py
├── schemas/
│   ├── user.py
│   ├── note.py
│   └── error.py
├── services/
│   ├── auth_service.py
│   ├── user_service.py
│   ├── note_service.py
│   ├── redis_service.py
│   ├── chunking_service.py
│   ├── embedding_service.py
│   └── embedding_ingestion_service.py
├── repositories/
│   ├── user_repository.py
│   └── note_repository.py
└── db/
    ├── base.py
    ├── session.py
    └── redis.py
```

## 6. Configuration

Configuration is handled through `pydantic-settings`.

Current environment configuration includes:

``` text
APP_NAME
APP_VERSION
ENVIRONMENT
DATABASE_URL
JWT_SECRET_KEY
JWT_ALGORITHM
JWT_ACCESS_TOKEN_EXPIRE_MINUTES
REDIS_URL
OLLAMA_HOST
EMBEDDING_MODEL
LLM_MODEL
RAG_MAX_DISTANCE
RAG_MAX_CONTEXT_CHARS
RAG_MAX_ANCHORS_PER_NOTE
RAG_HYBRID_TOP_K
RAG_CONVERSATION_HISTORY_LIMIT
RAG_CONVERSATION_RELEVANT_MESSAGE_LIMIT
```

Embedding configuration:

``` env
OLLAMA_HOST=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text
```

`.env` is ignored by Git.

## 7. Database

Database:

``` text
PostgreSQL
Database: ai_knowledge_db
```

SQLAlchemy is used as the ORM.

Alembic is the migration system.

`Base.metadata.create_all()` is no longer used by the application.
Schema changes are managed through Alembic migrations.

## 8. Current Database Models

### User

``` text
User
├── id
├── name
├── email
└── password_hash
```

Important constraints:

-   `id` is the primary key
-   `email` is unique and required
-   `name` is required
-   `password_hash` is required

### Note

``` text
Note
├── id
├── title
├── content
├── user_id
├── created_at
└── updated_at
```

`user_id` uses:

``` text
ForeignKey("users.id", ondelete="CASCADE")
```

and is indexed.

### NoteChunk

``` text
NoteChunk
├── id
├── note_id
├── content
├── contextual_content
├── chunk_index
├── embedding
└── created_at
```

`note_id` uses:

``` text
ForeignKey("notes.id", ondelete="CASCADE")
```

and is indexed.

The embedding column is:

``` text
vector(768)
```

because the selected local embedding model is `nomic-embed-text`.

## 9. Database Migrations

Alembic is fully integrated.

Schema changes are managed through migrations.

The database includes the `note_chunks` table required for vector
retrieval.

Important vector schema requirement:

``` text
note_chunks.embedding
    ↓
vector(768)
```

This dimension must remain aligned with the configured embedding model.

## 10. Authentication

Authentication uses:

-   Argon2 password hashing through `pwdlib`
-   JWT access tokens through `PyJWT`
-   FastAPI `OAuth2PasswordBearer`

Registration:

``` text
POST /users/
```

Login:

``` text
POST /auth/login
```

Flow:

``` text
Email + Password
      ↓
Find User
      ↓
Verify Argon2 Password
      ↓
Create JWT
      ↓
Return Access Token
```

## 11. Current User

Protected routes use `get_current_user()`.

Flow:

``` text
Authorization: Bearer <token>
          ↓
      Decode JWT
          ↓
      Validate `sub`
          ↓
      Load User
          ↓
    Current User
```

Current endpoint:

``` text
GET /users/me
```

Authentication failures return HTTP 401 with the standard API error
structure.

## 12. Authorization / Note Ownership

Users can only access their own notes.

The client does not provide the owner ID for note operations.

``` text
JWT
 ↓
Current User
 ↓
current_user.id
 ↓
Note operation
```

Ownership checks remain in the service layer.

Semantic search is also restricted to the current user's notes.

## 13. Current Notes API

``` text
POST   /notes/
GET    /notes/
GET    /notes/{note_id}
PUT    /notes/{note_id}
DELETE /notes/{note_id}
GET    /notes/search
```

The notes API also contains semantic-search functionality.

All note operations are authenticated.

## 14. Pagination

Pagination uses `skip` and `limit`.

Current constraints:

``` text
skip >= 0
1 <= limit <= 100
```

Note list responses include:

``` json
{
    "items": [],
    "total": 0,
    "skip": 0,
    "limit": 20,
    "has_more": false
}
```

## 15. Search

### PostgreSQL Full-Text Search

``` text
Note title + content
        ↓
to_tsvector()
        ↓
plainto_tsquery()
        ↓
@@
        ↓
ts_rank()
        ↓
Ordered results
```

Search is restricted to the authenticated user's notes.

### Semantic Search

Semantic search is integrated using pgvector.

``` text
User query
    ↓
EmbeddingService
    ↓
Query embedding
    ↓
NoteRepository.semantic_search()
    ↓
pgvector cosine distance
    ↓
Nearest NoteChunks
    ↓
Current user's notes only
```

Current retrieval exposes information including:

``` text
note_id
chunk_id
chunk_index
content
distance
```

This is semantic retrieval only, not complete RAG.

## 16. Database Indexing

Current important indexes include:

``` text
notes.user_id
note_chunks.note_id
```

Future indexes will be added when justified by actual query patterns.

Potential future examples include:

``` text
(user_id, created_at)
```

a GIN index for optimized PostgreSQL full-text search, and vector
indexes such as HNSW/IVFFlat when vector data and query requirements
justify them.

## 17. API Error Design

API errors use:

``` json
{
    "error": {
        "code": "NOTE_NOT_FOUND",
        "message": "Note not found"
    }
}
```

Stable codes include:

``` text
USER_ALREADY_EXISTS
USER_NOT_FOUND
NOTE_NOT_FOUND
AUTHENTICATION_FAILED
```

The iOS client should rely on `code`, not exact English `message`.

Internal database/provider details should not be exposed.

## 18. API Input Validation

Pydantic validates API boundaries.

User:

``` text
name: 2–100 characters
email: valid email
password: 8–128 characters
```

Names are stripped and blank names are rejected. Passwords are not
stripped.

Notes:

``` text
title: 1–255 characters
content: at least 1 character
```

Blank title/content values are rejected.

Pagination is constrained through FastAPI query validation.

## 19. Redis

Redis is implemented as a performance/temporary data layer. PostgreSQL
remains the source of truth.

Configuration:

``` text
REDIS_URL=redis://localhost:6379/0
```

`RedisService` centralizes:

``` text
GET
SET
DELETE
EXISTS
GET_INT
INCREMENT
TTL
```

Only `GET /notes/` is currently cached.

Strategy:

``` text
Cache-aside
+
Version-based invalidation
+
TTL
```

Version key:

``` text
notes:user:{user_id}:version
```

List cache key:

``` text
notes:user:{user_id}:v:{version}:list:{skip}:{limit}
```

TTL:

``` text
60 seconds
```

Successful mutations invalidate the user's notes cache by incrementing
the version after the PostgreSQL mutation.

Embedding data is not cached in Redis. Semantic-search caching is
deferred.

## 20. Chunking

`app/services/chunking_service.py` implements the initial
character-based chunking strategy.

Defaults:

``` text
chunk_size = 1000 characters
overlap = 200 characters
```

It:

-   rejects invalid chunk sizes
-   rejects overlap \>= chunk size
-   returns an empty list for empty/whitespace content
-   produces overlapping chunks

This is intentionally a simple initial strategy. More sophisticated
document-aware chunking can be introduced later for RAG.

## 21. Embedding Service

Local embeddings are generated through:

``` text
Ollama
Model: nomic-embed-text
Dimension: 768
```

`app/services/embedding_service.py`:

-   connects to Ollama
-   uses the configured embedding model
-   generates embeddings
-   validates dimensionality

An embedding whose dimension is not 768 is rejected.

## 22. Embedding Ingestion

`app/services/embedding_ingestion_service.py` coordinates:

``` text
Note content
   ↓
ChunkingService
   ↓
Chunks
   ↓
EmbeddingService
   ↓
Embeddings
   ↓
NoteChunk objects
   ↓
NoteRepository
```

The ingestion service does not commit.

It uses the same SQLAlchemy session supplied by the service layer.

If no chunks are generated, it raises an error rather than silently
creating a note without searchable chunks.

## 23. Transaction Ownership

`NoteService` owns commit/rollback.

``` text
Route
  ↓
NoteService          ← commit / rollback
  ↓
NoteRepository       ← DB operations / flush only
  ↓
PostgreSQL
```

The repository no longer commits note mutations.

Therefore:

``` text
Note
+
NoteChunks
+
Embeddings
```

participate in the same transaction.

## 24. Create Note + Embedding Flow

``` text
POST /notes/
      ↓
NoteService.create_note()
      ↓
Create Note
      ↓
flush
      ↓
Generate chunks
      ↓
Generate embeddings
      ↓
Insert NoteChunks
      ↓
COMMIT
      ↓
Redis cache invalidation
```

A note is not committed unless embedding ingestion succeeds.

## 25. Update Note + Embedding Flow

``` text
PUT /notes/{id}
      ↓
Verify ownership
      ↓
Update Note
      ↓
flush
      ↓
Delete old NoteChunks
      ↓
Generate new chunks
      ↓
Generate new embeddings
      ↓
Insert new NoteChunks
      ↓
COMMIT
      ↓
Redis cache invalidation
```

This prevents new note content from being committed alongside old
chunks.

## 26. Delete Note + Embedding Flow

``` text
DELETE /notes/{id}
      ↓
Verify ownership
      ↓
Delete Note
      ↓
COMMIT
      ↓
Redis invalidation
```

`note_chunks.note_id` uses `ON DELETE CASCADE`, so deleting a note
deletes its chunks.

## 27. Transaction Rollback

Failed mutations explicitly roll back:

``` python
try:
    ...
    self.db.commit()
except Exception:
    self.db.rollback()
    raise
```

This protects against partial embedding ingestion.

If embedding generation fails during an update, the previous committed
note/chunks remain intact.

## 28. Current AI / RAG Status

The project now has the initial RAG pipeline built incrementally on top of
semantic retrieval.

Completed AI/RAG capabilities:

``` text
FastAPI                         ✓
SQLAlchemy                      ✓
PostgreSQL                      ✓
Alembic                         ✓
Authentication                  ✓
Authorization                   ✓
Note CRUD                       ✓
PostgreSQL Full-Text Search    ✓
Pagination                      ✓
Database Indexing               ✓
API Error Design                ✓
Input Validation                ✓
Redis                           ✓
pgvector                        ✓
Local Embeddings                ✓
Embedding Ingestion             ✓
Semantic Retrieval              ✓
RAG Context Assembly            ✓
Prompt Construction             ✓
Local LLM Generation            ✓
Sources / Citations             ✓
Retrieval Relevance Filtering   ✓
Neighbor Chunk Expansion        ✓
Context Budgeting               ✓
Anchor-Aware Retrieval          ✓
Anchor Diversity                ✓
Hybrid Semantic + Lexical       ✓
RRF Score Fusion                ✓
Retrieval Evaluation            ✓
RAG Answer-Quality Evaluation   ✓
Contextual Retrieval            ✓
Conversation Persistence        ✓
Conversation-Aware Query Rewrite ✓
Conversation-Aware Retrieval    ✓
Conversational Prompting       ✓
Semantic Older-Message Retrieval ✓
End-to-End Conversational RAG  ✓
```

The AI layer is now beyond basic semantic search and has an initial
production-oriented RAG architecture.

## 29. RAG Architecture

The current RAG flow is:

``` text
User Question
      ↓
Query Embedding
      ↓
Semantic / Lexical / Hybrid Retrieval
      ↓
Relevance Filtering / RRF
      ↓
Anchor Diversity
      ↓
Neighbor Chunk Expansion
      ↓
Anchor-Aware Context Budget
      ↓
Context Assembly
      ↓
Prompt Construction
      ↓
Local LLM
      ↓
Grounded Answer + Sources
```

The RAG system is intentionally implemented as separate stages so retrieval,
context quality, prompting, generation, and evaluation can evolve
independently.

## 30. RAG Context Assembly

`app/schemas/rag.py` contains the RAG retrieval/context models.

`RetrievedChunk` currently carries:

``` text
note_id
chunk_id
chunk_index
content
distance | None
is_anchor
retrieval_sources
hybrid_score | None
```

`retrieval_sources` can contain:

``` text
semantic
lexical
neighbor
```

A chunk may be retrieved by both semantic and lexical search, so retrieval
source information is merged instead of representing the chunk twice.

Context assembly formats retrieved chunks with source metadata before they
are supplied to the prompt builder.

## 31. RAG Retrieval Flow

`RAGService.retrieve()`:

``` text
User query
   ↓
EmbeddingService
   ↓
NoteRepository.semantic_search()
   ↓
RetrievedChunk objects
```

The RAG service preserves the user's ownership boundary. Retrieval is always
performed against the authenticated user's notes before context reaches the
LLM.

## 32. Relevance Filtering

A configurable semantic relevance threshold was introduced:

``` env
RAG_MAX_DISTANCE=0.40
```

Lower cosine distance means greater semantic similarity.

The threshold is applied to semantic candidates before neighbor expansion.
If no chunks pass the threshold, the LLM is not called.

For hybrid/RRF retrieval, raw semantic distance is not used as the final
hybrid relevance score. Hybrid retrieval uses rank-based RRF instead.

## 33. Neighbor Chunk Expansion

Relevant semantic anchors can be expanded with neighboring chunks from the
same note.

Repository support:

``` text
get_neighbor_chunks()
```

The expansion flow is:

``` text
Semantic Candidates
      ↓
Relevance Filtering
      ↓
Anchor Chunks
      ↓
Neighbor Expansion
      ↓
Deduplication
      ↓
Document Ordering
```

Neighbor chunks inherit the anchor's retrieval distance for context handling;
the inherited distance is not treated as the neighbor's own semantic score.

## 34. Context Budgeting

A configurable character budget limits the amount of retrieved context sent
to the LLM:

``` env
RAG_MAX_CONTEXT_CHARS=12000
```

The current implementation uses a character budget rather than exact token
counting.

Anchor chunks are prioritized before neighbors when selecting context, after
which the selected chunks are placed back into document order.

## 35. Anchor-Aware Retrieval

`RetrievedChunk` distinguishes direct semantic matches from supporting
neighbors:

``` text
is_anchor = True
```

for semantic retrieval results, while neighbor chunks are non-anchor.

This distinction is preserved through deduplication and context budgeting.

This allows the system to prioritize chunks that directly matched the user
question without treating every supporting chunk as equally relevant.

## 36. Retrieval Diversity

A configurable per-note anchor limit was added:

``` env
RAG_MAX_ANCHORS_PER_NOTE=2
```

Only semantic anchors are limited by this setting. Neighbor chunks are not
restricted by the anchor-per-note limit.

This prevents one note from dominating the semantic retrieval candidates while
still allowing surrounding context to be included.

## 37. Prompt Construction

The RAG prompt explicitly instructs the LLM to answer using only the supplied
context and to state when the requested information is not available in the
user's notes.

Important principle:

``` text
Retrieval ≠ Truth
```

Retrieved chunks are evidence supplied to the LLM; the application controls
which chunks are allowed into the prompt.

## 38. LLM Integration

A dedicated `LLMService` uses Ollama for local generation.

Embedding and generation models are configured separately:

``` env
EMBEDDING_MODEL=nomic-embed-text
LLM_MODEL=<configured generation model>
```

The LLM receives:

``` text
System Prompt
+
User Prompt containing assembled context and question
```

## 39. Sources and Citations

The RAG answer response returns both:

``` text
answer
sources
```

Each source contains information identifying the originating note/chunk and
its retrieval metadata.

The same retrieved chunks used to construct the LLM context are returned as
sources. This keeps application-level source truth aligned with the context
actually given to the model.

## 40. Hybrid Search

Lesson 11 introduced hybrid retrieval combining:

``` text
Semantic Search
+
PostgreSQL Full-Text Search
```

Semantic retrieval captures meaning, while lexical retrieval captures exact
terms.

The lexical repository search uses PostgreSQL full-text search with
`to_tsvector`, `plainto_tsquery`, and `ts_rank`.

A chunk can be returned by both systems. Its retrieval metadata therefore
tracks multiple sources rather than duplicating the chunk.

Important observation from retrieval evaluation: lexical retrieval can fail
when a relevant chunk is semantically related to a query but does not contain
the query's exact searchable terms. For example, the current evaluation's JWT
and embeddings cases returned no lexical results while semantic retrieval
found the relevant chunks.

This is expected behavior and demonstrates the complementary roles of lexical
and semantic retrieval.

## 41. Reciprocal Rank Fusion

Raw semantic distance and PostgreSQL lexical rank are not directly comparable.
Hybrid retrieval therefore uses Reciprocal Rank Fusion (RRF):

``` text
RRF score = 1 / (k + rank)
```

with:

``` text
k = 60
```

Semantic and lexical rankings are fused by chunk ID. A chunk appearing in
both rankings receives contributions from both ranks.

Hybrid retrieval then selects the configured number of top results:

``` env
RAG_HYBRID_TOP_K=5
```

Hybrid retrieval should not be passed through the old semantic-distance
threshold because lexical results do not necessarily have a semantic distance.

## 42. Retrieval Evaluation

Lesson 13 added a dedicated retrieval evaluation package:

``` text
app/evaluation/
├── __init__.py
├── retrieval_dataset.py
├── retrieval_models.py
├── retrieval_metrics.py
├── retrieval_evaluator.py
├── retrieval_summary.py
└── retrieval_comparison.py
```

The evaluation dataset currently contains five representative test cases
covering pgvector, Redis caching, JWT authentication, hybrid search, and
embedding generation.

Each test case defines expected relevant chunk IDs.

## 43. Retrieval Evaluation Metrics

Current metrics:

``` text
Recall@K
Precision@K
Reciprocal Rank
Mean Reciprocal Rank (MRR)
```

Recall@K is true chunk-level recall:

``` text
relevant chunks retrieved in top K
-----------------------------------
       total relevant chunks
```

This is distinct from Hit Rate@K.

Precision@K measures the proportion of retrieved top-K chunks that are
relevant.

Reciprocal Rank measures the position of the first relevant result:

``` text
RR = 1 / rank
```

MRR is the mean reciprocal rank across evaluation queries.

## 44. Retrieval Evaluation Strategies

The same dataset and metrics are used to evaluate:

``` text
Semantic Retrieval
       ↓
semantic_search()

Lexical Retrieval
       ↓
full_text_search()

Hybrid Retrieval
       ↓
semantic_search()
       +
full_text_search()
       ↓
RRF
```

Evaluation does not modify production retrieval. It observes the retrieval
system and measures its output.

## 45. Current Retrieval Evaluation Baseline

The current five-query evaluation produced:

``` text
Semantic:
- Recall@5 = 1.0 for all five test cases
- Precision@5 = 0.4 for the pgvector case and 0.2 for each other case
- Reciprocal Rank = 1.0 for all five cases

Lexical:
- pgvector query retrieved chunks 6 and 7
- Redis query retrieved chunk 8
- JWT query returned no results
- semantic + lexical query retrieved chunk 11
- embeddings query returned no results

Hybrid/RRF:
- Current top-5 rankings match the semantic results for all five cases
```

These are development baseline measurements for the current five-case dataset,
not a broad benchmark.

The lexical JWT and embeddings failures are informative rather than
necessarily bugs: those relevant chunks were semantically related to their
queries but did not contain the corresponding exact searchable terms needed by
the current PostgreSQL FTS configuration.

The current hybrid baseline matching semantic retrieval means RRF did not
change the top-5 ordering for these five queries. More diverse evaluation
cases are needed before drawing broader conclusions about hybrid retrieval.

## 46. Evaluation Architecture

``` text
retrieval_dataset.py
        ↓
RetrievalTestCase
        ↓
retrieval_evaluator.py
        ↓
Semantic / Lexical / Hybrid retrieval
        ↓
retrieval_metrics.py
        ↓
Per-query RetrievalEvaluationResult
        ↓
retrieval_summary.py
        ↓
Aggregated Recall / Precision / MRR
        ↓
retrieval_comparison.py
        ↓
Strategy comparison
```

Evaluation remains separate from the production RAG pipeline.

## 47. Current API RAG Endpoints

The current RAG layer includes endpoints for progressively testing the
pipeline:

``` text
POST /rag/context
POST /rag/prompt
POST /rag/answer
```

The stages correspond to:

``` text
context assembly
      ↓
prompt construction
      ↓
LLM answer generation + sources
```

## 48. Current AI Status

``` text
Semantic retrieval                     ✓
RAG context assembly                   ✓
Prompt construction                    ✓
Local LLM generation                   ✓
Sources / citations                    ✓
Relevance threshold                    ✓
Neighbor expansion                     ✓
Context budgeting                      ✓
Anchor-aware retrieval                 ✓
Anchor diversity                       ✓
Hybrid semantic + lexical retrieval   ✓
RRF score fusion                       ✓
Retrieval evaluation                   ✓
RAG answer-quality evaluation         ✓
Contextual retrieval                   ✓
Conversation persistence                ✓
Conversation history                   ✓
Conversation-aware query representation ✓
Query rewriting                        ✓
Conversation-aware retrieval            ✓
Conversation-aware prompting            ✓
Semantic older-message retrieval       ✓
End-to-end conversational RAG          ✓
AI Knowledge Assistant                  ✓
Assistant API contract                  ✓
Assistant-specific error handling      ✓
End-to-end Assistant API testing       ✓
```

## 49. Current Roadmap

``` text
Backend Foundation
       ↓
Authentication
       ↓
Notes
       ↓
Search
       ↓
Pagination
       ↓
Indexing
       ↓
API Validation / Error Design
       ↓
Redis
       ↓
pgvector
       ↓
Local Embeddings
       ↓
Embedding Ingestion
       ↓
Semantic Search
       ↓
RAG Context Assembly
       ↓
Prompt Construction
       ↓
LLM Generation
       ↓
Sources / Citations
       ↓
Retrieval Quality / Hybrid Search
       ↓
Retrieval Evaluation
       ↓
RAG Answer-Quality Evaluation
       ↓
Contextual Retrieval
       ↓
Conversation Persistence
       ↓
Conversational RAG
       ↓
AI Knowledge Assistant ✓
       ↓
iOS Integration / AI Features
       ↓
Testing / Hardening
       ↓
Docker
       ↓
Deployment
```

## 50. Deliberately Deferred Work

### Chunking

Current implementation is character-based with `1000 / 200`. More
sophisticated document-aware chunking can come later.

### Embedding Performance

Embeddings are currently generated synchronously, one chunk at a time.
Batching/background processing can be introduced if needed.

### Redis

Semantic-search caching is not currently implemented.

### Embedding Provider Resilience

Retry/backoff/timeout hardening can be introduced later.

### Retrieval

The current hybrid/FTS implementation is intentionally simple. More advanced
lexical matching, weighting, query parsing, and vector indexes can be
introduced only when evaluation shows they are needed.

### Evaluation

The current retrieval dataset contains five representative test cases and
should grow as the knowledge base and retrieval requirements grow. Do not
optimize against five queries alone.

RAG answer-quality evaluation is now implemented for the current evaluation
dataset. It measures context relevance, answer faithfulness, and citation
correctness. The current evaluation remains a development baseline rather
than a broad benchmark.

## 51. Specialized Chat Strategy

``` text
AI KNOWLEDGE PLATFORM
│
├── MAIN PROJECT CHAT
│   ├── Architecture
│   ├── Roadmap
│   ├── Feature decisions
│   ├── Database/schema
│   ├── Integration
│   ├── project-context.md
│   └── Git milestones
│
├── REDIS CHAT
│   ├── Redis-specific implementation
│   ├── Redis testing
│   └── Redis debugging
│
├── PGVECTOR / AI CHAT
│   ├── pgvector
│   ├── embeddings
│   ├── chunking
│   ├── semantic retrieval
│   ├── hybrid retrieval
│   ├── RAG
│   └── retrieval evaluation
│
└── FUTURE SPECIALIZED CHATS
```

Redis fundamentals have already been learned and should not be re-taught
unless explicitly requested.

The Main Project Chat remains the architectural owner.

## 52. Specialized Chat Workflow

``` text
Main Project Chat
       ↓
Identify feature requirement
       ↓
Specialized Chat
       ↓
Build focused feature
       ↓
Test feature
       ↓
Return to Main Project Chat
       ↓
Integrate / verify
       ↓
Update project-context.md
       ↓
Git milestone
```

Dedicated chats are for large independent technical areas, not every small
feature.

## 53. Git Strategy

Git/GitHub are used throughout the project.

Completed milestones include:

``` text
Initial project setup
Add application configuration
Add Alembic database migrations
Add clean FastAPI architecture
Add user CRUD and exception handling
Add database constraints and pagination
Add notes feature
Add secure user registration
Add JWT authentication
Add JWT protected routes
Secure note ownership
Refine authentication and token handling
Add note search
Improve note search with PostgreSQL full-text search
Add paginated note responses
Add note query index
Standardize API error responses
Strengthen API input validation
Add Redis notes caching
Integrate pgvector semantic search and embeddings
Build initial RAG pipeline
Add retrieval relevance controls
Add hybrid retrieval with RRF
Add retrieval evaluation pipeline
Add RAG answer-quality evaluation
Add contextual retrieval
Add conversation persistence and APIs
Add conversational RAG
Add semantic retrieval of older conversation messages
Add AI Knowledge Assistant
```

The retrieval evaluation milestone establishes a baseline before further
retrieval or RAG quality changes.

## 54. Development Workflow

``` text
Plan
 ↓
Implement
 ↓
Test
 ↓
Integrate
 ↓
Verify
 ↓
Update project-context.md
 ↓
Git commit
```

Do not move to the next major subsystem while the current integration is
unverified.

## 55. Project Context Maintenance

`project-context.md` is the durable project-level source of context across
conversations.

It describes current truth, not a diary.

When architecture changes:

1. Update the relevant section.
2. Remove obsolete descriptions.
3. Keep important architectural decisions.
4. Do not append contradictory historical states.

Do not store every debugging mistake, terminal command, temporary test data,
abandoned implementation, full source code, or detailed lesson transcript.

Git history preserves implementation history. Source code preserves
implementation details.

## 56. Source-of-Truth Hierarchy

When information conflicts:

``` text
Actual source code
      +
Database / migrations
      +
Git history
      +
project-context.md
      +
Current conversations
```

If `project-context.md` conflicts with the actual implementation, verify the
implementation and update the context file.

## 57. Current Project State

The project now has a complete traditional backend foundation, measured hybrid
retrieval, contextual retrieval, answer-quality evaluation, a complete
Conversational RAG pipeline, and a product-facing AI Knowledge Assistant:

``` text
FastAPI
SQLAlchemy
PostgreSQL
Alembic
Pydantic
JWT authentication
Argon2 password hashing
Authorization
User ownership
Notes CRUD
PostgreSQL FTS
Pagination
Database indexing
API error contracts
Input validation
Redis caching
pgvector
Ollama embeddings
Embedding ingestion
Semantic search
RAG context assembly
Prompt construction
Local LLM generation
Sources / citations
Retrieval relevance controls
Neighbor expansion
Context budgeting
Anchor-aware retrieval
Anchor diversity
Hybrid retrieval
RRF
Retrieval evaluation
RAG answer-quality evaluation
Contextual retrieval
Conversation persistence
Conversation APIs
Conversation history
Conversation-aware query rewriting
Conversation-aware retrieval
Conversation-aware prompting
Semantic older-message retrieval
End-to-end Conversational RAG
AI Knowledge Assistant
Assistant API contract and `/assistant/chat`
Assistant-specific error handling
End-to-end Assistant API validation
```

The project has moved from:

``` text
Semantic Retrieval
        ↓
Measured Hybrid Retrieval
        ↓
RAG Pipeline
        ↓
Evaluated RAG
        ↓
Contextual Retrieval
        ↓
Conversational RAG
        ↓
AI Knowledge Assistant
```

## 58. Immediate Next Direction

The AI Knowledge Assistant milestone is now complete and has been validated
through the public `/assistant/chat` API.

The next major direction is iOS/UIKit integration, followed by broader
automated testing and production hardening.

Potential next areas include:

``` text
AI Knowledge Assistant
       ↓
iOS/UIKit integration
       ↓
Broader automated testing
       ↓
Production hardening
       ↓
Docker
       ↓
Deployment
```

Retrieval, RAG, and conversation behavior should continue to be evaluated as
the system grows. Existing evaluation baselines should be preserved rather
than optimized away.

## 59. Contextual Retrieval

Contextual retrieval was added so each chunk has both its original content
and retrieval-oriented contextual content:

``` text
NoteChunk
├── content              # exact original chunk
└── contextual_content   # retrieval-oriented representation
```

The important separation is:

``` text
Original chunk content
        ↓
source / context shown to LLM

Contextual content
        ↓
embedding generation / semantic retrieval
```

`ContextualizationService` uses the local LLM to generate a concise contextual
description from the full note and the individual chunk. The contextualized
representation is stored together with the original chunk.

Current ingestion flow:

``` text
Note
 ↓
Chunking
 ↓
Contextualization
 ↓
contextual_content
 ↓
Embedding
 ↓
NoteChunk
```

The current implementation makes one LLM contextualization call per chunk.
Batching, background processing, retries, and timeout hardening remain deferred.

Existing test data was deleted before introducing the new contextual retrieval
schema, so no embedding backfill was required.

## 60. RAG Answer-Quality Evaluation

RAG evaluation now extends beyond retrieval quality:

``` text
Question
  ↓
Retrieval
  ↓
Context
  ↓
LLM Answer
  ↓
Answer Quality Evaluation
  ├── Context Relevance
  ├── Faithfulness
  └── Citation Correctness
```

The current evaluation dataset contains five project-specific test cases and
fifteen expected facts.

Current development baseline:

``` text
Test cases:                    5
Expected facts:                15
Supported facts:               15
Unsupported facts:              0
Average context relevance:   1.00
Faithful answers:               5 / 5
Unfaithful answers:             0 / 5
Citation-correct answers:      4 / 5
Citation-incorrect answers:     1 / 5
```

The evaluation uses dedicated LLM judges with strict outputs for supported
facts, faithfulness, and citation correctness.

Citation correctness currently evaluates whether the cited/source material
supports the answer. Explicit citation-marker placement is not yet the focus.

The dataset is intentionally small and is a development baseline, not a broad
benchmark.

## 61. Conversation Architecture

Conversational RAG extends the single-turn pipeline:

``` text
Single-turn:
User Question
      ↓
Retrieval
      ↓
Context
      ↓
LLM
      ↓
Answer
```

into:

``` text
Conversation
      ↓
Conversation History
      ↓
Query Understanding / Rewriting
      ↓
Hybrid Note Retrieval
      ↓
Context Assembly
      ↓
Conversation-Aware Prompt
      ↓
LLM
      ↓
Answer
```

Core architectural distinction:

- Conversation history helps understand user intent, references, and pronouns.
- User note retrieval remains the authoritative knowledge source.
- Previous assistant answers are not treated as authoritative knowledge.
- Conversation history must not be inserted directly into note retrieval.
- Retrieval remains scoped to the authenticated user's notes.

## 62. Conversation Persistence

Two new models were introduced:

``` text
Conversation
├── id
├── user_id
├── title
├── created_at
└── updated_at
```

``` text
ConversationMessage
├── id
├── conversation_id
├── role
├── content
├── embedding
└── created_at
```

`ConversationMessage.embedding` uses:

``` text
vector(768)
```

and is non-nullable because existing test conversation data was deleted before
the embedding migration. No backfill mechanism is required for the current
database state.

Conversation messages are persisted in PostgreSQL.

Conversation ownership is enforced through the authenticated user's ID. Client
input must never be trusted to identify the owner.

## 63. Conversation APIs

Current conversation lifecycle API:

``` text
POST   /conversations
GET    /conversations
GET    /conversations/{conversation_id}/messages
POST   /conversations/{conversation_id}/messages
DELETE /conversations/{conversation_id}/messages/{message_id}
DELETE /conversations/{conversation_id}
```

Conversation and message not-found cases use stable API error codes:

``` text
CONVERSATION_NOT_FOUND
MESSAGE_NOT_FOUND
```

All conversation APIs have been end-to-end tested.

## 64. Conversation Context

`ConversationContext` is the application-level representation used while
processing a conversational request:

``` text
ConversationContext
├── history
└── current_message
```

Each history turn contains:

``` text
role: user | assistant
content
```

The current user message remains separate from prior history.

Persistent database messages and `ConversationContext` are intentionally
different concepts:

``` text
PostgreSQL messages
        ↓
bounded / selected history
        ↓
ConversationContext
```

## 65. Query Rewriting

Conversational RAG uses a dedicated `QueryRewritingService`.

The rewriting stage converts a conversational message into a standalone
retrieval query when necessary.

The important rule is:

``` text
Current message = primary source of intent
Conversation history = context for resolving ambiguity
```

A self-contained question should remain self-contained.

For example:

``` text
Conversation:
User: What is pgvector?

Current:
What are embeddings?

Rewritten query:
What are embeddings?
```

Previous topics must not be injected into an already clear question merely
because the topics are related.

For genuinely context-dependent messages:

``` text
User: What is pgvector?
Current: How does it store vectors?

Rewritten:
How does pgvector store vectors?
```

The rewriting model must:

- preserve current-message intent
- resolve genuine pronouns and references
- use only necessary conversation context
- avoid broadening or redirecting the query
- preserve user terminology where possible
- never answer the question
- return only the final standalone retrieval query

## 66. Conversational Retrieval

Conversational RAG uses the rewritten query for note retrieval:

``` text
ConversationContext
       ↓
QueryRewritingService
       ↓
Rewritten Query
       ↓
Hybrid Note Retrieval
       ↓
RRF
       ↓
Anchor Diversity
       ↓
Neighbor Expansion
       ↓
Context Budget
       ↓
Retrieved NoteChunks
```

The original current message is used later for the final conversational prompt.

This creates an intentional separation:

``` text
Rewritten query
    → retrieval

Original current message
    → final user-facing answer prompt

Conversation history
    → understanding + final prompt only
```

Raw conversation history is never concatenated into the note retrieval query.

Conversation messages are never represented as `RetrievedChunk` objects.

## 67. Semantic Retrieval of Older Conversation Messages

Conversation context uses both guaranteed recent messages and semantically relevant
older messages.

Current flow:

``` text
Current user question
        ↓
Recent conversation messages
        +
Semantic search over older conversation messages
        ↓
Deduplicate by message ID
        ↓
Chronological ordering
        ↓
ConversationContext
```

Configuration:

``` env
RAG_CONVERSATION_HISTORY_LIMIT=10
RAG_CONVERSATION_RELEVANT_MESSAGE_LIMIT=5
```

Recent messages are always included within the configured history window.

The current message is embedded and used to search older messages belonging only
to the same conversation. Recent message IDs are excluded from the semantic
older-message search to prevent duplication.

Every newly stored user and assistant conversation message receives a 768
dimensional embedding.

The architecture keeps embedding generation in `EmbeddingService`; database
retrieval remains in `ConversationRepository`; transaction and orchestration
remain in `ConversationService`.

Conversation-message semantic retrieval is used to recover older conversational
context. It is not treated as authoritative knowledge for factual answers.

## 68. Conversational Prompting

The final conversational prompt contains:

``` text
Conversation history
+
Retrieved note context
+
Original current user question
```

The prompt explicitly distinguishes the roles of these inputs:

``` text
Conversation history
    → helps understand references and conversational context

Retrieved note context
    → only authoritative source for factual answers

Previous assistant answers
    → not authoritative unless supported by retrieved note context
```

The conversational system prompt enforces strict grounding:

- Retrieved note context is the only authoritative knowledge source.
- Conversation history is used only for references, pronouns, and continuity.
- Previous assistant answers are not factual evidence.
- The model must not use pretrained/general knowledge to fill missing information.
- If retrieved context is insufficient, the model must not infer, speculate, or complete unsupported facts.
- The model must answer only what the retrieved context supports.
- When the information is unavailable, the required fallback is: `I couldn't find that information in your notes.`

The single-turn `SYSTEM_PROMPT` follows the same grounding contract without
conversation-history rules.

Application-level retrieval guards remain separate from prompt grounding. If
no usable chunks survive the RAG preparation pipeline, the application returns
the grounded fallback without invoking the LLM. Prompt grounding therefore
acts as a second safety layer for cases where context exists but does not fully
support the requested answer.

## 69. Shared RAG Generation Pipeline

`generate_answer()` and `generate_conversational_answer()` use the same private
retrieval/context preparation stage:

``` text
_prepare_rag_chunks()
    ↓
hybrid_retrieve()
    ↓
select_hybrid_results()
    ↓
limit_anchor_diversity()
    ↓
expand_with_neighbors()
    ↓
apply_context_budget()
```

Normal RAG then uses:

``` text
_prepare_rag_chunks()
    ↓
normal RAG prompt
    ↓
LLM
```

Conversational RAG uses:

``` text
query rewriting
    ↓
_prepare_rag_chunks()
    ↓
conversation-aware prompt
    ↓
LLM
```

This keeps shared retrieval behavior in one place while preserving different
final prompts. The retrieval pipeline itself remains conversation-agnostic.

## 70. AI Knowledge Assistant

The AI Knowledge Assistant is the product-facing orchestration layer built on
top of the existing Conversational RAG system. It does not replace RAG and
does not duplicate retrieval logic.

Architecture:

``` text
iOS / Client
      ↓
POST /assistant/chat
      ↓
AssistantRoute
      ↓
AssistantService
      ↓
ConversationService
      ↓
RAGService
      ↓
AssistantResponse
```

Responsibilities:

- `AssistantRoute` handles HTTP concerns and authentication dependency.
- `AssistantService` is the thin product-level orchestration layer.
- `ConversationService` owns conversation lifecycle, ownership, message history, persistence, and conversational RAG orchestration.
- `RAGService` owns retrieval, context preparation, prompting, and answer generation.
- `LLMService` owns communication with the local LLM provider.

### Public Assistant API

``` text
POST /assistant/chat
```

Request:

``` json
{
    "conversation_id": 12,
    "message": "Why did we use Redis for note caching?"
}
```

The client does not send `user_id`. The authenticated user identity comes from
the JWT. The requested conversation must already exist and belong to that user.

Response:

``` json
{
    "conversation_id": 12,
    "message_id": 47,
    "answer": "...",
    "sources": [
        {
            "note_id": 8,
            "chunk_id": 21,
            "chunk_index": 2,
            "content": "..."
        }
    ]
}
```

The public response intentionally hides internal retrieval metadata such as
cosine distance, RRF/hybrid score, anchor status, and retrieval source type.
The iOS client receives product-level source information rather than being
coupled to RAG implementation details.

### Assistant Error Handling

Assistant-specific infrastructure failure uses:

``` text
AIServiceUnavailableError
        ↓
AI_SERVICE_UNAVAILABLE
```

`LLMService` translates expected Ollama/API connection failures into this
application exception. Unexpected programming errors are not caught and
misclassified as AI-service failures. Existing authentication, conversation,
message, validation, and ownership error contracts remain unchanged.

### Grounding Contract

The Assistant uses two grounding layers:

``` text
Application retrieval guard
        ↓
No usable chunks → grounded fallback, no LLM call

Prompt grounding
        ↓
Context exists → LLM may answer only from supported retrieved evidence
```

This prevents empty retrieval from reaching generation and reduces hallucination
when retrieved context is present but incomplete.

### End-to-End Validation

The public Assistant API has been tested for:

- successful single-turn assistant requests
- conversational follow-up questions
- blank-message validation
- missing authentication
- non-existent conversations
- cross-user conversation access
- questions with no relevant knowledge
- AI-service unavailability
- persisted assistant messages
- persisted user messages

All planned Assistant API tests pass.

## 71. Core Project Principle

Build a real product, not a collection of tutorials.

Build a real product, not a collection of tutorials.

Every technology should answer:

> "What problem in our product requires this?"

The project should remain:

- Understandable
- Testable
- Incrementally built
- Secure
- Maintainable
- Production-oriented
- Strong enough to demonstrate real engineering ability
- Capable of evolving into a real AI/RAG system
