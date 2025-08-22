# Quick Start Guide

Get WorkChat running in under 5 minutes with this step-by-step guide.

## Prerequisites

- **Git** - for cloning the repository
- **Docker & Docker Compose** (recommended) OR
- **Python 3.12+** and **Node.js 18+** (for local development)

## Option 1: Docker Compose (Recommended)

The fastest way to get WorkChat running:

```bash
# Clone the repository
git clone <repository>
cd workchat

# Start all services
docker compose up
```

This will start:
- Backend API at [http://localhost:8000](http://localhost:8000)
- Frontend UI at [http://localhost:3000](http://localhost:3000)
- Database (SQLite) with sample data

**That's it!** You now have a fully functional WorkChat instance.

## Option 2: Local Development

For development or if you prefer running services locally:

### Backend Setup (2 minutes)

```bash
# Clone and enter directory
git clone <repository>
cd workchat

# Install dependencies with UV
uv sync

# Setup database
uv run alembic upgrade head

# Start backend server
uv run uvicorn workchat.app:app --reload
```

Backend will be available at [http://localhost:8000](http://localhost:8000)

### Frontend Setup (2 minutes)

In a new terminal:

```bash
# Enter frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at [http://localhost:3000](http://localhost:3000)

## First Steps

### 1. Explore the API

Visit [http://localhost:8000/docs](http://localhost:8000/docs) to see the interactive API documentation.

### 2. Create Your First User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "you@example.com",
    "password": "yourpassword",
    "display_name": "Your Name"
  }'
```

### 3. Login and Get a Token

```bash
curl -X POST http://localhost:8000/auth/jwt/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=you@example.com&password=yourpassword'
```

Save the returned `access_token` for API calls.

### 4. Create a Channel

```bash
export TOKEN="your_access_token_here"

curl -X POST http://localhost:8000/api/channels \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "general",
    "description": "General discussion"
  }'
```

### 5. Post Your First Message

```bash
export CHANNEL_ID="channel_id_from_step_4"

curl -X POST http://localhost:8000/api/messages \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "'$CHANNEL_ID'",
    "body": "Hello, WorkChat! 🎉"
  }'
```

### 6. Watch Real-time Updates

Open a new terminal and connect to the event stream:

```bash
curl -N -H "Authorization: Bearer $TOKEN" http://localhost:8000/events
```

Now post another message and watch it appear in real-time!

## Using the Web Interface

1. Open [http://localhost:3000](http://localhost:3000) in your browser
2. You'll see the channel sidebar and main chat area
3. Click on a channel to view its messages
4. Use the message composer at the bottom to send messages
5. Watch messages appear in real-time as others post them

## MCP Integration (AI Assistants)

To use WorkChat with AI assistants like Claude:

```bash
# Start the MCP server
python -m workchat.mcp
```

This exposes WorkChat operations as MCP tools that AI assistants can use.

## What's Next?

- **[Development Guide](development.md)** - Set up your development environment
- **[API Reference](api.md)** - Complete API documentation  
- **[Architecture](architecture.md)** - Understand the system design
- **[Deployment](deployment.md)** - Deploy to production

## Troubleshooting

### Port Already in Use

If you get port conflicts:

```bash
# Check what's using the port
lsof -i :8000  # or :3000

# Kill the process or use different ports
docker compose down  # stops all containers
```

### Database Issues

```bash
# Reset the database
rm workchat.db
uv run alembic upgrade head
```

### Frontend Won't Start

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Permission Issues (Linux/Mac)

```bash
# Make sure you have permissions
sudo chown -R $USER:$USER .
```

## Performance Notes

- First startup may take 30-60 seconds to download dependencies
- Subsequent starts should be under 10 seconds
- Real-time messaging latency is typically under 100ms
- Search queries return in under 50ms for 100k+ messages

**Need help?** Check the [development documentation](development.md) or review the [architecture guide](architecture.md).