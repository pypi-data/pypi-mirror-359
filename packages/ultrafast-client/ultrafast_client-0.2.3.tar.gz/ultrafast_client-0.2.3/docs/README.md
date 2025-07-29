# UltraFast HTTP Client Documentation 📚

Complete documentation for the UltraFast HTTP Client - a high-performance Python HTTP library built with Rust.

## Documentation Structure

```
docs/
├── README.md                    # This overview (start here)
├── api/                        # Complete API reference
│   └── README.md               # Full API documentation
├── tutorials/                  # Step-by-step tutorials
│   └── getting-started.md      # Quick start guide
├── guides/                     # In-depth guides
│   └── migration-guide.md      # Migration from other libraries
└── examples/                   # Practical examples
    ├── basic/                  # HTTP basics
    ├── authentication/         # Auth methods
    ├── advanced/              # Advanced configuration
    ├── real-time/             # WebSocket & SSE
    └── performance/           # Benchmarking
```

## Quick Navigation

### 🚀 **Getting Started**
- **[Getting Started Tutorial](tutorials/getting-started.md)** - Your first steps with UltraFast
- **[Basic Examples](../examples/basic/)** - Simple HTTP requests and async patterns
- **[Migration Guide](guides/migration-guide.md)** - Coming from requests, aiohttp, httpx, or urllib

### 📖 **API Reference**
- **[Complete API Documentation](api/README.md)** - All classes, methods, and parameters
- **[Authentication API](api/README.md#authentication)** - Bearer, Basic, API Key, OAuth2
- **[Configuration API](api/README.md#configuration)** - Timeouts, retries, rate limiting, SSL
- **[Real-time API](api/README.md#real-time-communication)** - WebSocket and SSE

### 💡 **Examples & Tutorials**
- **[Examples Directory](../examples/README.md)** - Comprehensive examples with explanations
- **[Authentication Examples](../examples/authentication/)** - All auth methods with real APIs
- **[Performance Examples](../examples/performance/)** - Benchmarking and optimization
- **[Real-time Examples](../examples/real-time/)** - WebSocket and SSE patterns

## Feature Overview

### 🚄 **High Performance**
```python
# HTTP/2 with automatic fallback
protocol_config = uc.ProtocolConfig(
    preferred_version=uc.HttpVersion.Http3,
    fallback_strategy=uc.ProtocolFallback.Http2ToHttp1
)

client = uc.HttpClient(protocol_config=protocol_config)
response = client.get("https://example.com")  # Uses fastest available protocol
```

### 🔄 **Sync & Async**
```python
# Synchronous
client = uc.HttpClient()
response = client.get("https://api.github.com/users/octocat")

# Asynchronous
async def fetch_data():
    client = uc.AsyncHttpClient()
    response = await client.get("https://api.github.com/users/octocat")
    return response.json()
```

### 🔐 **Enterprise Authentication**
```python
# Bearer token
auth = uc.AuthConfig.bearer("your-api-token")

# OAuth2 with automatic refresh
auth = uc.AuthConfig.oauth2(
    client_id="your-client-id",
    client_secret="your-secret",
    token_url="https://auth.example.com/token"
)

client = uc.HttpClient(auth_config=auth)
```

### ⚙️ **Advanced Configuration**
```python
client = uc.HttpClient(
    timeout_config=uc.TimeoutConfig(connect_timeout=10.0, read_timeout=30.0),
    retry_config=uc.RetryConfig(max_retries=3, backoff_factor=2.0),
    rate_limit_config=uc.RateLimitConfig.moderate(),  # 10 req/s, burst 20
    pool_config=uc.PoolConfig(max_connections_per_host=20),
    ssl_config=uc.SSLConfig(min_tls_version=uc.TlsVersion.TLS_1_2)
)
```

### 🔌 **Real-time Communication**
```python
# WebSocket
ws_client = uc.WebSocketClient()
ws_client.connect("wss://echo.websocket.org/")
ws_client.send(uc.WebSocketMessage.new_text("Hello!"))

# Server-Sent Events
sse_client = uc.SSEClient()
sse_client.connect("https://api.example.com/events")
for event in sse_client.listen():
    print(f"Event: {event.data}")
```

## Performance Benchmarks

### Speed Comparison
```
Library                    Requests/Second    Relative Speed
requests (sync)                    122           1.0x
aiohttp (async)                    323           2.6x
httpx (async)                      445           3.6x
UltraFast HTTP/1.1 (sync)         556           4.6x
UltraFast HTTP/2 (async)          834           6.8x
UltraFast HTTP/2 (async)         1,247         10.2x
```

### Memory Usage
```
Library            Memory Usage    Reduction
requests                 45MB         —
aiohttp                  32MB       29%
httpx                    28MB       38%
UltraFast                18MB       60%
```

## Common Use Cases

### 🌐 **API Integration**
Perfect for integrating with REST APIs, handling authentication, rate limiting, and retries automatically.

**[See API Integration Examples →](../examples/authentication/auth_examples.py)**

### 🏗️ **Microservices Communication**
High-performance service-to-service communication with connection pooling and circuit breakers.

**[See Microservices Examples →](../examples/advanced/configuration_examples.py)**

### 📱 **Real-time Applications**
WebSocket and SSE support for live updates, chat applications, and streaming data.

**[See Real-time Examples →](../examples/real-time/)**

### ⚡ **High-Performance Data Processing**
Concurrent request processing with async/await for maximum throughput.

**[See Performance Examples →](../examples/performance/benchmarking_examples.py)**

## Architecture Deep Dive

### 🦀 **Rust Core**
Built on top of proven Rust libraries:
- **reqwest** - HTTP client foundation
- **hyper** - HTTP/1 and HTTP/2 implementation
- **quiche** - HTTP/2 (QUIC) support
- **tokio** - Async runtime
- **PyO3** - Python bindings

### 🔧 **Modular Design**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Python API    │◄──►│   Rust Core     │◄──►│ Tokio Runtime   │
│                 │    │                 │    │                 │
│ • HttpClient    │    │ • reqwest       │    │ • Connection    │
│ • AsyncClient   │    │ • hyper         │    │   Pooling       │
│ • WebSocket     │    │ • quiche (HTTP/2)│   │ • HTTP/1,2,3    │
│ • SSE           │    │ • tokio-tungstenite│  │ • TLS/SSL      │
│ • Sessions      │    │ • serde_json    │    │ • Rate Limiting │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### �� **Protocol Negotiation**
```
Request → HTTP/2 Attempt → Success ✅
            ↓ (if unavailable)
          HTTP/2 Attempt → Success ✅
            ↓ (if unavailable)
          HTTP/1.1 → Success ✅
```

## Configuration Reference

### Essential Configurations

#### Timeouts
```python
timeout_config = uc.TimeoutConfig(
    connect_timeout=10.0,    # Time to establish connection
    read_timeout=30.0,       # Time to read response
    total_timeout=60.0       # Maximum total request time
)
```

#### Retries
```python
retry_config = uc.RetryConfig(
    max_retries=3,               # Maximum retry attempts
    initial_delay=1.0,           # Initial delay between retries
    max_delay=30.0,             # Maximum delay (exponential backoff)
    backoff_factor=2.0,         # Multiplier for exponential backoff
    retry_on_timeout=True,      # Retry on timeout errors
    retry_on_connection_error=True,  # Retry on connection errors
    status_codes_to_retry=[500, 502, 503, 504]  # HTTP status codes to retry
)
```

#### Rate Limiting
```python
# Predefined configurations
rate_config = uc.RateLimitConfig.conservative()  # 1 req/s, burst 5
rate_config = uc.RateLimitConfig.moderate()      # 10 req/s, burst 20
rate_config = uc.RateLimitConfig.aggressive()    # 100 req/s, burst 200

# Custom configuration
rate_config = uc.RateLimitConfig(
    enabled=True,
    algorithm=uc.RateLimitAlgorithm.TokenBucket,
    requests_per_second=5.0,
    burst_size=10,
    per_host=True,              # Rate limit per destination host
    queue_requests=True,        # Queue requests when limit is hit
    max_queue_size=100,
    queue_timeout_seconds=30.0
)
```

## Best Practices

### 🎯 **Client Configuration**
```python
# Production-ready client
def create_production_client(api_token):
    return uc.HttpClient(
        auth_config=uc.AuthConfig.bearer(api_token),
        timeout_config=uc.TimeoutConfig(
            connect_timeout=10.0,
            read_timeout=30.0,
            total_timeout=60.0
        ),
        retry_config=uc.RetryConfig(
            max_retries=3,
            initial_delay=1.0,
            max_delay=30.0,
            backoff_factor=2.0
        ),
        rate_limit_config=uc.RateLimitConfig.moderate(),
        pool_config=uc.PoolConfig(
            max_connections_per_host=20,
            max_idle_connections=10
        ),
        headers={
            "User-Agent": "MyApp/1.0",
            "Accept": "application/json"
        }
    )
```

### 🔄 **Error Handling**
```python
try:
    response = client.get("https://api.example.com/data")
    
    if response.ok():
        return response.json()
    elif response.is_client_error():
        # Handle 4xx errors (client mistakes)
        raise ClientError(f"Bad request: {response.status_code}")
    elif response.is_server_error():
        # Handle 5xx errors (server issues)
        raise ServerError(f"Server error: {response.status_code}")
        
except uc.UltraFastError as e:
    # Handle network errors, timeouts, etc.
    logger.error(f"Request failed: {e}")
    raise NetworkError(str(e))
```

### ⚡ **Async Patterns**
```python
async def fetch_multiple_apis():
    client = uc.AsyncHttpClient()
    
    # Concurrent requests for maximum performance
    tasks = [
        client.get("https://api1.example.com/data"),
        client.get("https://api2.example.com/data"),
        client.get("https://api3.example.com/data")
    ]
    
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    results = []
    for response in responses:
        if isinstance(response, Exception):
            logger.error(f"Request failed: {response}")
            continue
        
        if response.ok():
            results.append(response.json())
    
    return results
```

## Learning Path

### 1. **Beginner** (New to HTTP clients)
1. Start with **[Getting Started Tutorial](tutorials/getting-started.md)**
2. Work through **[Basic Examples](../examples/basic/)**
3. Practice **[Authentication Examples](../examples/authentication/)**

### 2. **Intermediate** (Familiar with HTTP libraries)
1. Read **[Migration Guide](guides/migration-guide.md)** for your current library
2. Explore **[Advanced Configuration](../examples/advanced/)**
3. Try **[Performance Examples](../examples/performance/)**

### 3. **Advanced** (Building high-performance applications)
1. Master **[Real-time Communication](../examples/real-time/)**
2. Study **[Performance Optimization](../examples/performance/)**
3. Contribute to **[API Reference](api/README.md)**

## Support & Community

### 📖 **Documentation**
- **[API Reference](api/README.md)** - Complete API documentation
- **[Examples](../examples/README.md)** - Practical code examples
- **[Tutorials](tutorials/)** - Step-by-step guides

### 🐛 **Getting Help**
- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - Questions and community support
- **Documentation Issues** - Help improve these docs

### 🤝 **Contributing**
- **Code Contributions** - New features and bug fixes
- **Documentation** - Improve tutorials and examples
- **Examples** - Share your use cases
- **Testing** - Help test new features

## Changelog & Releases

### Latest Features (v0.1.3)
- ✅ **90.8% test coverage** with comprehensive test suite
- ✅ **HTTP/2 support** with automatic fallback
- ✅ **WebSocket and SSE** real-time communication
- ✅ **Advanced rate limiting** with multiple algorithms
- ✅ **Memory profiling** and performance tools
- ✅ **Production-ready** error handling and retries

### Roadmap
- 🚧 **HTTP/2 optimizations** - Further performance improvements
- 🚧 **gRPC support** - Protocol Buffer communication
- 🚧 **Distributed tracing** - OpenTelemetry integration
- 🚧 **Circuit breaker** - Advanced resilience patterns

---

**Ready to build lightning-fast HTTP applications?** Start with the **[Getting Started Tutorial](tutorials/getting-started.md)** or dive into **[Examples](../examples/README.md)**! 🚀
