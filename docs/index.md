# WorkChat Documentation

Welcome to WorkChat - a production-ready, real-time team chat application built with FastAPI, SQLModel, and modern web technologies.

## What is WorkChat?

WorkChat is a comprehensive team communication platform that provides:

- **Real-time messaging** with Server-Sent Events (SSE)
- **Channel-based organization** with threaded conversations  
- **Full-text search** using SQLite FTS5
- **Comprehensive audit logging** for all message operations
- **MCP (Model Context Protocol) integration** for AI assistant access
- **Multi-tenant organization support**
- **Modern React frontend** with TypeScript

## Getting Started

The fastest way to get WorkChat running:

```bash
git clone <repository>
cd workchat
docker compose up
```

→ Open [http://localhost:8000](http://localhost:8000) to access the API
→ Open [http://localhost:3000](http://localhost:3000) for the chat interface

For detailed setup instructions, see the [Quick Start Guide](quickstart.md).

## Architecture Overview

WorkChat follows a modern full-stack architecture:

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   React Frontend    │    │   FastAPI Backend   │    │   SQLite Database   │
│   (TypeScript)      │◄──►│   (Python)          │◄──►│   + FTS5 Search     │
│                     │    │                     │    │                     │
│ • TanStack Query    │    │ • SQLModel ORM      │    │ • Multi-tenant      │
│ • SSE Integration   │    │ • JWT Auth          │    │ • Audit Logs        │
│ • Real-time UI      │    │ • Event Streaming   │    │ • Message History   │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                      │
                           ┌─────────────────────┐
                           │   MCP Integration   │
                           │   (AI Assistants)   │
                           │                     │
                           │ • FastMCP Server    │
                           │ • Tool Exposure     │
                           │ • Claude Integration │
                           └─────────────────────┘
```

## Key Features

### Real-time Communication
Messages appear instantly across all connected clients using Server-Sent Events, providing a smooth chat experience without the complexity of WebSockets.

### Organization-Based Multi-tenancy
Every resource belongs to an organization, ensuring complete data isolation between different teams or companies.

### Full-text Search
Powered by SQLite FTS5, search returns relevant messages in under 50ms even with 100k+ messages.

### AI Integration
Native MCP (Model Context Protocol) support allows AI assistants like Claude to interact with your chat history and post messages.

### Comprehensive Auditing
All changes are tracked with JSON diffs, providing complete accountability and change history.

## Documentation Sections

- **[Quick Start](quickstart.md)** - Get up and running in under 5 minutes
- **[Architecture](architecture.md)** - System design and technology choices
- **[API Reference](api.md)** - Complete REST API documentation
- **[Development](development.md)** - Developer setup and workflows
- **[Deployment](deployment.md)** - Production deployment guides
- **[ADR Index](adr/index.md)** - Architecture Decision Records

## Need Help?

- Check the [API documentation](http://localhost:8000/docs) when running locally
- Review the [development guide](development.md) for common workflows
- See the [architecture documentation](architecture.md) for system design details