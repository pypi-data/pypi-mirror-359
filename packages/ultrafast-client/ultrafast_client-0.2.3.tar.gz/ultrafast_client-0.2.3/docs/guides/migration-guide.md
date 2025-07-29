# Migration Guide 🔄

Complete guide for migrating from popular Python HTTP libraries to UltraFast HTTP Client.

## From `requests` Library

The most common migration path. UltraFast maintains similar API patterns while adding performance and features.

### Basic Request Migration

**Before (requests):**
```python
import requests

response = requests.get('https://api.github.com/user')
print(response.status_code)
print(response.json())
```

**After (UltraFast):**
```python
import ultrafast_client as uc

client = uc.HttpClient()
response = client.get('https://api.github.com/user')
print(response.status_code)
print(response.json())
```

### Authentication Migration

**Before (requests):**
```python
import requests

# Bearer token
headers = {'Authorization': 'Bearer your-token'}
response = requests.get('https://api.github.com/user', headers=headers)

# Basic auth
response = requests.get('https://api.example.com/data', 
                       auth=('username', 'password'))
```

**After (UltraFast):**
```python
import ultrafast_client as uc

# Bearer token
auth_config = uc.AuthConfig.bearer('your-token')
client = uc.HttpClient(auth_config=auth_config)
response = client.get('https://api.github.com/user')

# Basic auth
auth_config = uc.AuthConfig.basic('username', 'password')
client = uc.HttpClient(auth_config=auth_config)
response = client.get('https://api.example.com/data')
```

### Session Migration

**Before (requests):**
```python
import requests

session = requests.Session()
session.headers.update({'User-Agent': 'MyApp/1.0'})

# Login
session.post('https://api.example.com/login', json={'user': 'admin'})

# Use session
response = session.get('https://api.example.com/profile')
```

**After (UltraFast):**
```python
import ultrafast_client as uc

session = uc.Session()
session.set_header('User-Agent', 'MyApp/1.0')

# Login
session.post('https://api.example.com/login', json={'user': 'admin'})

# Use session
response = session.get('https://api.example.com/profile')
```

### Advanced Features Migration

**Before (requests):**
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Retry configuration
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)

session = requests.Session()
session.mount("http://", adapter)
session.mount("https://", adapter)

# Timeout
response = session.get('https://api.example.com/data', timeout=(5, 30))
```

**After (UltraFast):**
```python
import ultrafast_client as uc

# Retry configuration
retry_config = uc.RetryConfig(
    max_retries=3,
    initial_delay=1.0,
    backoff_factor=2.0,
    status_codes_to_retry=[429, 500, 502, 503, 504]
)

# Timeout configuration
timeout_config = uc.TimeoutConfig(
    connect_timeout=5.0,
    read_timeout=30.0
)

client = uc.HttpClient(
    retry_config=retry_config,
    timeout_config=timeout_config
)

response = client.get('https://api.example.com/data')
```

## From `aiohttp` Library

Migrating from aiohttp to UltraFast's async client.

### Basic Async Migration

**Before (aiohttp):**
```python
import aiohttp
import asyncio

async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.github.com/users/octocat') as response:
            return await response.json()

asyncio.run(fetch_data())
```

**After (UltraFast):**
```python
import ultrafast_client as uc
import asyncio

async def fetch_data():
    client = uc.AsyncHttpClient()
    response = await client.get('https://api.github.com/users/octocat')
    return response.json()

asyncio.run(fetch_data())
```

### Session and Context Manager Migration

**Before (aiohttp):**
```python
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:
        # Multiple requests with same session
        async with session.get('https://api.example.com/users') as response:
            users = await response.json()
        
        async with session.post('https://api.example.com/analytics', 
                               json={'event': 'page_view'}) as response:
            await response.text()
```

**After (UltraFast):**
```python
import ultrafast_client as uc

async def main():
    async with uc.AsyncSession() as session:
        # Multiple requests with same session
        users_response = await session.get('https://api.example.com/users')
        users = users_response.json()
        
        analytics_response = await session.post('https://api.example.com/analytics',
                                               json={'event': 'page_view'})
        await analytics_response.text()
```

### Concurrent Requests Migration

**Before (aiohttp):**
```python
import aiohttp
import asyncio

async def fetch_multiple():
    async with aiohttp.ClientSession() as session:
        tasks = []
        urls = ['https://api.github.com/users/user1', 
                'https://api.github.com/users/user2']
        
        for url in urls:
            task = session.get(url)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        results = []
        for response in responses:
            results.append(await response.json())
        
        return results
```

**After (UltraFast):**
```python
import ultrafast_client as uc
import asyncio

async def fetch_multiple():
    client = uc.AsyncHttpClient()
    urls = ['https://api.github.com/users/user1', 
            'https://api.github.com/users/user2']
    
    tasks = [client.get(url) for url in urls]
    responses = await asyncio.gather(*tasks)
    
    results = [response.json() for response in responses]
    return results
```

## From `httpx` Library

HTTPX users will find UltraFast familiar since both support sync/async patterns.

### Basic Migration

**Before (httpx):**
```python
import httpx

# Sync client
with httpx.Client() as client:
    response = client.get('https://api.github.com/users/octocat')
    print(response.json())

# Async client
async with httpx.AsyncClient() as client:
    response = await client.get('https://api.github.com/users/octocat')
    print(response.json())
```

**After (UltraFast):**
```python
import ultrafast_client as uc

# Sync client
client = uc.HttpClient()
response = client.get('https://api.github.com/users/octocat')
print(response.json())

# Async client
async def main():
    client = uc.AsyncHttpClient()
    response = await client.get('https://api.github.com/users/octocat')
    print(response.json())

import asyncio
asyncio.run(main())
```

### HTTP/2 Migration

**Before (httpx):**
```python
import httpx

# HTTP/2 support
client = httpx.Client(http2=True)
response = client.get('https://www.example.com/')
```

**After (UltraFast):**
```python
import ultrafast_client as uc

# HTTP/2 with fallback
protocol_config = uc.ProtocolConfig(
    preferred_version=uc.HttpVersion.Http2,
    enable_http2=True,
    fallback_strategy=uc.ProtocolFallback.Http2ToHttp1
)

client = uc.HttpClient(protocol_config=protocol_config)
response = client.get('https://www.example.com/')
```

## From `urllib` (Standard Library)

Upgrading from urllib to UltraFast provides significant ergonomic improvements.

### Basic Request Migration

**Before (urllib):**
```python
import urllib.request
import urllib.parse
import json

# GET request
response = urllib.request.urlopen('https://api.github.com/users/octocat')
data = json.loads(response.read().decode('utf-8'))

# POST request
post_data = json.dumps({'key': 'value'}).encode('utf-8')
request = urllib.request.Request(
    'https://httpbin.org/post',
    data=post_data,
    headers={'Content-Type': 'application/json'}
)
response = urllib.request.urlopen(request)
```

**After (UltraFast):**
```python
import ultrafast_client as uc

client = uc.HttpClient()

# GET request
response = client.get('https://api.github.com/users/octocat')
data = response.json()

# POST request
response = client.post('https://httpbin.org/post', json={'key': 'value'})
```

### Error Handling Migration

**Before (urllib):**
```python
import urllib.request
import urllib.error

try:
    response = urllib.request.urlopen('https://httpbin.org/status/404')
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.reason}")
except urllib.error.URLError as e:
    print(f"URL Error: {e.reason}")
```

**After (UltraFast):**
```python
import ultrafast_client as uc

client = uc.HttpClient()

try:
    response = client.get('https://httpbin.org/status/404')
    
    if response.is_client_error():
        print(f"Client Error: {response.status_code} - {response.reason()}")
        
except uc.UltraFastError as e:
    print(f"Request Error: {e}")
```

## Migration Checklist

### ✅ Feature Comparison

| Feature | requests | aiohttp | httpx | urllib | UltraFast |
|---------|----------|---------|-------|--------|-----------|
| Sync API | ✅ | ❌ | ✅ | ✅ | ✅ |
| Async API | ❌ | ✅ | ✅ | ❌ | ✅ |
| HTTP/2 | ❌ | ❌ | ✅ | ❌ | ✅ |
| HTTP/2 | ❌ | ❌ | ❌ | ❌ | ✅ |
| WebSocket | ❌ | ✅ | ✅ | ❌ | ✅ |
| SSE | ❌ | ✅ | ❌ | ❌ | ✅ |
| Sessions | ✅ | ✅ | ✅ | ❌ | ✅ |
| Connection Pooling | ✅ | ✅ | ✅ | ❌ | ✅ |
| Built-in Retries | 🔧 | ❌ | ❌ | ❌ | ✅ |
| Rate Limiting | ❌ | ❌ | ❌ | ❌ | ✅ |
| Performance | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |

### 🔄 Migration Steps

1. **Install UltraFast**: `pip install ultrafast-client`
2. **Replace imports**: Change library imports to `import ultrafast_client as uc`
3. **Update client creation**: Use `uc.HttpClient()` or `uc.AsyncHttpClient()`
4. **Migrate authentication**: Use `uc.AuthConfig` instead of headers/auth parameters
5. **Update configuration**: Replace adapter/session config with UltraFast config objects
6. **Test thoroughly**: Verify all requests work as expected
7. **Optimize**: Take advantage of new features like rate limiting and HTTP/2

### 🚨 Breaking Changes

1. **Response object**: UltraFast uses `ClientResponse` instead of library-specific response objects
2. **Session management**: Explicit session creation vs automatic context managers
3. **Error types**: UltraFast uses `UltraFastError` hierarchy instead of library-specific exceptions
4. **Configuration**: Structured config objects vs parameters

### 📈 Performance Benefits

After migration, you can expect:

- **2-5x faster** requests with HTTP/2
- **3-8x faster** with HTTP/2 (when available)
- **Better memory efficiency** with connection pooling
- **Built-in optimizations** like compression and keep-alive
- **Automatic retries** reducing error rates

## Common Migration Patterns

### 1. Drop-in Replacement Pattern
```python
# Create a compatibility wrapper
class RequestsCompatClient:
    def __init__(self):
        self.client = uc.HttpClient()
    
    def get(self, url, **kwargs):
        return self.client.get(url, **kwargs)
    
    def post(self, url, **kwargs):
        return self.client.post(url, **kwargs)
    
    # Add other methods as needed

# Use as drop-in replacement
requests = RequestsCompatClient()
response = requests.get('https://api.example.com/data')
```

### 2. Gradual Migration Pattern
```python
# Migrate one module at a time
import ultrafast_client as uc
import requests  # Keep for other modules

class APIClient:
    def __init__(self):
        # Use UltraFast for new features
        self.uc_client = uc.HttpClient()
        # Keep requests for legacy code
        self.requests_session = requests.Session()
    
    def new_api_call(self, endpoint):
        return self.uc_client.get(f'https://api.example.com/{endpoint}')
    
    def legacy_api_call(self, endpoint):
        return self.requests_session.get(f'https://legacy.example.com/{endpoint}')
```

### 3. Configuration Migration Pattern
```python
# Centralized configuration migration
def create_http_client():
    return uc.HttpClient(
        timeout_config=uc.TimeoutConfig(
            connect_timeout=10.0,
            read_timeout=30.0
        ),
        retry_config=uc.RetryConfig(
            max_retries=3,
            initial_delay=1.0
        ),
        rate_limit_config=uc.RateLimitConfig.moderate(),
        headers={
            'User-Agent': 'MyApp/2.0 (UltraFast-Powered)'
        }
    )

# Use throughout application
client = create_http_client()
```

## Testing Migration

### Unit Test Migration
```python
# Before (with requests)
import unittest.mock
import requests

def test_api_call():
    with unittest.mock.patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'status': 'ok'}
        result = my_api_function()
        assert result['status'] == 'ok'

# After (with UltraFast)
import unittest.mock
import ultrafast_client as uc

def test_api_call():
    with unittest.mock.patch.object(uc.HttpClient, 'get') as mock_get:
        mock_response = uc.ClientResponse(200, {}, b'{"status": "ok"}', 'https://api.example.com')
        mock_get.return_value = mock_response
        result = my_api_function()
        assert result['status'] == 'ok'
```

## Troubleshooting Migration

### Common Issues

1. **Import Errors**
   ```python
   # Wrong
   from ultrafast_client import HttpClient
   
   # Correct
   import ultrafast_client as uc
   client = uc.HttpClient()
   ```

2. **Response Object Differences**
   ```python
   # requests: response.text is a property
   text = response.text
   
   # UltraFast: response.text() is a method
   text = response.text()
   ```

3. **Authentication Headers**
   ```python
   # Instead of manual headers
   headers = {'Authorization': 'Bearer token'}
   
   # Use structured auth
   auth = uc.AuthConfig.bearer('token')
   client = uc.HttpClient(auth_config=auth)
   ```

4. **Session Management**
   ```python
   # Instead of automatic context
   with requests.Session() as session:
       response = session.get(url)
   
   # Use explicit session
   session = uc.Session()
   response = session.get(url)
   # or with context manager
   with uc.Session() as session:
       response = session.get(url)
   ```

### Performance Verification

After migration, verify performance improvements:

```python
import time
import ultrafast_client as uc

def benchmark_migration():
    client = uc.HttpClient()
    
    # Benchmark your actual API calls
    start_time = time.time()
    
    for i in range(100):
        response = client.get('https://your-api.com/endpoint')
        assert response.ok()
    
    end_time = time.time()
    print(f"100 requests completed in {end_time - start_time:.2f} seconds")

benchmark_migration()
```

## Migration Support

Need help with migration? Check these resources:

- 📖 **[API Reference](../api/README.md)** - Complete API documentation
- 💡 **[Examples](../../examples/README.md)** - Side-by-side comparisons
- 🐛 **GitHub Issues** - Report migration issues
- 💬 **Discussions** - Ask migration questions

Happy migrating! 🚀
