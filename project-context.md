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

## 28. Current AI Status

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

RAG Context Assembly            → Next
LLM Answer Generation           → Later
Sources / Citations             → Later
AI Assistant                    → Later
```

## 29. Current Roadmap

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
RAG Context Assembly       ← NEXT
       ↓
LLM Answer Generation
       ↓
Sources / Citations
       ↓
AI Assistant
       ↓
iOS Integration / AI Features
       ↓
Testing
       ↓
Docker
       ↓
Production Hardening
       ↓
Deployment
```

## 30. Deliberately Deferred Work

### Chunking

Current implementation is character-based with `1000 / 200`. More
sophisticated chunking can come later.

### Embedding Performance

Embeddings are currently generated synchronously, one chunk at a time.
Batching/background processing can be introduced if needed.

### Redis

Semantic-search caching is not currently implemented.

### Embedding Provider Resilience

Retry/backoff/timeout hardening can be introduced later.

### RAG

Current system has semantic retrieval but not yet:

``` text
retrieval
+
context assembly
+
LLM generation
+
sources/citations
```

## 31. Specialized Chat Strategy

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
│   └── RAG
│
└── FUTURE SPECIALIZED CHATS
```

Redis fundamentals have already been learned and should not be re-taught
unless explicitly requested.

The Main Project Chat remains the architectural owner.

## 32. Specialized Chat Workflow

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

Dedicated chats are for large independent technical areas, not every
small feature.

## 33. Git Strategy

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
```

Recommended current PGVector milestone:

``` text
feat: integrate pgvector semantic search and embeddings
```

## 34. Development Workflow

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

## 35. Project Context Maintenance

`project-context.md` is the durable project-level source of context
across conversations.

It describes current truth, not a diary.

When architecture changes:

1.  Update the relevant section.
2.  Remove obsolete descriptions.
3.  Keep important architectural decisions.
4.  Do not append contradictory historical states.

Do not store every debugging mistake, terminal command, temporary test
data, abandoned implementation, full source code, or detailed lesson
transcript.

Git history preserves implementation history. Source code preserves
implementation details.

## 36. Source-of-Truth Hierarchy

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

If `project-context.md` conflicts with the actual implementation, verify
the implementation and update the context file.

## 37. Current Project State

The project now has a complete traditional backend foundation plus an
initial AI retrieval layer:

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
```

The next transition is from semantic retrieval to RAG.

## 38. Immediate Next Direction

The next major phase is **RAG Context Assembly**.

The system already retrieves relevant chunks:

``` text
Question
   ↓
Query Embedding
   ↓
pgvector
   ↓
Relevant NoteChunks
```

Next:

``` text
User Question
      ↓
Semantic Retrieval
      ↓
Relevant Chunks
      ↓
Context Assembly
      ↓
LLM
      ↓
Grounded Answer
      ↓
Sources / Citations
```

The RAG system should be implemented incrementally rather than jumping
directly into a complete chatbot.

## 39. Core Project Principle

Build a real product, not a collection of tutorials.

Every technology should answer:

> "What problem in our product requires this?"

The project should remain:

-   Understandable
-   Testable
-   Incrementally built
-   Secure
-   Maintainable
-   Production-oriented
-   Strong enough to demonstrate real engineering ability
-   Capable of evolving into a real AI/RAG system

