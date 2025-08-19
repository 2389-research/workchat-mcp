## 🚧 Blueprint (Revision 0.1)

| Phase                      | Goal                            | Key Deliverables                                                                                   | Exit Criteria                                           |
| -------------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| **0 — Prep**               | Project bootstrap & CI          | Git repo, dev-container, Makefile, GitHub Actions (pytest + ruff), decision record (ADR-000)       | Green “hello-world” test in CI                          |
| **1 — Core Domain**        | Data schema + persistence slice | Pydantic models for all entities, Alembic migration, SQLite dev DB, Repository layer w/ unit tests | CRUD for Org & User passes tests                        |
| **2 — Auth & Session**     | Token-based auth scaffold       | Login / refresh endpoints, middleware, fixtures for test client                                    | Auth tests pass; protected route works                  |
| **3 — Channels & Threads** | Public channel operations       | Create/List/Join/Leave Channel APIs + Thread starter (root message)                                | Posting root message returns 201 + versioned row        |
| **4 — Messaging**          | Replies, edits, reactions       | Message POST/GET/PATCH, reaction endpoints, optimistic locking                                     | 95% branch coverage on messaging                        |
| **5 — Event Stream**       | Real-time SSE/WebSocket         | Presence, newMessage, unreadCount events; heartbeat                                                | Locust load test ≥5k concurrent clients w/ <200 ms push |
| **6 — Search**             | Full-text & filters             | Pg trgm (or SQLite FTS) integration, query parser, API                                             | Search returns ≤200 ms P95 for 100k msgs                |
| **7 — Audit & Admin**      | Immutable audit log             | Hook layer, ListAuditLogs w/ tail pagination                                                       | Admin can view JSON diff for edits                      |
| **8 — Packaging**          | Docker & deploy scripts         | `docker compose up`, dev/prod envs, Helm chart stub                                                | One-command spin-up on fresh laptop                     |
| **9 — MCP Wiring**         | Expose as MCP Server            | FastMCP decorators around APIs; stdio transport wrapper                                            | `listTools` shows chat-tool set in Claude               |
| **10 — Frontend MVP**      | Minimal chat UI                 | React + TanStack Query; Channel/Thread panes; SSE hook                                             | Manual smoke test passes                                |
| **11 — Hardening**         | Load, security, e2e             | Rate-limit, schema fuzz tests, OWASP baseline scan                                                 | Test matrix all green                                   |
| **12 — Docs & Handover**   | Dev guide & OpenAPI             | mkdocs site, ADR index, API reference                                                              | New dev can post a message <15 min                      |

> **Feedback loop** Run `Phase-Review` checklist after each phase; regroup if blockers appear.

---

## 🔨 Iterative Chunk → Step Decomposition

Below each **Chunk (Cx)** is split into **Steps (Sx.y)**.
Every step ≤ 2 dev-days, ≥ ½ day effort, always comes with tests.

<details>
<summary>Chunk C1 — Core Domain</summary>

| Step     | Task                                              | Tests                       |
| -------- | ------------------------------------------------- | --------------------------- |
| **S1.1** | Create monorepo, pre-commit (ruff, black, isort)  | Lint job runs               |
| **S1.2** | Add UV + `fastapi`, `sqlmodel`, `pytest`          | `pytest -q` shows 0 tests   |
| **S1.3** | Define `BaseModel` mixin with `id`, `created_at`  | Model serialises round-trip |
| **S1.4** | Implement Org & User SQLModel + Alembic migration | CRUD repo unit tests        |
| **S1.5** | Seed script for first Org + admin User            | Seeder asserts row counts   |

</details>

<details>
<summary>Chunk C2 — Auth & Session</summary>

| Step     | Task                                                |
| -------- | --------------------------------------------------- |
| **S2.1** | Integrate `fastapi-users` w/ JWT; config via `.env` |
| **S2.2** | `/login` & `/refresh` routes; pytest token fixture  |
| **S2.3** | Protect “/orgs/me” route; 401 vs 200 tests          |

</details>

<details>
<summary>Chunk C3 — Channels & Threads</summary>

| Step     | Task                                                   |         |
| -------- | ------------------------------------------------------ | ------- |
| **S3.1** | Channel table + repository                             |         |
| **S3.2** | POST `/channels` (create) + validation                 |         |
| **S3.3** | Membership table + \`/channels/{id}/join               | leave\` |
| **S3.4** | Thread starter: POST `/messages` with null `thread_id` |         |

</details>

<details>
<summary>… repeat pattern for remaining chunks C4–C12</summary>

Each chunk subdivided into 3-5 similar-sized steps following the above cadence.

</details>

---

## ✅ Right-Sizing Review

- **Atomic**: No step requires touching more than three files.
- **Parallel-isable**: Different chunks unblock in parallel after C2.
- **Test-First**: Each step specifies at least one failing test to start.
- **Continuous Value**: After every chunk, a running chat slice is demo-able.

---

## 🤖 Code-Gen LLM Prompt Series

> Copy-paste each block (in order) into your code-generation LLM.
> Prompts assume Python 3.12, FastAPI, SQLModel, Pytest.

### **Prompt P0 – Repository Bootstrap**

```text
You are an expert Python engineer.

TASK: Scaffold a clean repo named “workchat”.
Requirements:
- Use UV.
- Add dev-dependencies: pytest, pytest-asyncio, ruff, black, isort, httpx.
- Initialise basic folder layout: `workchat/` (package), `tests/`.
- Provide a `.pre-commit-config.yaml` enabling ruff+black.
- Include a GitHub Actions workflow that runs lint & tests on push.
Return only the diff or file listings necessary to create these files.
Write minimal placeholder code so `pytest` passes with zero tests.
```

---

### **Prompt P1 – Core Models**

```text
CONTEXT: Repo from P0.

TASK: Implement domain models Org and User using SQLModel.

Details:
- Base mixin with fields `id: UUID = Field(default_factory=uuid4, primary_key=True)` and `created_at: datetime = Field(default_factory=datetime.utcnow, index=True)`.
- Org: `name` (unique, 100 chars).
- User: `org_id` FK, `display_name`, `email` (unique), `role` Enum("admin","member").
- Create Alembic migration.
- Write `tests/test_models.py` asserting table creation and basic CRUD via an in-memory SQLite engine.

Return full file contents and the Alembic revision script.
```

---

### **Prompt P2 – Auth Scaffold**

```text
CONTEXT: Codebase after P1.

TASK: Add JWT auth with fastapi-users.

Steps:
1. Install fastapi-users[sqlalchemy], python-jose, passlib[bcrypt].
2. Configure UserDB model extending previous User.
3. Expose `/auth/jwt/login` and `/auth/jwt/refresh`.
4. Add a pytest fixture that yields an authenticated async client.
5. Tests: unauthenticated access to `/orgs/me` -> 401; authenticated -> 200.

Provide updated files and new tests only.
```

---

### **Prompt P3 – Channel CRUD**

```text
CONTEXT: Codebase after P2.

TASK: Implement public Channels.

Requirements:
- SQLModel Channel table: `name`, `description`, `is_system`.
- POST `/channels` (create), GET `/channels` (list), GET `/channels/{id}`.
- Business rule: name unique within org; return 400 otherwise.
- Tests covering create-list-duplicate.

Focus on endpoint code, schemas, and tests; omit docs, keep style consistent.
```

---

### **Prompt P4 – Thread & Message Posting**

```text
CONTEXT: Codebase after P3.

TASK: Add messaging.

1. SQLModel Message: `channel_id`, `thread_id`, `body`, `edited_at`, version column.
2. Posting root message creates new thread (`thread_id = id`).
3. Reply requires valid existing `thread_id`.
4. Endpoint: POST `/messages`, GET `/threads/{thread_id}` (paginated).
5. Tests: root vs reply logic, immutable edit (PATCH increments version).

Return new/modified files and tests.
```

---

### **Prompt P5 – SSE Event Stream**

```text
CONTEXT: Codebase after P4.

TASK: Implement server-sent events at `/events`.

Features:
- On connect, server streams presenceUpdate for current user (status=online).
- Broadcast newMessage to all connections on successful POST `/messages`.
- Heartbeat comment every 15 s.
- Use asyncio queue per connection.

Write integration test using httpx AsyncClient that asserts:
- Connect, post message, receive newMessage payload.

Return code and tests.
```

---

### **Prompt P6 – Search API**

```text
CONTEXT: Codebase after P5.

TASK: Integrate SQLite FTS5 for full-text search.

- Virtual table `message_fts` auto-indexed on Message insert/update.
- Endpoint GET `/search?q={query}&scope=channel:{id}`.
- Unit tests: insert 3 messages, search term returns correct ids.

Return migrations, repo layer, endpoint, tests.
```

---

### **Prompt P7 – Audit Log Hook**

```text
CONTEXT: Codebase after P6.

TASK: Add AuditLog model and middleware.

- Any PATCH to `/messages/{id}` inserts AuditLog row with JSON diff.
- Endpoint GET `/audit?limit=50` (admin-only).
- Tests: Editing message creates exactly one audit row with correct payload.

Return code and tests.
```

---

### **Prompt P8 – MCP Server Exposure**

```text
CONTEXT: Codebase after P7.

TASK: Wrap key operations as MCP tools using FastMCP.

Tools:
- `post_message(channel_id:str, body:str) -> str` returns message_id.
- `search(query:str) -> list[str]` returns snippets.
- `add_reaction(message_id:str, emoji:str) -> bool`.

Implement `server.py` that starts FastMCP stdio transport when `python -m workchat.mcp`.

Provide code and minimal doctest showing `list_tools()` output.
```

---

### **Prompt P9 – Docker & CI Release**

```text
CONTEXT: Codebase after P8.

TASK: Add Dockerfile and CI release.

- Multi-stage build; final image runs `uvicorn workchat.app:app --host 0.0.0.0 --port 8000`.
- GitHub Action on tag `v*` builds and pushes image to ghcr.io.

Return Dockerfile and updated workflow yaml.
```

---

### **Prompt P10 – Frontend Slice**

```text
CONTEXT: Backend running at localhost:8000.

TASK: Create frontend in React (Vite).

Features for first slice:
- Channel list sidebar (GET /channels)
- Thread view pane; Message composer.
- SSE hook to `/events` updating UI in real time.

Return project scaffolding (package.json), main components, and README run instructions.
```

---

### **Prompt P11 – E2E Tests & Hardening**

```text
CONTEXT: Full stack after P10.

TASK: Add Playwright tests.

Scenarios:
1. User logs in, joins channel, posts message, sees it appear.
2. Two browser contexts receive real-time updates.

Integrate into CI; failing tests break the build.
```

---

Each prompt explicitly depends on artifacts from the previous step, enforces tests, and incrementally wires the system end-to-end—no dangling code.

Happy building!
