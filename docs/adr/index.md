# Architecture Decision Records (ADR) Index

This directory contains Architecture Decision Records (ADRs) for the WorkChat project. ADRs document important architectural decisions made during the development process.

## What are ADRs?

Architecture Decision Records are lightweight documents that capture important architectural decisions made during a project. Each ADR describes:

- The context and problem being solved
- The decision made
- The rationale behind the decision
- The consequences of the decision

## ADR List

### ADR-001: Database Choice - SQLite with SQLModel
**Status**: Accepted  
**Date**: 2024  
**Context**: Need for embedded database with full-text search capabilities  
**Decision**: Use SQLite with FTS5 and SQLModel ORM  
**Rationale**: Zero-config deployment, excellent performance, integrated full-text search  

### ADR-002: Real-time Communication - Server-Sent Events
**Status**: Accepted  
**Date**: 2024  
**Context**: Need for real-time message delivery  
**Decision**: Use Server-Sent Events (SSE) instead of WebSockets  
**Rationale**: Simpler implementation, works with HTTP/2, easier to scale, sufficient for chat use case  

### ADR-003: Frontend Framework - React with TypeScript
**Status**: Accepted  
**Date**: 2024  
**Context**: Need for modern, type-safe frontend  
**Decision**: React 18 with TypeScript, Vite for build  
**Rationale**: Mature ecosystem, excellent TypeScript support, fast development server  

### ADR-004: State Management - TanStack Query
**Status**: Accepted  
**Date**: 2024  
**Context**: Need for server state management and caching  
**Decision**: TanStack Query for data fetching and caching  
**Rationale**: Excellent caching, background updates, optimistic updates, TypeScript support  

### ADR-005: Authentication - JWT with FastAPI Users
**Status**: Accepted  
**Date**: 2024  
**Context**: Need for stateless authentication  
**Decision**: JWT tokens with FastAPI Users library  
**Rationale**: Stateless, standard protocol, good library support, role-based access control  

### ADR-006: Multi-tenancy - Organization-Based Isolation
**Status**: Accepted  
**Date**: 2024  
**Context**: Need to support multiple teams/companies  
**Decision**: Every resource belongs to an organization  
**Rationale**: Clear data isolation, simple access control, scalable approach  

### ADR-007: Audit Trail - Immutable Log with JSON Diffs
**Status**: Accepted  
**Date**: 2024  
**Context**: Need for comprehensive change tracking  
**Decision**: Immutable audit log with before/after JSON snapshots  
**Rationale**: Complete change history, easy to query, supports compliance requirements  

### ADR-008: AI Integration - Model Context Protocol (MCP)
**Status**: Accepted  
**Date**: 2024  
**Context**: Need for AI assistant integration  
**Decision**: Expose chat operations via MCP server  
**Rationale**: Standard protocol, works with Claude and other AI assistants, clean API surface  

### ADR-009: Package Management - UV for Python
**Status**: Accepted  
**Date**: 2024  
**Context**: Need for fast, reliable Python package management  
**Decision**: Use UV instead of pip/poetry  
**Rationale**: 10-100x faster, single binary, lockfile support, pip-compatible  

### ADR-010: Testing Strategy - Pyramid Testing
**Status**: Accepted  
**Date**: 2024  
**Context**: Need for comprehensive test coverage  
**Decision**: Unit tests + Integration tests + E2E tests with Playwright  
**Rationale**: Multiple levels of confidence, catch different types of bugs, automated in CI  

## ADR Template

When creating new ADRs, use this template:

```markdown
# ADR-XXX: [Title]

**Status**: [Proposed | Accepted | Superseded | Deprecated]  
**Date**: YYYY-MM-DD  
**Authors**: [Name(s)]  

## Context

Brief description of the problem or situation requiring a decision.

## Decision

Clear statement of the decision made.

## Rationale

Explanation of why this decision was made, including:
- Alternatives considered
- Trade-offs evaluated
- Key factors in the decision

## Consequences

Expected outcomes of this decision:
- Positive consequences
- Negative consequences or risks
- Impact on other systems/decisions

## References

- Links to relevant discussions
- Related ADRs
- External resources
```

## Guidelines

1. **Keep it concise**: ADRs should be brief but complete
2. **Focus on the why**: Document the reasoning, not just the what
3. **Update status**: Mark ADRs as superseded when decisions change
4. **Link related ADRs**: Reference other ADRs that influenced or are influenced by this decision
5. **Date everything**: Include decision dates for historical context