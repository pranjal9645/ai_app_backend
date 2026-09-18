# AI Knowledge Platform — Project Context

## 1. Project Identity

**Project:** AI Knowledge Platform

**Goal:** Build a production-oriented, AI-powered personal knowledge platform that allows users to store, search, and interact with their own knowledge.

The project is being developed as a serious portfolio project for internship/full-time opportunities, with an iOS client and a backend capable of evolving into a complete AI/RAG system.

---

## 2. Product Vision

The platform will allow users to:

* Register and authenticate securely
* Create, view, update, and delete notes
* Search their own notes
* Use traditional PostgreSQL full-text search
* Later use semantic/vector search
* Later ask an AI assistant questions grounded in their own knowledge
* Access the platform through an iOS/UIKit client

Long-term AI pipeline:

```text
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

---

## 3. Technology Stack

### Backend

* Python
* FastAPI
* Pydantic
* Pydantic Settings
* SQLAlchemy
* PostgreSQL
* Alembic
* Redis
* pgvector
* Embedding model
* LLM API
* REST APIs

### Client

* Swift
* UIKit
* MVVM
* REST API integration

### Infrastructure / Engineering

* Git
* GitHub
* Docker
* Testing
* Logging
* Security
* Deployment

Docker and deployment will be introduced later when the application architecture is mature enough.

---

## 4. Architecture

Current backend architecture:

```text
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

Redis is coordinated at the service layer:

```text
FastAPI
   ↓
API Routes
   ↓
NoteService
   ├──────────────→ RedisService
   │                    ↓
   │                  Redis
   │
   └──────────────→ NoteRepository
                        ↓
                    PostgreSQL
```

Future AI architecture:

```text
iOS App
   ↓
HTTPS
   ↓
FastAPI
   ↓
Application / Service Layer
   ↓
PostgreSQL + Redis
   ↓
Embedding / AI Layer
   ↓
pgvector
   ↓
Semantic Search
   ↓
RAG
   ↓
LLM
```

### Architecture principle

Technologies are introduced because the product requires them, not merely to make the stack look impressive.

---

## 5. Repository Structure

Current structure:

```text
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

Important files currently include:

```text
app/
├── api/routes/
│   ├── auth.py
│   ├── users.py
│   └── notes.py
│
├── core/
│   ├── config.py
│   └── security.py
│
├── models/
│   ├── user.py
│   └── note.py
│
├── schemas/
│   ├── user.py
│   ├── note.py
│   └── error.py
│
├── services/
│   ├── auth_service.py
│   ├── user_service.py
│   ├── note_service.py
│   └── redis_service.py
│
├── repositories/
│   ├── user_repository.py
│   └── note_repository.py
│
└── db/
    ├── base.py
    ├── session.py
    └── redis.py
```

---

# 6. Configuration

Configuration is handled through `pydantic-settings`.

Environment variables currently include:

```text
APP_NAME
APP_VERSION
ENVIRONMENT

DATABASE_URL

JWT_SECRET_KEY
JWT_ALGORITHM
JWT_ACCESS_TOKEN_EXPIRE_MINUTES

REDIS_URL
```

`.env` is ignored by Git.

`.env.example` documents required configuration without exposing secrets.

---

# 7. Database

Database:

```text
PostgreSQL
Database: ai_knowledge_db
```

SQLAlchemy is used as the ORM.

Alembic is the migration system.

`Base.metadata.create_all()` is no longer used by the application. Schema changes are managed through Alembic migrations.

---

# 8. Current Database Models

## User

Conceptually:

```text
User
├── id
├── name
├── email
└── password_hash
```

Important constraints:

* `id` is the primary key
* `email` is unique
* `email` is required
* `name` is required
* `password_hash` is required

---

## Note

Conceptually:

```text
Note
├── id
├── title
├── content
├── user_id
├── created_at
└── updated_at
```

Relationship:

```text
User
  │
  └── 1 → many
          Notes
```

`user_id` has:

```text
ForeignKey("users.id", ondelete="CASCADE")
```

and is indexed because note queries frequently filter by user.

---

# 9. Database Migrations

Alembic is fully integrated.

Migration history has covered:

* Initial users table
* User constraints
* Notes table
* Password hashing field
* Cascade deletion
* Search-related database evolution where required
* Note `user_id` index
* Other schema changes through Alembic

Current rule:

```text
Schema change
      ↓
Alembic migration
      ↓
alembic upgrade head
```

Do not manually modify production schema outside the migration process.

---

# 10. Authentication

Authentication uses:

* Argon2 password hashing through `pwdlib`
* JWT access tokens through `PyJWT`
* FastAPI `OAuth2PasswordBearer`

Registration:

```text
POST /users/
```

Login:

```text
POST /auth/login
```

Current login flow:

```text
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

JWT contains the user ID as `sub` and an expiration time.

---

# 11. Current User

Protected routes use:

```text
get_current_user()
```

Flow:

```text
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

```text
GET /users/me
```

Important security behavior:

* Missing token → 401
* Invalid token → 401
* Expired token → 401
* Malformed `sub` → 401
* Deleted user → authentication failure
* Valid token → current user returned

The iOS client will use this flow after login.

---

# 12. Authorization / Note Ownership

Users can only access their own notes.

The client does **not** provide the owner ID for note operations.

Instead:

```text
JWT
 ↓
Current User
 ↓
current_user.id
 ↓
Note operation
```

A user attempting to access another user's note receives a not-found response rather than being given information about the other user's resource.

Ownership checks are implemented in the service layer.

---

# 13. Current Notes API

Current note functionality includes:

```text
POST   /notes/
GET    /notes/
GET    /notes/{note_id}
PUT    /notes/{note_id}
DELETE /notes/{note_id}
GET    /notes/search
```

All note operations are authenticated.

---

# 14. Pagination

Pagination uses:

```text
skip
limit
```

Current constraints:

```text
skip >= 0
1 <= limit <= 100
```

Note list responses include:

```json
{
    "items": [],
    "total": 0,
    "skip": 0,
    "limit": 20,
    "has_more": false
}
```

This structure is intended to make client-side pagination straightforward for the iOS application.

---

# 15. Search

## PostgreSQL Full-Text Search

Current note search uses PostgreSQL full-text search.

Conceptually:

```text
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

Current search is traditional lexical/full-text search.

It is intentionally separate from the future semantic search system.

---

# 16. Database Indexing

Current important index:

```text
notes.user_id
```

Reason:

Most note queries contain:

```text
WHERE user_id = ...
```

The primary key already has database indexing.

The unique user email constraint also provides the necessary uniqueness support.

Future indexes will be added only when justified by actual query patterns.

Potential future examples:

```text
(user_id, created_at)
```

FTS:

```text
GIN index on tsvector
```

Vector search:

```text
pgvector HNSW / IVFFlat
```

These are not added prematurely.

---

# 17. API Error Design

API errors use a consistent structure:

```json
{
    "error": {
        "code": "NOTE_NOT_FOUND",
        "message": "Note not found"
    }
}
```

Stable machine-readable error codes include:

```text
USER_ALREADY_EXISTS
USER_NOT_FOUND
NOTE_NOT_FOUND
AUTHENTICATION_FAILED
```

Important principle:

```text
iOS should rely on `code`,
not exact English `message`.
```

Internal database/provider details should not be exposed to clients.

---

# 18. API Input Validation

Pydantic validates API boundaries.

Current examples:

### User

```text
name:
    min 2
    max 100

email:
    valid email format

password:
    min 8
    max 128
```

Names are stripped and blank names are rejected.

Passwords are **not** stripped because changing a password silently is undesirable.

### Notes

```text
title:
    min 1
    max 255

content:
    min 1
```

Blank title/content values are rejected.

Pagination is constrained using FastAPI query validation.

Important distinction:

```text
Pydantic validation
        =
Is this input structurally valid?

Service logic
        =
Is this operation allowed?
```

---

# 19. Redis

Redis has now been **implemented and feature-tested**.

Redis is used as a performance/temporary data layer.

PostgreSQL remains the source of truth.

Redis configuration:

```text
REDIS_URL=redis://localhost:6379/0
```

Local connectivity has been verified.

---

## Redis Infrastructure

Redis connection:

```text
app/db/redis.py
```

Application-level Redis operations are centralized in:

```text
app/services/redis_service.py
```

`RedisService` currently supports:

```text
GET
SET
DELETE
EXISTS
GET_INT
INCREMENT
TTL
```

JSON serialization/deserialization is handled inside `RedisService`.

Application services do not directly perform Redis JSON serialization.

---

# 20. Redis Notes Cache

Currently only:

```text
GET /notes/
```

is cached.

The initial caching strategy is:

```text
Cache-aside
+
Version-based invalidation
+
TTL
```

---

## Cache Version

Version key:

```text
notes:user:{user_id}:version
```

Example:

```text
notes:user:7:version
```

---

## List Cache Key

Cache key:

```text
notes:user:{user_id}:v:{version}:list:{skip}:{limit}
```

Example:

```text
notes:user:7:v:3:list:0:20
```

This provides:

* user isolation
* pagination isolation
* version-based invalidation
* simple debugging

---

## Cache Read Flow

```text
GET /notes/
      ↓
Get user's cache version
      ↓
Build versioned key
      ↓
Redis GET
   ↙       ↘
 HIT       MISS
  ↓          ↓
Return    PostgreSQL
             ↓
       NoteListResponse
             ↓
      model_dump(mode="json")
             ↓
        Redis SET
         TTL 60 sec
             ↓
          Return
```

Cached data is JSON-compatible.

SQLAlchemy model objects are never stored directly in Redis.

---

# 21. Redis TTL

Current notes-list cache TTL:

```text
60 seconds
```

Versioning makes old cache keys logically obsolete immediately after a mutation.

TTL eventually removes old keys physically.

---

# 22. Redis Cache Invalidation

Cache invalidation is coordinated by `NoteService`.

Current helper:

```text
invalidate_notes_cache(user_id)
```

It increments:

```text
notes:user:{user_id}:version
```

Invalidation happens after successful PostgreSQL mutations.

### Create

```text
PostgreSQL INSERT
      ↓
version++
```

### Update

```text
PostgreSQL UPDATE
      ↓
version++
```

### Delete

```text
PostgreSQL DELETE
      ↓
version++
```

Database mutation occurs before cache invalidation.

---

# 23. Why Version-Based Invalidation

We do not use Redis `KEYS` to find and delete every pagination key.

For example:

```text
notes:user:7:v:5:list:0:20
notes:user:7:v:5:list:20:20
notes:user:7:v:5:list:40:20
```

After a mutation:

```text
version 5 → version 6
```

New requests use:

```text
notes:user:7:v:6:...
```

Old version-5 entries are no longer used and eventually expire through TTL.

---

# 24. Redis Responsibilities

Current architecture:

```text
NoteRepository
    ↓
PostgreSQL only

RedisService
    ↓
Redis operations only

NoteService
    ↓
Coordinates PostgreSQL + Redis
```

Redis is intentionally **not** placed inside `NoteRepository`.

The repository remains responsible for persistence.

The service layer decides when caching is useful.

---

# 25. Redis Testing

Redis implementation has been manually feature-tested for:

* Redis connectivity
* JSON SET/GET
* Version initialization
* Version increment
* Cache MISS
* Cache HIT
* TTL
* Pagination-specific keys
* User-specific cache keys
* Create invalidation
* Update invalidation
* Delete invalidation
* TTL expiration

Expected lifecycle:

```text
First GET
    ↓
MISS
    ↓
PostgreSQL
    ↓
Redis cache

Second identical GET
    ↓
HIT
    ↓
Redis

Create / Update / Delete
    ↓
PostgreSQL mutation
    ↓
version++

Next GET
    ↓
new version
    ↓
MISS
    ↓
PostgreSQL
    ↓
fresh Redis cache
```

Automated Redis service tests are also being developed in:

```text
tests/test_redis_service.py
```

---

# 26. Deferred Redis Work

Not currently cached:

```text
GET /notes/{note_id}
GET /notes/search
```

Search caching is intentionally deferred because the search architecture will evolve toward semantic/vector search.

Redis failure-handling hardening is also deferred.

Future production behavior may allow Redis failures to fall back to PostgreSQL rather than breaking note retrieval.

This will be implemented only when production hardening becomes relevant.

---

# 27. AI / pgvector Status

Current status:

```text
PostgreSQL
    ✓

FastAPI
    ✓

SQLAlchemy
    ✓

Alembic
    ✓

Authentication
    ✓

Authorization
    ✓

Note CRUD
    ✓

PostgreSQL FTS
    ✓

Pagination
    ✓

Database indexing
    ✓

API error design
    ✓

Input validation
    ✓

Redis
    ✓

pgvector
    → Next major area

Embeddings
    → Later

Semantic Search
    → Later

RAG
    → Later

LLM Assistant
    → Later
```

---

# 28. Current Development Direction

The current roadmap is:

```text
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
API validation/error design
       ↓
Redis
       ↓
pgvector
       ↓
Embeddings
       ↓
Semantic Search
       ↓
RAG
       ↓
LLM Assistant
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

The next major technical area is **pgvector**.

---

# 29. Specialized Chat Strategy

Because this project will span many months, large independent technical areas use dedicated chats.

```text
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
│   ├── semantic search
│   └── RAG
│
└── FUTURE SPECIALIZED CHATS
```

Redis fundamentals have already been learned and should **not** be re-taught unless explicitly requested.

The Redis chat is now an implementation/debugging workspace.

The Main Project Chat remains the architectural owner.

---

# 30. Specialized Chat Workflow

```text
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

Do not create a separate chat for every small feature.

Dedicated chats are for large independent technical areas.

---

# 31. Git Strategy

Git/GitHub are used throughout the project.

Important completed milestones include:

```text
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
```

Current Redis milestone:

```text
Add Redis notes caching
```

Meaningful commits should represent stable project milestones rather than every tiny change.

---

# 32. Development Workflow

For major features:

```text
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

Do not move to the next major subsystem while the current integration is unverified.

---

# 33. Project Context Maintenance

`project-context.md` is the durable project-level source of context across conversations.

It should describe **current truth**, not act as a diary.

When architecture changes:

1. Update the relevant section.
2. Remove obsolete descriptions.
3. Keep important architectural decisions.
4. Do not append contradictory historical states.

Do not store:

* Every debugging mistake
* Every terminal command
* Temporary test data
* Abandoned implementations
* Full source code
* Detailed lesson transcripts

Git history preserves implementation history.

Source code preserves implementation details.

---

# 34. Source-of-Truth Hierarchy

When information conflicts, use:

```text
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

If `project-context.md` conflicts with the actual implementation, verify the implementation and update the context file.

---

# 35. Current Project State

The project has moved beyond basic backend learning.

The following foundation is now operational:

```text
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
```

The project is now transitioning from the **traditional backend foundation** into the **AI retrieval layer**.

---

# 36. Immediate Next Direction

Next major area:

```text
pgvector
```

The goal is to add vector storage/search to PostgreSQL without prematurely implementing the entire AI system.

The next progression will be:

```text
pgvector
    ↓
Understand vector storage/indexing
    ↓
Integrate with PostgreSQL
    ↓
Design note/chunk embedding storage
    ↓
Embeddings
    ↓
Semantic Search
    ↓
RAG
```

The AI architecture should continue to be built incrementally.

---

# 37. Core Project Principle

Build a real product, not a collection of tutorials.

Every technology should answer:

> "What problem in our product requires this?"

The project should remain:

* Understandable
* Testable
* Incrementally built
* Secure
* Maintainable
* Production-oriented
* Strong enough to demonstrate real engineering ability
* Capable of evolving into an AI/RAG system


