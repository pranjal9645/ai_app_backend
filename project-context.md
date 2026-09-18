# AI Knowledge Platform — Project Context

## 1. Project Overview

The AI Knowledge Platform is a long-running portfolio project designed to demonstrate production-oriented backend, database, AI, and iOS development skills.

The core idea is a personal knowledge platform where users can store notes and documents, search their knowledge, and eventually interact with an AI assistant that answers questions using their own stored knowledge.

The project will gradually evolve from a traditional CRUD application into an AI-powered knowledge system using semantic search and Retrieval-Augmented Generation (RAG).

---

## 2. Main Goal

Build a serious portfolio project that demonstrates:

* Backend API development
* Authentication and authorization
* PostgreSQL database design
* SQLAlchemy
* Database migrations
* Redis
* Semantic search
* pgvector
* Embeddings
* LLM integration
* RAG
* iOS client integration
* Testing
* Docker
* Deployment
* Production-oriented architecture

The technologies should be introduced because the product requires them, not simply to make the technology stack larger.

---

## 3. Technology Stack

### Client

* iOS
* Swift
* UIKit initially

### Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy

### Database

* PostgreSQL
* Alembic
* pgvector

### Infrastructure / Supporting Technologies

* Redis
* Git
* GitHub
* Docker
* Deployment platform to be selected later

### AI

* Embedding model
* LLM API
* Semantic search
* Retrieval-Augmented Generation (RAG)

---

## 4. High-Level Architecture

The eventual architecture is expected to look approximately like:

iOS App
↓
HTTPS
↓
FastAPI
↓
┌───────────────────────────────┐
│ Application / Service Layer   │
└───────────────────────────────┘
↓          ↓          ↓
PostgreSQL     Redis     AI Layer
↓                    ↓
pgvector            Embeddings
↓
Semantic Search
↓
RAG
↓
LLM

This architecture will be built progressively rather than all at once.

---

## 5. Development Philosophy

The project is being developed incrementally.

Each major version should leave the application in a usable state.

General progression:

MVP
↓
Authentication
↓
Secure user-owned data
↓
Traditional search
↓
Database optimization
↓
Redis
↓
pgvector
↓
Embeddings
↓
Semantic search
↓
RAG
↓
AI assistant
↓
Production hardening
↓
iOS integration / refinement
↓
Deployment

Do not prematurely implement future features before their prerequisites are understood.

---

# 6. Current Backend Structure

Current structure:

```text
ai-knowledge-platform/
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── users.py
│   │       ├── auth.py
│   │       └── notes.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── exceptions.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   └── note.py
│   │
│   ├── schemas/
│   │   ├── user.py
│   │   └── note.py
│   │
│   ├── services/
│   │   ├── user_service.py
│   │   ├── auth_service.py
│   │   └── note_service.py
│   │
│   ├── repositories/
│   │   ├── user_repository.py
│   │   └── note_repository.py
│   │
│   └── db/
│       ├── base.py
│       └── session.py
│
├── alembic/
├── tests/
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── project-context.md
```

The application follows:

```text
API Route
    ↓
Service
    ↓
Repository
    ↓
Database
```

Routes should primarily handle HTTP concerns.

Services contain application/business logic.

Repositories handle database access.

---

# 7. Database

Current database:

```text
PostgreSQL
    └── ai_knowledge_db
```

Current tables:

```text
users
  │
  │ 1
  │
  │ many
  ▼
notes
```

## Users

Current important fields:

* id
* name
* email
* password_hash

`email` is unique and non-null.

Passwords are never stored directly.

Passwords are hashed using Argon2 through `pwdlib`.

---

## Notes

Current important fields:

* id
* title
* content
* user_id
* created_at
* updated_at

`user_id` references `users.id`.

The foreign key uses:

```text
ON DELETE CASCADE
```

A database index exists on `notes.user_id` because notes are frequently queried by owner.

---

# 8. Database Migrations

Alembic is used for schema changes.

The project should not rely on:

```python
Base.metadata.create_all()
```

for normal application schema management.

Schema changes should be made through:

```text
Model change
    ↓
alembic revision --autogenerate
    ↓
Review migration
    ↓
alembic upgrade head
```

---

# 9. Authentication

Authentication currently uses:

* Password hashing with Argon2
* JWT access tokens
* OAuth2 bearer token extraction through FastAPI

Login flow:

```text
Email + Password
       ↓
AuthService
       ↓
Verify password
       ↓
Create JWT
       ↓
Return access token
```

Protected request:

```text
Authorization: Bearer <token>
                ↓
        get_current_user()
                ↓
          Decode JWT
                ↓
         Find User in DB
                ↓
        Current User object
```

JWT currently contains:

* `sub` → user ID
* `exp` → expiration time

Authentication failures use generic messages such as:

```text
Invalid email or password
```

to avoid unnecessarily revealing whether an account exists.

---

# 10. Authorization

Users can only access their own notes.

The client does not provide the owner ID for note creation or protected note operations.

Instead:

```text
JWT
 ↓
Current User
 ↓
current_user.id
 ↓
Note ownership
```

For operations on a specific note:

```text
Request note ID
      ↓
Does note exist?
      ↓
Does note belong to current user?
      ↓
Allow operation
```

A note belonging to another user is treated as not accessible.

---

# 11. Current API Features

## Users

Implemented:

```text
POST   /users/
GET    /users/
GET    /users/{user_id}
PUT    /users/{user_id}
DELETE /users/{user_id}
GET    /users/me
```

## Authentication

Implemented:

```text
POST /auth/login
```

## Notes

Implemented:

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

# 12. Search

The project currently supports two conceptual levels of search.

## Current search

PostgreSQL Full-Text Search is used for note searching.

The current implementation uses:

```text
to_tsvector()
        +
plainto_tsquery()
        +
@@
        +
ts_rank()
```

Search is restricted to the authenticated user's notes.

Search results are ranked using PostgreSQL text-search ranking.

---

## Future semantic search

Semantic search is not implemented yet.

Planned flow:

```text
User query
    ↓
Embedding model
    ↓
Query vector
    ↓
pgvector
    ↓
Similarity search
    ↓
Relevant note chunks
```

This will be implemented after pgvector and embeddings are properly learned.

---

# 13. Pagination

Note list and search responses currently return metadata:

```text
items
total
skip
limit
has_more
```

This is intended to support efficient client-side pagination, particularly for the future iOS application.

Current pagination uses offset/limit.

The project will not introduce a generic pagination abstraction prematurely.

---

# 14. Current Learning Progress

Completed:

```text
Python
↓
FastAPI
↓
Pydantic
↓
REST APIs
↓
PostgreSQL
↓
SQLAlchemy
↓
SQLAlchemy + FastAPI
↓
Alembic
↓
FastAPI architecture
↓
CRUD
↓
Authentication
↓
Authorization
↓
Basic note search
↓
PostgreSQL Full-Text Search
↓
Pagination
↓
Database indexing
```

Currently:

```text
Redis
```

Redis is being learned in a separate dedicated conversation using a structured lesson roadmap.

After Redis:

```text
pgvector
```

will be learned before integrating it into this project.

---

# 15. Git Strategy

Git and GitHub are part of the project from the beginning.

Major completed milestones should receive meaningful commits.

Examples of existing milestone commits include:

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
```

Future major milestones should also be committed.

---

# 16. Important Architectural Decisions

### Decision 1 — Layered architecture

Use:

```text
Routes → Services → Repositories → Database
```

Do not bypass layers without a clear reason.

### Decision 2 — JWT authentication

JWT access tokens are currently used for API authentication.

### Decision 3 — User ownership from authentication

Protected resources should derive ownership from the authenticated user rather than trusting a user ID supplied by the client.

### Decision 4 — PostgreSQL as the primary database

PostgreSQL is the primary persistent data store.

### Decision 5 — Alembic for migrations

Database schema evolution is managed through Alembic.

### Decision 6 — Incremental complexity

Redis, pgvector, embeddings, RAG, and LLM functionality will be introduced when the application reaches the stage where those technologies solve an actual problem.

---

# 17. Current Project Status

The project currently has a functional backend foundation with:

* User registration
* Secure password hashing
* JWT authentication
* Current-user authentication
* User CRUD
* Note CRUD
* Note ownership/authorization
* PostgreSQL
* SQLAlchemy
* Alembic
* PostgreSQL Full-Text Search
* Pagination
* Database indexing

The project is **not yet an AI/RAG system**.

The AI layer is intentionally being built later.

---

# 18. Immediate Next Direction

The immediate learning track is:

```text
Redis
   ↓
pgvector
   ↓
Integrate pgvector
   ↓
Document/note chunking
   ↓
Embedding generation
   ↓
Store embeddings
   ↓
Semantic search
   ↓
RAG
   ↓
AI assistant
```

The exact implementation details should be updated as architectural decisions are made.

---

# 19. Context Management Rules

This file is the project's durable context.

Whenever a major project decision, structural change, completed milestone, or important constraint is established, update this file.

Do not record every small coding detail.

The file should answer:

1. What are we building?
2. Why are we building it?
3. What technologies are being used?
4. What architecture are we following?
5. What has already been implemented?
6. What important decisions have been made?
7. What is currently being learned/built?
8. What comes next?

Individual feature implementation details belong in the relevant source code and Git history rather than becoming an unnecessarily large context file.
