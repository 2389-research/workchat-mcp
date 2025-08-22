# WorkChat Implementation Guide

This document provides detailed implementation guidance for developers working on the WorkChat codebase.

## Project Structure

```
workchat/
├── README.md                 # Main project documentation
├── IMPLEMENTATION.md         # This file - implementation details
├── docker-compose.yml        # Local development stack
├── Dockerfile               # Production container build
├── mkdocs.yml               # Documentation site config
├── pyproject.toml           # Python dependencies and config
├── uv.lock                  # Dependency lockfile
├── alembic.ini              # Database migration config
├── docs/                    # Documentation source files
│   ├── index.md
│   ├── quickstart.md
│   ├── architecture.md
│   └── adr/index.md
├── alembic/                 # Database migrations
│   └── versions/
├── workchat/               # Python package
│   ├── app.py              # FastAPI application
│   ├── database.py         # Database setup
│   ├── events.py           # SSE event streaming
│   ├── api/                # REST API endpoints
│   │   ├── channels.py
│   │   ├── messages.py
│   │   ├── search.py
│   │   └── audit.py
│   ├── models/             # SQLModel database models
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── channel.py
│   │   ├── message.py
│   │   └── audit_log.py
│   ├── auth/               # Authentication system
│   │   ├── config.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── services/           # Business logic layer
│   │   ├── audit.py
│   │   └── mcp_tools.py
│   ├── repositories/       # Data access layer
│   │   └── search.py
│   └── mcp/               # MCP server integration
│       ├── server.py
│       └── __main__.py
├── frontend/               # React frontend
│   ├── package.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   └── types.ts
│   └── tests/e2e/          # End-to-end tests
└── tests/                  # Backend tests
    ├── conftest.py
    ├── test_*.py
    └── fixtures/
```

## Development Workflow

### Setting Up Development Environment

1. **Clone and Setup**
   ```bash
   git clone <repository>
   cd workchat
   uv sync  # Install Python dependencies
   ```

2. **Database Setup**
   ```bash
   uv run alembic upgrade head  # Apply migrations
   ```

3. **Start Development Servers**
   ```bash
   # Backend (terminal 1)
   uv run uvicorn workchat.app:app --reload
   
   # Frontend (terminal 2)
   cd frontend
   npm install
   npm run dev
   ```

### Code Organization Principles

#### Backend Structure

**Models Layer** (`workchat/models/`)
- SQLModel classes that map to database tables
- Include validation logic and relationships
- Inherit from `BaseModel` for common fields (id, created_at)

```python
# Example model
class Message(BaseModel, table=True):
    channel_id: UUID = Field(foreign_key="channels.id")
    user_id: UUID = Field(foreign_key="users.id") 
    thread_id: Optional[UUID] = Field(foreign_key="messages.id")
    body: str = Field(max_length=10000)
    version: int = Field(default=1)
    edited_at: Optional[datetime] = None
```

**API Layer** (`workchat/api/`)
- FastAPI routers for REST endpoints
- Handle HTTP concerns (request/response, status codes)
- Delegate business logic to service layer
- Include comprehensive error handling

```python
@router.post("/", response_model=MessageResponse, status_code=201)
def create_message(
    message: MessageCreate,
    user: User = Depends(current_active_user),
    session: Session = Depends(get_session)
):
    # Validate and create message
    # Trigger audit logging
    # Broadcast SSE event
    return created_message
```

**Services Layer** (`workchat/services/`)
- Business logic and complex operations
- Coordinate between models and external systems
- Handle transactions and error scenarios
- Testable without HTTP dependencies

**Repositories Layer** (`workchat/repositories/`)
- Data access patterns
- Complex queries and database operations
- Search implementations

#### Frontend Structure

**Components** (`frontend/src/components/`)
- React functional components with TypeScript
- Use hooks for state management
- Follow single responsibility principle
- Include proper error boundaries

```typescript
interface ChannelSidebarProps {
  selectedChannelId?: string;
  onChannelSelect: (channelId: string) => void;
}

export function ChannelSidebar({ selectedChannelId, onChannelSelect }: ChannelSidebarProps) {
  const { data: channels, isLoading, error } = useQuery(['channels'], fetchChannels);
  // Component implementation
}
```

**Hooks** (`frontend/src/hooks/`)
- Custom React hooks for shared logic
- API integration patterns
- Real-time connection management

**API Client** (`frontend/src/api/`)
- Centralized API communication
- Type-safe request/response handling
- Authentication token management

### Database Development

#### Migration Workflow

1. **Create Migration**
   ```bash
   uv run alembic revision --autogenerate -m "Add new feature"
   ```

2. **Review Generated Migration**
   - Check the generated SQL in `alembic/versions/`
   - Verify data safety (no data loss)
   - Test both upgrade and downgrade paths

3. **Apply Migration**
   ```bash
   uv run alembic upgrade head
   ```

#### Model Development Patterns

**Base Model Usage**
```python
from workchat.models.base import BaseModel

class MyModel(BaseModel, table=True):
    # Automatically includes id: UUID and created_at: datetime
    name: str = Field(max_length=100)
    org_id: UUID = Field(foreign_key="organizations.id")
```

**Multi-tenancy Implementation**
Every model should be scoped to an organization:
```python
# In API endpoints
def get_resources(user: User = Depends(current_active_user)):
    return session.exec(
        select(Resource).where(Resource.org_id == user.org_id)
    ).all()
```

### Testing Implementation

#### Backend Testing

**Unit Tests** (`tests/test_*.py`)
```python
def test_create_message(client, auth_headers, sample_channel):
    response = client.post(
        "/api/messages",
        json={"channel_id": str(sample_channel.id), "body": "Test message"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["body"] == "Test message"
```

**Test Fixtures** (`tests/conftest.py`)
```python
@pytest.fixture
def sample_user(session):
    user = User(email="test@example.com", display_name="Test User")
    session.add(user)
    session.commit()
    return user
```

#### Frontend Testing

**E2E Tests** (`frontend/tests/e2e/`)
```typescript
test('user can post message', async ({ page }) => {
  await page.goto('/');
  await page.click('[data-testid="channel-item"]');
  await page.fill('[data-testid="message-input"]', 'Hello world');
  await page.click('[data-testid="send-button"]');
  await expect(page.locator('[data-testid="message"]')).toContainText('Hello world');
});
```

### Real-time Implementation

#### Server-Sent Events (SSE)

**Backend Event Streaming** (`workchat/events.py`)
```python
async def event_stream(user: User):
    queue = asyncio.Queue()
    connections[user.id] = queue
    
    try:
        while True:
            # Send heartbeat
            yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
            
            # Check for new events
            try:
                event = await asyncio.wait_for(queue.get(), timeout=15.0)
                yield f"data: {json.dumps(event)}\n\n"
            except asyncio.TimeoutError:
                continue
    finally:
        connections.pop(user.id, None)
```

**Frontend SSE Hook** (`frontend/src/hooks/useSSE.ts`)
```typescript
export function useSSE(url: string) {
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connected'>('disconnected');
  const [lastMessage, setLastMessage] = useState<SSEMessage | null>(null);

  useEffect(() => {
    const eventSource = new EventSource(url);
    
    eventSource.onopen = () => setConnectionStatus('connected');
    eventSource.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setLastMessage(message);
    };
    
    return () => eventSource.close();
  }, [url]);

  return { connectionStatus, lastMessage };
}
```

### Authentication & Security

#### JWT Implementation

**Token Generation** (`workchat/auth/config.py`)
```python
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

**Route Protection**
```python
@router.get("/protected")
def protected_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.display_name}"}
```

#### Input Validation

**Pydantic Schemas** (`workchat/schemas/`)
```python
class MessageCreate(BaseModel):
    channel_id: UUID
    body: str = Field(min_length=1, max_length=10000)
    thread_id: Optional[UUID] = None

    @validator('body')
    def validate_body(cls, v):
        if not v.strip():
            raise ValueError('Message body cannot be empty')
        return v.strip()
```

### MCP Integration Implementation

#### Server Setup (`workchat/mcp/server.py`)
```python
from fastmcp import FastMCP

mcp = FastMCP("WorkChat")

@mcp.tool()
def post_message(channel_id: str, body: str, user_email: str = "admin@example.com") -> str:
    """Post a message to a channel"""
    return post_message_logic(channel_id, body, user_email)

if __name__ == "__main__":
    mcp.run()
```

#### Tool Logic (`workchat/services/mcp_tools.py`)
```python
def post_message_logic(channel_id: str, body: str, user_email: str) -> str:
    """Business logic for posting messages via MCP"""
    with Session(engine) as session:
        # Validate user and channel
        # Create message
        # Audit log
        # Return message ID
```

### Performance Optimization

#### Database Query Optimization

**N+1 Query Prevention**
```python
# Bad: N+1 queries
messages = session.exec(select(Message)).all()
for message in messages:
    print(message.user.display_name)  # Each access hits DB

# Good: Single query with join
messages = session.exec(
    select(Message, User)
    .join(User, Message.user_id == User.id)
).all()
```

**FTS5 Search Implementation**
```python
def search_messages(query: str, org_id: UUID) -> List[Message]:
    # Use FTS5 for fast text search
    fts_results = session.exec(
        text("SELECT message_id FROM message_fts WHERE message_fts MATCH ?"),
        [query]
    ).all()
    
    # Join with actual message data, filtered by org
    if not fts_results:
        return []
    
    message_ids = [r[0] for r in fts_results]
    return session.exec(
        select(Message)
        .join(Channel, Message.channel_id == Channel.id)
        .where(Message.id.in_(message_ids), Channel.org_id == org_id)
    ).all()
```

#### Frontend Performance

**Query Optimization with TanStack Query**
```typescript
// Cache and background refresh
const { data: messages, isLoading } = useQuery(
  ['messages', channelId],
  () => fetchMessages(channelId),
  {
    staleTime: 30 * 1000, // 30 seconds
    cacheTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
  }
);
```

### Deployment Implementation

#### Docker Build Strategy

**Multi-stage Dockerfile**
```dockerfile
# Stage 1: Build dependencies
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim as builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-dev

# Stage 2: Runtime
FROM debian:bookworm-slim
COPY --from=builder /app/.venv /app/.venv
COPY . .
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "workchat.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### CI/CD Pipeline

**GitHub Actions Workflow**
```yaml
name: CI/CD
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync
      - run: uv run pytest
      - run: uv run ruff check
      
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker compose up -d
      - run: cd frontend && npm ci && npx playwright install
      - run: cd frontend && npm run test:e2e
```

### Debugging & Troubleshooting

#### Common Issues

**Database Connection Issues**
```bash
# Check database file
ls -la workchat.db

# Reset database
rm workchat.db
uv run alembic upgrade head
```

**SSE Connection Problems**
```bash
# Test SSE endpoint
curl -N http://localhost:8000/events

# Check for CORS issues in browser console
# Verify authentication token is valid
```

**Frontend Build Issues**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

#### Logging and Monitoring

**Backend Logging**
```python
import logging

logger = logging.getLogger(__name__)

@router.post("/messages")
def create_message(message: MessageCreate):
    logger.info(f"Creating message in channel {message.channel_id}")
    try:
        # Implementation
        logger.info(f"Message created with ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"Failed to create message: {e}")
        raise
```

**Performance Monitoring**
```python
import time

@router.get("/messages")
def list_messages(channel_id: UUID):
    start_time = time.time()
    result = get_messages(channel_id)
    duration = time.time() - start_time
    logger.info(f"Messages query took {duration:.3f}s")
    return result
```

### Contributing Guidelines

#### Code Style
- Follow PEP 8 for Python code
- Use TypeScript strict mode for frontend
- Run pre-commit hooks before committing
- Include docstrings for public functions

#### Pull Request Process
1. Create feature branch from main
2. Write tests for new functionality
3. Ensure all tests pass
4. Update documentation if needed
5. Submit PR with clear description

#### Git Commit Messages
```
feat: add message threading support
fix: resolve SSE reconnection issues
docs: update API documentation
test: add integration tests for search
refactor: simplify message creation logic
```

This implementation guide should be used alongside the main README.md and architecture documentation for a complete understanding of the WorkChat codebase.