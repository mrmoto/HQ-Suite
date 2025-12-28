# API Design Analysis: Watcher → DigiDoc Integration

**Date**: 2025-12-23  
**Context**: Zero Trust, RESTful design for inter-service communication on localhost

---

## Architecture Context

### Current Setup
- **Watcher**: OS-level daemon (separate process, separate binary)
- **DigiDoc**: Python Flask service (separate process)
- **Communication**: Localhost HTTP (same machine, different processes)
- **Security Model**: Zero Trust (even localhost should authenticate)

### Existing DigiDoc API
- Current endpoint: `/process` (POST)
- Other endpoints: `/health`, `/templates/sync`, `/templates/update`, etc.
- Framework: Flask
- Port: Not explicitly configured in current setup

---

## Best Practices Analysis

### 1. Zero Trust Principles

**Key Principle**: "Never trust, always verify" - even on localhost

**Implications**:
- ✅ **Authentication Required**: Even localhost services should authenticate
- ✅ **Token-Based Auth**: Use API tokens/keys (simpler than OAuth for service-to-service)
- ✅ **Audit Logging**: Log all API calls with caller identity
- ✅ **Least Privilege**: Watcher only needs `enqueue` permission

**Recommendation**:
- **MVP**: API token authentication (simple, secure for localhost)
- **Post-MVP**: Consider mTLS for production/cloud deployments

---

### 2. RESTful Design Principles

**RESTful Best Practices**:
- ✅ **Resource-Based URLs**: `/api/digidoc/queue` (noun, not verb)
- ✅ **HTTP Methods**: POST for creating queue items
- ✅ **Consistent Naming**: Plural nouns for collections
- ✅ **Versioning**: Consider `/api/v1/...` for future changes

**Current State**:
- ❌ `/process` is verb-based (not RESTful)
- ✅ `/templates/sync` follows RESTful pattern
- ⚠️ Mixed patterns in existing API

**Recommendation**:
- **Option A**: RESTful `/api/digidoc/queue` (aligns with MA.md, best practice)
- **Option B**: Keep `/process` for MVP, migrate later (faster, less breaking change)

---

### 3. Port Configuration

**Best Practices**:
- ✅ **Configurable**: Port should be in config file, not hardcoded
- ✅ **Default Port**: Standard default (e.g., 8001) but overrideable
- ✅ **Environment Variable**: Allow override via env var
- ✅ **Documentation**: Clearly document default and override methods

**Current State**:
- ⚠️ Port not in `digidoc_config.yaml`
- ⚠️ WS.md specifies `8001` but not configurable

**Recommendation**:
- Add `api.port` to `digidoc_config.yaml` (default: 8001)
- Allow override via `DIGIDOC_API_PORT` environment variable
- Document in both WS.md and MA.md

---

### 4. Authentication Strategy

**Zero Trust Requirements**:
- ✅ **API Token**: Required for all requests
- ✅ **Token in Header**: `Authorization: Bearer <token>` or `X-API-Key: <token>`
- ✅ **Token in Config**: Watcher config contains DigiDoc API token
- ✅ **Token Validation**: DigiDoc validates token on every request

**MVP Implementation**:
- Simple API key/token (not JWT for MVP)
- Token stored in Watcher config: `digidoc_api_token`
- Token validated in DigiDoc API middleware
- Reject requests without valid token

**Post-MVP**:
- JWT tokens with expiration
- Token rotation
- mTLS for cloud deployments

---

## Recommended Solution

### Endpoint Design

**Option 1: RESTful (Recommended for Zero Trust)**
```
POST http://localhost:8001/api/digidoc/queue
Authorization: Bearer <api_token>
```

**Pros**:
- ✅ RESTful resource-based naming
- ✅ Aligns with MA.md specification
- ✅ Clear resource: "queue" (noun)
- ✅ Consistent with `/api/digidoc/templates/sync` pattern
- ✅ Better for future API versioning

**Cons**:
- ⚠️ Requires updating existing `/process` endpoint (breaking change)
- ⚠️ More verbose URL

**Option 2: Keep Current (Faster MVP)**
```
POST http://localhost:8001/process
Authorization: Bearer <api_token>
```

**Pros**:
- ✅ No breaking changes to existing code
- ✅ Shorter URL
- ✅ Already implemented

**Cons**:
- ❌ Not RESTful (verb-based)
- ❌ Doesn't align with MA.md
- ❌ Inconsistent with other endpoints

---

### Port Configuration

**Recommended Approach**:
```yaml
# digidoc_config.yaml
api:
  port: 8001  # Default, configurable
  base_url: "http://localhost:{port}"  # Auto-constructed
  enqueue_endpoint: "/api/digidoc/queue"  # or "/process"
  auth_required: true  # Zero trust
```

**Environment Override**:
```bash
DIGIDOC_API_PORT=8001  # Override config file
```

---

### Authentication Implementation

**MVP Approach**:
1. **Watcher Config**:
   ```yaml
   digidoc_api_endpoint: "http://localhost:8001/api/digidoc/queue"
   digidoc_api_token: "your-secret-token-here"
   ```

2. **DigiDoc API Middleware**:
   ```python
   def require_api_token(f):
       @wraps(f)
       def decorated_function(*args, **kwargs):
           token = request.headers.get('Authorization', '').replace('Bearer ', '')
           if not token or token != config.api.digidoc_api_token:
               return jsonify({'error': 'Unauthorized'}), 401
           return f(*args, **kwargs)
       return decorated_function
   ```

3. **Watcher Request**:
   ```http
   POST /api/digidoc/queue HTTP/1.1
   Host: localhost:8001
   Authorization: Bearer your-secret-token-here
   Content-Type: application/json
   ```

---

## Recommendation Summary

### For Question 1 (API Endpoint):

**Endpoint Path**: `/api/digidoc/queue` (RESTful, aligns with MA.md)
- **Rationale**: Zero Trust + RESTful best practices
- **Alternative**: Keep `/process` for MVP, migrate in post-MVP

**Port**: `8001` (configurable via config file + env var)
- **Rationale**: Standard practice, allows flexibility
- **Implementation**: Add to `digidoc_config.yaml`

**Auth Token**: **Required for MVP** (Zero Trust principle)
- **Rationale**: Even localhost services should authenticate
- **Implementation**: API token in Watcher config, validated by DigiDoc
- **Format**: `Authorization: Bearer <token>` header

---

## Migration Path

If choosing RESTful endpoint:

1. **MVP**: Implement `/api/digidoc/queue` alongside `/process`
2. **Deprecation**: Mark `/process` as deprecated
3. **Post-MVP**: Remove `/process` endpoint

This allows:
- ✅ Watcher uses new RESTful endpoint
- ✅ Existing code continues working
- ✅ Clean migration path

---

## Questions for You

1. **Endpoint**: Prefer RESTful `/api/digidoc/queue` or keep `/process`?
2. **Breaking Change**: OK to update existing endpoint, or need backward compatibility?
3. **Auth Token**: Confirm MVP requires authentication (Zero Trust)?

---

**Ready for your decision on Question 1!**

---

## Path Handling Requirements

**CRITICAL**: All file paths in API communications must be absolute paths.

**Requirements**:
1. **API Request `file_path` Parameter**: Must be an absolute path (e.g., `/Users/username/Dropbox/Application Data/DigiDoc/queue/file.pdf`)
2. **Path Expansion**: Configuration paths using `~` or environment variables are expanded to absolute paths using `os.path.expanduser()` or equivalent
3. **Internal Operations**: All apps (Watcher, DigiDoc) use absolute paths internally after expansion

**Rationale**:
- Stateless services need explicit paths (no assumptions about working directories)
- Cross-system compatibility (different user accounts, deployment environments)
- Eliminates ambiguity in file location

**Examples**:
- ✅ Correct: `"file_path": "/Users/username/Dropbox/Application Data/DigiDoc/queue/file.pdf"`
- ❌ Incorrect: `"file_path": "queue/file.pdf"` (relative path)

**Reference**: See `shared_documentation/architecture/MASTER_ARCHITECTURE.md` "Path Handling Specifications" section for ecosystem-wide requirements.
