# UltraFast HTTP Client - Examples 📚

This directory contains comprehensive examples demonstrating all features of the UltraFast HTTP Client.

## Directory Structure

```
examples/
├── basic/                    # Basic HTTP operations
│   ├── simple_requests.py    # Simple GET, POST, PUT, DELETE requests
│   └── async_requests.py     # Async/await patterns and concurrency
├── authentication/          # Authentication methods
│   └── auth_examples.py      # Bearer, Basic, API Key, OAuth2
├── advanced/                # Advanced configurations
│   └── configuration_examples.py  # Timeouts, retries, rate limiting, SSL
├── real-time/               # Real-time communication
│   ├── websocket_examples.py     # WebSocket bidirectional communication
│   └── sse_examples.py           # Server-Sent Events streaming
├── performance/             # Performance and benchmarking
│   └── benchmarking_examples.py  # Performance testing and optimization
└── README.md               # This file
```

## Quick Start Examples

### 1. Basic HTTP Request
```python
import ultrafast_client as uc

client = uc.HttpClient()
response = client.get("https://api.github.com/users/octocat")
print(f"Status: {response.status_code}")
print(f"User: {response.json()['name']}")
```

### 2. Async Concurrent Requests
```python
import asyncio
import ultrafast_client as uc

async def main():
    client = uc.AsyncHttpClient()
    
    # Make 3 concurrent requests
    tasks = [
        client.get("https://api.github.com/users/octocat"),
        client.get("https://api.github.com/users/defunkt"), 
        client.get("https://api.github.com/users/mojombo")
    ]
    
    responses = await asyncio.gather(*tasks)
    for response in responses:
        user = response.json()
        print(f"User: {user['login']} has {user['public_repos']} repos")

asyncio.run(main())
```

### 3. Authentication
```python
import ultrafast_client as uc

# Bearer token auth
auth = uc.AuthConfig.bearer("your-api-token")
client = uc.HttpClient(auth_config=auth)
response = client.get("https://api.github.com/user")
```

### 4. WebSocket Communication
```python
import ultrafast_client as uc

ws_client = uc.WebSocketClient()
if ws_client.connect("wss://echo.websocket.org/"):
    ws_client.send(uc.WebSocketMessage.new_text("Hello WebSocket!"))
    message = ws_client.receive()
    print(f"Received: {message.text()}")
    ws_client.close()
```

### 5. Server-Sent Events
```python
import ultrafast_client as uc

sse_client = uc.SSEClient()
sse_client.connect("https://httpbin.org/stream/5")

for event in sse_client.listen():
    print(f"Event: {event.data}")
    # Process only 5 events
    if event.id and int(event.id) >= 5:
        break

sse_client.close()
```

## Running Examples

Each example file can be run independently:

```bash
# Basic examples
python examples/basic/simple_requests.py
python examples/basic/async_requests.py

# Authentication examples
python examples/authentication/auth_examples.py

# Advanced configuration
python examples/advanced/configuration_examples.py

# Real-time communication
python examples/real-time/websocket_examples.py
python examples/real-time/sse_examples.py

# Performance benchmarking
python examples/performance/benchmarking_examples.py
```

## Example Categories

### 🚀 Basic Examples (`basic/`)

**`simple_requests.py`** - Start here for HTTP basics:
- GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS requests
- Query parameters and custom headers
- JSON and form data handling
- Basic error handling

**`async_requests.py`** - Asynchronous programming patterns:
- Async/await syntax
- Concurrent request execution
- Producer-consumer patterns
- Performance comparisons

### 🔐 Authentication Examples (`authentication/`)

**`auth_examples.py`** - Complete authentication guide:
- Bearer token authentication
- Basic username/password auth
- API key authentication (headers and query params)
- OAuth2 configuration
- Session-based authentication
- Dynamic auth switching

### ⚙️ Advanced Examples (`advanced/`)

**`configuration_examples.py`** - Production-ready configuration:
- Timeout configuration (connect, read, total)
- Retry logic with exponential backoff
- Rate limiting (conservative, moderate, aggressive)
- Connection pooling for performance
- SSL/TLS security settings
- Protocol configuration (HTTP/1.1, HTTP/2, HTTP/2)
- Compression settings

### 🔌 Real-time Examples (`real-time/`)

**`websocket_examples.py`** - Bidirectional real-time communication:
- Synchronous and asynchronous WebSocket clients
- Different message types (text, binary, ping, pong, close)
- Authentication with WebSocket headers
- Concurrent connections
- Chat application simulation
- Heartbeat/keepalive patterns

**`sse_examples.py`** - Server-to-client streaming:
- Synchronous and asynchronous SSE clients
- Event filtering and processing
- Authentication headers
- Multiple stream monitoring
- Timeout handling
- Utility functions for SSE parsing

### ⚡ Performance Examples (`performance/`)

**`benchmarking_examples.py`** - Performance testing and optimization:
- Basic benchmarking with metrics
- Memory profiling
- Sync vs async performance comparison
- Rate limiting performance impact
- Connection pooling benefits
- Compression performance
- HTTP protocol comparisons

## Common Patterns

### Error Handling Pattern
```python
try:
    response = client.get("https://api.example.com/data")
    
    if response.ok():
        data = response.json()
        # Process successful response
    elif response.is_client_error():
        print(f"Client error: {response.status_code}")
    elif response.is_server_error():
        print(f"Server error: {response.status_code}")
        
except uc.UltraFastError as e:
    print(f"Request failed: {e}")
```

### Session Management Pattern
```python
with uc.Session() as session:
    session.set_base_url("https://api.example.com")
    session.set_auth(auth_config)
    
    # Login
    login_response = session.post("/login", json=credentials)
    
    # Use authenticated session
    user_data = session.get("/profile").json()
    settings = session.get("/settings").json()
# Session automatically closed
```

### Async Context Manager Pattern
```python
async with uc.AsyncSession() as session:
    session.set_base_url("https://api.example.com")
    
    # Multiple concurrent requests
    tasks = [
        session.get("/users"),
        session.get("/posts"),
        session.get("/comments")
    ]
    
    responses = await asyncio.gather(*tasks)
```

### Configuration Builder Pattern
```python
# Build a production-ready client
client = uc.HttpClient(
    auth_config=uc.AuthConfig.bearer("token"),
    timeout_config=uc.TimeoutConfig(connect_timeout=10.0, read_timeout=30.0),
    retry_config=uc.RetryConfig(max_retries=3, initial_delay=1.0),
    rate_limit_config=uc.RateLimitConfig.moderate(),
    pool_config=uc.PoolConfig(max_connections_per_host=20),
    protocol_config=uc.ProtocolConfig(preferred_version=uc.HttpVersion.Http2),
    headers={"User-Agent": "MyApp/1.0"}
)
```

## Testing Examples

You can test the examples with real endpoints:

```bash
# Test with httpbin.org (HTTP testing service)
python examples/basic/simple_requests.py

# Test with GitHub API (set GITHUB_TOKEN environment variable)
export GITHUB_TOKEN="your_personal_access_token"
python examples/authentication/auth_examples.py

# Test WebSocket with echo server
python examples/real-time/websocket_examples.py

# Run performance benchmarks
python examples/performance/benchmarking_examples.py
```

## Environment Variables

Some examples use environment variables for configuration:

```bash
export GITHUB_TOKEN="your_github_token"           # For GitHub API examples
export API_TOKEN="your_api_token"                 # For bearer auth examples
export PROXY_URL="http://proxy.example.com:8080"  # For proxy examples
```

## Contributing Examples

When adding new examples:

1. **Follow the existing structure** - Place examples in appropriate directories
2. **Include comprehensive comments** - Explain what each example demonstrates
3. **Handle errors gracefully** - Show proper error handling patterns
4. **Use realistic scenarios** - Create examples that solve real-world problems
5. **Test thoroughly** - Ensure examples work with the provided endpoints

## Support

- 📖 **API Reference**: See `docs/api/README.md`
- 🎓 **Tutorials**: See `docs/tutorials/`
- 🐛 **Issues**: Report bugs on GitHub
- 💬 **Discussions**: Ask questions on GitHub Discussions

Happy coding with UltraFast HTTP Client! 🚀
