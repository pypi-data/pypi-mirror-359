# UltraFast HTTP Client - API Reference 📚

Complete API documentation for the UltraFast HTTP Client library.

## Table of Contents

- [HTTP Clients](#http-clients)
- [Authentication](#authentication) 
- [Configuration](#configuration)
- [Sessions](#sessions)
- [Real-time Communication](#real-time-communication)
- [Performance Tools](#performance-tools)

---

## HTTP Clients

### HttpClient (Synchronous)

```python
import ultrafast_client as uc

client = uc.HttpClient(
    auth_config=None,           # Authentication configuration
    rate_limit_config=None,     # Rate limiting settings  
    retry_config=None,          # Retry logic configuration
    pool_config=None,           # Connection pooling settings
    protocol_config=None,       # HTTP protocol settings
    ssl_config=None,            # SSL/TLS configuration
    headers=None,               # Default headers
    proxy_config=None           # Proxy settings
)
```

#### HTTP Methods
```python
# GET request
response = client.get(url, params=None, headers=None, auth=None)

# POST request  
response = client.post(url, data=None, json=None, files=None, headers=None, auth=None)

# PUT, PATCH, DELETE, HEAD, OPTIONS
response = client.put(url, data=None, json=None, headers=None, auth=None)
response = client.patch(url, data=None, json=None, headers=None, auth=None)
response = client.delete(url, headers=None, auth=None)
response = client.head(url, headers=None, auth=None)
response = client.options(url, headers=None, auth=None)
```

### AsyncHttpClient (Asynchronous)

```python
import asyncio
import ultrafast_client as uc

async def main():
    client = uc.AsyncHttpClient()
    response = await client.get("https://api.example.com/data")
    data = response.json()

asyncio.run(main())
```

---

## Authentication

### AuthConfig

```python
# Bearer Token
auth = uc.AuthConfig.bearer("your-token-here")

# Basic Authentication  
auth = uc.AuthConfig.basic("username", "password")

# API Key in Headers
auth = uc.AuthConfig.api_key_header("X-API-Key", "your-key")

# OAuth2
auth = uc.AuthConfig.oauth2(
    client_id="your-client-id",
    client_secret="your-client-secret", 
    token_url="https://auth.example.com/token"
)
```

---

## Configuration

### TimeoutConfig

```python
timeout_config = uc.TimeoutConfig(
    connect_timeout=10.0,
    read_timeout=30.0,
    total_timeout=60.0
)
```

### RetryConfig

```python
retry_config = uc.RetryConfig(
    max_retries=3,
    initial_delay=1.0,
    max_delay=30.0,
    backoff_factor=2.0
)
```

### RateLimitConfig

```python
rate_config = uc.RateLimitConfig(
    requests_per_second=10.0,
    burst_size=20
)
```

---

## Sessions

### Session Management
```python
# Create session with persistent state
session = uc.Session(
    auth_config=auth_config,
    base_url="https://api.example.com"
)

# Use session (maintains cookies)
login_response = session.post("/login", json=credentials)
user_data = session.get("/profile").json()
```

---

## Real-time Communication

### WebSocket
```python
ws_client = uc.WebSocketClient()
ws_client.connect("wss://api.example.com/ws")
ws_client.send(uc.WebSocketMessage.new_text("Hello!"))
message = ws_client.receive()
```

### Server-Sent Events
```python
sse_client = uc.SSEClient()
sse_client.connect("https://api.example.com/events")
for event in sse_client.listen():
    print(f"Event: {event.data}")
```

---

## Performance Tools

### BenchmarkRunner
```python
benchmark = uc.BenchmarkRunner()
results = benchmark.run_benchmark(test_function, iterations=100)
print(f"Average time: {results.average_time}ms")
```

### MemoryProfiler
```python
with uc.MemoryProfiler() as profiler:
    # Your code here
    pass

stats = profiler.get_stats()
print(f"Peak memory: {stats.peak_memory_mb}MB")
```

---

## Response Handling

### ClientResponse
```python
response = client.get("https://api.example.com/data")

# Status and content
response.status_code     # HTTP status code
response.ok()           # True if 2xx status
response.text()         # Response as text
response.json()         # Parse JSON response
response.headers()      # Response headers
response.size()         # Response size in bytes
```

For detailed examples, see the [examples directory](../../examples/).
