# WorkChat Frontend

React frontend for WorkChat real-time team chat application.

## Features

- **Channel Sidebar** - Browse and select channels
- **Thread View** - View messages in threaded conversations
- **Message Composer** - Send new messages with Shift+Enter support
- **Real-time Updates** - SSE connection for live message updates
- **TanStack Query** - Efficient data fetching and caching
- **TypeScript** - Full type safety with backend API

## Development

### Prerequisites

Make sure the WorkChat backend is running at `http://localhost:8000`.

### Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:3000` with API proxy to the backend.

### Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Architecture

### Components

- **App.tsx** - Main application layout and state
- **ChannelSidebar.tsx** - Channel list navigation  
- **ThreadView.tsx** - Message thread display and composition
- **MessageList.tsx** - Individual message rendering
- **MessageComposer.tsx** - Message input and sending

### API Integration

- **api/client.ts** - REST API client for backend communication
- **hooks/useSSE.ts** - Server-Sent Events hook for real-time updates
- **types.ts** - TypeScript definitions matching backend models

### Key Features

- **Real-time messaging** via SSE `/events` endpoint
- **Optimistic updates** with TanStack Query invalidation
- **Auto-scroll** to newest messages
- **Connection status** indicator
- **Error boundaries** for graceful failure handling

## Production Build

```bash
npm run build
```

Built files will be in the `dist/` directory, ready for deployment to any static hosting service.