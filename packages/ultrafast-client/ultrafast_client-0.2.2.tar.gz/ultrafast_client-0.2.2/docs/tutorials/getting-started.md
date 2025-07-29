# Getting Started with UltraFast HTTP Client 🚀

A step-by-step guide to get you up and running with the UltraFast HTTP Client.

## Installation

### Quick Installation
```bash
pip install ultrafast-client
```

### Development Installation
```bash
# Clone the repository
git clone https://github.com/username/ultrafast-client
cd ultrafast-client

# Install in development mode
pip install -e .

# Verify installation
python -c "import ultrafast_client as uc; print('✅ Installation successful!')"
```

## Your First Request

Let's start with a simple HTTP GET request:

```python
import ultrafast_client as uc

# Create an HTTP client
client = uc.HttpClient()

# Make a GET request
response = client.get("https://httpbin.org/get")

# Check the response
print(f"Status Code: {response.status_code}")
print(f"Success: {response.ok()}")
print(f"Response Size: {response.size()} bytes")

# Get response content
text_content = response.text()
json_data = response.json()

print(f"URL: {json_data['url']}")
print(f"User Agent: {json_data['headers']['User-Agent']}")
```

Expected output:
```
Status Code: 200
Success: True
Response Size: 424 bytes
URL: https://httpbin.org/get
User Agent: ultrafast-client/0.1.0
```

## HTTP Methods

UltraFast supports all standard HTTP methods:

### GET Request
```python
# Simple GET
response = client.get("https://api.github.com/users/octocat")

# GET with query parameters
response = client.get("https://httpbin.org/get", params={
    "name": "john",
    "age": "30"
})
```

### POST Request
```python
# POST with JSON data
response = client.post("https://httpbin.org/post", json={
    "name": "Alice",
    "email": "alice@example.com"
})

# POST with form data
response = client.post("https://httpbin.org/post", data={
    "username": "alice",
    "password": "secret123"
})
```

### Other Methods
```python
# PUT request
response = client.put("https://httpbin.org/put", json={"id": 1, "name": "Updated"})

# PATCH request
response = client.patch("https://httpbin.org/patch", json={"name": "Patched"})

# DELETE request
response = client.delete("https://httpbin.org/delete")

# HEAD request (headers only)
response = client.head("https://httpbin.org/get")

# OPTIONS request
response = client.options("https://httpbin.org/get")
```

## Working with Headers

### Setting Default Headers
```python
# Create client with default headers
client = uc.HttpClient(headers={
    "User-Agent": "MyApp/1.0",
    "Accept": "application/json"
})

# Add headers dynamically
client.set_header("X-API-Version", "v1")
client.set_header("Authorization", "Bearer your-token")

# View current headers
print(client.get_headers())
```

### Request-Specific Headers
```python
# Headers for a single request
response = client.get("https://httpbin.org/headers", headers={
    "X-Custom-Header": "CustomValue",
    "Accept-Language": "en-US"
})
```

## Authentication

### Bearer Token Authentication
```python
# Create authentication configuration
auth_config = uc.AuthConfig.bearer("your-api-token-here")

# Create client with authentication
client = uc.HttpClient(auth_config=auth_config)

# All requests will now include the Authorization header
response = client.get("https://api.github.com/user")
```

### Basic Authentication
```python
# Username and password authentication
auth_config = uc.AuthConfig.basic("username", "password")
client = uc.HttpClient(auth_config=auth_config)

response = client.get("https://httpbin.org/basic-auth/username/password")
```

### API Key Authentication
```python
# API key in headers
auth_config = uc.AuthConfig.api_key_header("X-API-Key", "your-api-key")
client = uc.HttpClient(auth_config=auth_config)

# API key in query parameters
auth_config = uc.AuthConfig.api_key_query("api_key", "your-api-key")
client = uc.HttpClient(auth_config=auth_config)
```

## Error Handling

Always handle errors gracefully:

```python
import ultrafast_client as uc

client = uc.HttpClient()

try:
    response = client.get("https://httpbin.org/status/404")
    
    if response.ok():
        # Success (2xx status codes)
        data = response.json()
        print("Success:", data)
    elif response.is_client_error():
        # Client errors (4xx status codes)
        print(f"Client error: {response.status_code} - {response.reason()}")
    elif response.is_server_error():
        # Server errors (5xx status codes)
        print(f"Server error: {response.status_code} - {response.reason()}")
        
except uc.UltraFastError as e:
    # Network errors, timeouts, etc.
    print(f"Request failed: {e}")
except Exception as e:
    # Other unexpected errors
    print(f"Unexpected error: {e}")
```

## Configuration

### Timeouts
```python
# Configure timeouts
timeout_config = uc.TimeoutConfig(
    connect_timeout=10.0,    # 10 seconds to connect
    read_timeout=30.0,       # 30 seconds to read response
    total_timeout=60.0       # 60 seconds maximum total time
)

client = uc.HttpClient(timeout_config=timeout_config)
```

### Retries
```python
# Configure retry behavior
retry_config = uc.RetryConfig(
    max_retries=3,           # Try up to 3 times
    initial_delay=1.0,       # Start with 1 second delay
    max_delay=10.0,          # Maximum delay of 10 seconds
    backoff_factor=2.0       # Double the delay each retry
)

client = uc.HttpClient(retry_config=retry_config)
```

## Asynchronous Programming

For high-performance applications, use async/await:

### Basic Async Request
```python
import asyncio
import ultrafast_client as uc

async def fetch_user(user_id):
    client = uc.AsyncHttpClient()
    response = await client.get(f"https://api.github.com/users/{user_id}")
    return response.json()

# Run async function
async def main():
    user = await fetch_user("octocat")
    print(f"User: {user['name']}")

asyncio.run(main())
```

### Concurrent Requests
```python
async def fetch_multiple_users():
    client = uc.AsyncHttpClient()
    
    # Create multiple tasks
    tasks = [
        client.get("https://api.github.com/users/octocat"),
        client.get("https://api.github.com/users/defunkt"),
        client.get("https://api.github.com/users/mojombo")
    ]
    
    # Execute concurrently
    responses = await asyncio.gather(*tasks)
    
    # Process results
    for response in responses:
        user = response.json()
        print(f"User: {user['login']} - {user['name']}")

asyncio.run(fetch_multiple_users())
```

## Sessions

Use sessions to maintain state across requests:

### Basic Session Usage
```python
# Create a session
session = uc.Session()
session.set_base_url("https://api.github.com")

# Login (simulate)
login_response = session.post("/user", json={"token": "your-token"})

# Subsequent requests use the same session
user_response = session.get("/user")
repos_response = session.get("/user/repos")

print(f"User: {user_response.json()['login']}")
print(f"Repos: {len(repos_response.json())}")
```

### Session with Context Manager
```python
with uc.Session() as session:
    session.set_base_url("https://httpbin.org")
    session.set_auth(uc.AuthConfig.bearer("token"))
    
    response1 = session.get("/get")
    response2 = session.post("/post", json={"data": "test"})
    
    print(f"Request 1: {response1.status_code}")
    print(f"Request 2: {response2.status_code}")
# Session automatically closed
```

## Real-World Example: GitHub API

Here's a complete example using the GitHub API:

```python
import ultrafast_client as uc
import os

def github_example():
    # Get token from environment variable
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("Please set GITHUB_TOKEN environment variable")
        return
    
    # Create authenticated client
    auth_config = uc.AuthConfig.bearer(github_token)
    client = uc.HttpClient(
        auth_config=auth_config,
        headers={"Accept": "application/vnd.github.v3+json"}
    )
    
    try:
        # Get authenticated user
        user_response = client.get("https://api.github.com/user")
        user = user_response.json()
        
        print(f"Hello, {user['name']} (@{user['login']})!")
        print(f"You have {user['public_repos']} public repositories")
        
        # Get user's repositories
        repos_response = client.get(
            "https://api.github.com/user/repos",
            params={"sort": "updated", "per_page": 5}
        )
        repos = repos_response.json()
        
        print("\nYour 5 most recently updated repositories:")
        for repo in repos:
            print(f"  📂 {repo['name']} - ⭐ {repo['stargazers_count']} stars")
            
    except uc.UltraFastError as e:
        print(f"GitHub API request failed: {e}")

# Run the example
github_example()
```

## Next Steps

Now that you know the basics, explore more advanced features:

1. **[API Reference](../api/README.md)** - Complete API documentation
2. **[Examples](../../examples/README.md)** - Comprehensive examples for all features
3. **[Authentication Guide](authentication.md)** - Detailed authentication patterns
4. **[Performance Guide](performance.md)** - Optimization and benchmarking
5. **[Real-time Guide](real-time.md)** - WebSocket and SSE communication

## Common Patterns

### API Client Class
```python
class GitHubClient:
    def __init__(self, token):
        self.client = uc.HttpClient(
            auth_config=uc.AuthConfig.bearer(token),
            headers={"Accept": "application/vnd.github.v3+json"}
        )
        self.base_url = "https://api.github.com"
    
    def get_user(self, username=None):
        url = f"{self.base_url}/user" if not username else f"{self.base_url}/users/{username}"
        response = self.client.get(url)
        return response.json() if response.ok() else None
    
    def get_repos(self, username=None):
        url = f"{self.base_url}/user/repos" if not username else f"{self.base_url}/users/{username}/repos"
        response = self.client.get(url)
        return response.json() if response.ok() else []

# Usage
github = GitHubClient("your-token")
user = github.get_user()
repos = github.get_repos()
```

### Retry with Custom Logic
```python
def resilient_request(url, max_attempts=3):
    client = uc.HttpClient()
    
    for attempt in range(max_attempts):
        try:
            response = client.get(url)
            if response.ok():
                return response
            elif response.status_code >= 500:
                # Server error, retry
                print(f"Server error {response.status_code}, retrying... ({attempt + 1}/{max_attempts})")
                continue
            else:
                # Client error, don't retry
                return response
        except uc.UltraFastError as e:
            print(f"Request failed: {e}, retrying... ({attempt + 1}/{max_attempts})")
            if attempt == max_attempts - 1:
                raise
    
    return None
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure ultrafast-client is installed: `pip install ultrafast-client`
2. **SSL Errors**: Use `ssl_config=uc.SSLConfig(verify_certificates=False)` for development
3. **Timeout Errors**: Increase timeout values: `timeout_config=uc.TimeoutConfig(total_timeout=120.0)`
4. **Rate Limiting**: Use `rate_limit_config=uc.RateLimitConfig.conservative()` for APIs with strict limits

### Debug Mode
```python
# Enable verbose logging for debugging
import logging
logging.basicConfig(level=logging.DEBUG)

client = uc.HttpClient()
response = client.get("https://httpbin.org/get")
```

You're now ready to build amazing applications with UltraFast HTTP Client! 🎉
