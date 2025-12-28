# Redis Installation Guide

## Redis Architecture

Redis consists of **two separate components**:

### 1. Redis Server (System-Level)
- **What it is**: A standalone database server/daemon (like PostgreSQL or MySQL)
- **Installation**: System-level via Homebrew (macOS) or package manager
- **Purpose**: Runs as a background service, stores queue data in memory
- **NOT** a Python package - cannot be installed in venv
- **Location**: System-wide installation (e.g., `/opt/homebrew/bin/redis-server`)

### 2. Python Redis Client (Environment-Level)
- **What it is**: Python library that connects to Redis server
- **Installation**: In your Python venv (already in `requirements_ocr.txt`)
- **Purpose**: Allows Python code to communicate with Redis server
- **Package**: `redis>=5.0.0` (already listed in requirements)

## Installation Strategy

### ✅ Recommended: System-Level Redis Server + venv Python Client

**Why this approach:**
- Redis server is a system service that should run independently
- Multiple applications can share the same Redis server
- Python client in venv keeps dependencies isolated
- Matches production deployment patterns
- Standard practice for Redis usage

**Installation:**

1. **Install Redis Server (System-Level)**
   ```bash
   brew install redis
   ```

2. **Start Redis Server**
   ```bash
   # Start and enable auto-start on boot
   brew services start redis
   
   # OR start manually (for testing)
   redis-server
   ```

3. **Install Python Client (venv)**
   ```bash
   cd /Users/scottroberts/Library/CloudStorage/Dropbox/app_development/Construction_Suite/apps/digidoc
   source .venv/bin/activate  # or your venv activation
   pip install -r requirements_ocr.txt
   ```

## Verification

### Check Redis Server is Running
```bash
# Test connection
redis-cli ping
# Should return: PONG
```

### Check Python Client in venv
```bash
source .venv/bin/activate
python3 -c "import redis; r = redis.Redis.from_url('redis://localhost:6379/0'); print(r.ping())"
# Should return: True
```

## Configuration

Redis server runs on:
- **Default Port**: 6379
- **Default URL**: `redis://localhost:6379/0`
- **Config Location**: `/opt/homebrew/etc/redis.conf` (Homebrew)

Your DigiDoc config (`digidoc_config.yaml`) already has:
```yaml
queue:
  redis_url: "redis://localhost:6379/0"
```

## Alternative: Docker (Not Recommended for MVP)

If you prefer containerization:
```bash
docker run -d -p 6379:6379 redis:latest
```

**Why not recommended for MVP:**
- Adds complexity
- Requires Docker installation
- System-level installation is simpler for development

## Production Considerations

In production:
- Redis server runs as a system service (systemd on Linux, LaunchDaemon on macOS)
- Multiple applications can connect to the same Redis instance
- Can use Redis Cluster for high availability (post-MVP)

## Summary

- **Redis Server**: System-level installation via Homebrew ✅
- **Python Redis Client**: venv installation (already in requirements) ✅
- **Connection**: Python client connects to system Redis server ✅

This is the standard, recommended approach.

