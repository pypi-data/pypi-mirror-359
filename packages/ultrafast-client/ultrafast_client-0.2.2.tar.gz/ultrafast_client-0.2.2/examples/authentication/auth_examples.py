#!/usr/bin/env python3
"""
Authentication Examples
=======================

Comprehensive examples for different authentication methods supported by UltraFast HTTP Client.
"""

import asyncio
import os

import ultrafast_client as uc


def bearer_token_auth():
    """Bearer token authentication example."""
    print("=== Bearer Token Authentication ===")

    # Create bearer token auth config
    auth_config = uc.AuthConfig.bearer("your-api-token-here")

    # Create client with authentication
    client = uc.HttpClient(auth_config=auth_config)

    # Make authenticated request
    try:
        response = client.get("https://httpbin.org/bearer")
        print(f"Status: {response.status_code}")

        if response.ok():
            data = response.json()
            print(f"Authenticated: {data['authenticated']}")
            print(f"Token: {data['token']}")
        else:
            print(f"Authentication failed: {response.status_code}")
    except Exception as e:
        print(f"Request failed: {e}")

    print()


def basic_auth():
    """Basic authentication example."""
    print("=== Basic Authentication ===")

    # Create basic auth config
    auth_config = uc.AuthConfig.basic("testuser", "testpass")

    client = uc.HttpClient(auth_config=auth_config)

    # Test with httpbin's basic auth endpoint
    try:
        response = client.get("https://httpbin.org/basic-auth/testuser/testpass")
        print(f"Status: {response.status_code}")

        if response.ok():
            data = response.json()
            print(f"Authenticated: {data['authenticated']}")
            print(f"User: {data['user']}")
        else:
            print(f"Authentication failed: {response.status_code}")
    except Exception as e:
        print(f"Request failed: {e}")

    print()


def api_key_auth():
    """API Key authentication examples."""
    print("=== API Key Authentication ===")

    # API Key in headers
    print("API Key in Headers:")
    auth_config = uc.AuthConfig.api_key_header("X-API-Key", "your-api-key-here")
    client = uc.HttpClient(auth_config=auth_config)

    response = client.get("https://httpbin.org/headers")
    data = response.json()
    print(f"Headers sent: {data['headers']}")

    # API Key in query parameters
    print("\nAPI Key in Query Parameters:")
    auth_config = uc.AuthConfig.api_key_query("api_key", "your-api-key-here")
    client = uc.HttpClient(auth_config=auth_config)

    response = client.get("https://httpbin.org/get")
    data = response.json()
    print(f"Query args: {data['args']}")

    print()


def oauth2_example():
    """OAuth2 authentication example (mock)."""
    print("=== OAuth2 Authentication ===")

    # Create OAuth2 config
    auth_config = uc.AuthConfig.oauth2(
        client_id="your-client-id",
        client_secret="your-client-secret",
        token_url="https://auth.example.com/token",
        scope="read write",
    )

    # In a real scenario, you would:
    # 1. Redirect user to authorization URL
    # 2. Get authorization code from callback
    # 3. Exchange code for access token
    # 4. Use access token for API requests

    print("OAuth2 configuration created")
    print(f"Client ID: {auth_config.get_credential('client_id')}")
    print(f"Token URL: {auth_config.get_credential('token_url')}")
    print(f"Scope: {auth_config.get_credential('scope')}")
    print(
        "Note: This is a configuration example - real OAuth2 flow requires authorization server"
    )

    print()


def github_api_example():
    """Real-world example with GitHub API."""
    print("=== GitHub API Example ===")

    # Get token from environment variable for security
    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        print("Set GITHUB_TOKEN environment variable to run this example")
        print("export GITHUB_TOKEN='your_github_personal_access_token'")
        return

    # Create authenticated client
    auth_config = uc.AuthConfig.bearer(github_token)
    client = uc.HttpClient(auth_config=auth_config)

    try:
        # Get authenticated user info
        response = client.get("https://api.github.com/user")

        if response.ok():
            user = response.json()
            print(f"✅ GitHub user: {user['login']}")
            print(f"Name: {user.get('name', 'N/A')}")
            print(f"Public repos: {user['public_repos']}")
            print(f"Followers: {user['followers']}")

            # Get user's repositories
            repos_response = client.get("https://api.github.com/user/repos?per_page=5")
            if repos_response.ok():
                repos = repos_response.json()
                print("\nRecent repositories:")
                for repo in repos[:5]:
                    print(f"  - {repo['name']} ⭐ {repo['stargazers_count']}")
        else:
            print(f"❌ GitHub API error: {response.status_code}")

    except Exception as e:
        print(f"Request failed: {e}")

    print()


def dynamic_auth_switching():
    """Example of switching authentication methods dynamically."""
    print("=== Dynamic Authentication Switching ===")

    client = uc.HttpClient()

    # Test with different auth methods
    auth_methods = [
        ("No Auth", None),
        ("Bearer Token", uc.AuthConfig.bearer("test-token")),
        ("Basic Auth", uc.AuthConfig.basic("user", "pass")),
        ("API Key", uc.AuthConfig.api_key_header("X-API-Key", "test-key")),
    ]

    for auth_name, auth_config in auth_methods:
        print(f"Testing with {auth_name}:")

        # Set or clear authentication
        if auth_config:
            client.set_auth(auth_config)
        else:
            client.clear_auth()

        # Check current auth status
        has_auth = client.has_auth()
        print(f"  Has auth: {has_auth}")

        if has_auth:
            current_auth = client.get_auth()
            print(f"  Auth type: {current_auth.auth_type}")

        # Make request to see headers
        response = client.get("https://httpbin.org/headers")
        if response.ok():
            headers = response.json()["headers"]
            auth_header = headers.get("Authorization", "None")
            print(f"  Auth header: {auth_header}")

        print()


def session_based_auth():
    """Session-based authentication example."""
    print("=== Session-Based Authentication ===")

    # Simulate login flow with session
    session = uc.Session()
    session.set_base_url("https://httpbin.org")

    # Step 1: Login (simulate)
    login_data = {"username": "demo_user", "password": "demo_pass"}

    login_response = session.post("/post", json=login_data)  # Simulate login endpoint
    print(f"Login response: {login_response.status_code}")

    # Step 2: Set authentication for subsequent requests
    auth_config = uc.AuthConfig.bearer("session-token-from-login")
    session.set_auth(auth_config)

    # Step 3: Make authenticated requests
    profile_response = session.get("/get")  # Simulate profile endpoint
    print(f"Profile response: {profile_response.status_code}")

    settings_response = session.get("/headers")  # Check what headers are sent
    if settings_response.ok():
        headers = settings_response.json()["headers"]
        print(f"Session headers include auth: {'Authorization' in headers}")

    print()


async def async_auth_example():
    """Asynchronous authentication example."""
    print("=== Async Authentication ===")

    # Create async client with auth
    auth_config = uc.AuthConfig.bearer("async-token")
    client = uc.AsyncHttpClient(auth_config=auth_config)

    # Make multiple concurrent authenticated requests
    urls = [
        "https://httpbin.org/headers",
        "https://httpbin.org/get",
        "https://httpbin.org/bearer",
    ]

    tasks = [client.get(url) for url in urls]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    for i, response in enumerate(responses):
        if isinstance(response, Exception):
            print(f"Request {i+1} failed: {response}")
        else:
            print(f"Request {i+1}: {response.status_code}")

    print()


def auth_validation_example():
    """Authentication configuration validation."""
    print("=== Authentication Validation ===")

    # Valid configurations
    valid_configs = [
        uc.AuthConfig.bearer("valid-token"),
        uc.AuthConfig.basic("user", "pass"),
        uc.AuthConfig.api_key_header("X-API-Key", "key"),
        uc.AuthConfig.oauth2(
            "client_id", "client_secret", "https://auth.example.com/token"
        ),
    ]

    for i, config in enumerate(valid_configs, 1):
        try:
            config.validate()
            print(f"✅ Auth config {i}: Valid")
        except Exception as e:
            print(f"❌ Auth config {i}: Invalid - {e}")

    # Test invalid configurations
    print("\nTesting invalid configurations:")

    try:
        # Missing token
        invalid_config = uc.AuthConfig.bearer("")
        invalid_config.validate()
    except Exception as e:
        print(f"✅ Empty bearer token correctly rejected: {e}")

    try:
        # Missing username in basic auth
        invalid_config = uc.AuthConfig.basic("", "password")
        invalid_config.validate()
    except Exception as e:
        print(f"✅ Empty username correctly rejected: {e}")

    print()


async def main():
    """Run all authentication examples."""
    print("🔐 UltraFast HTTP Client - Authentication Examples\n")

    bearer_token_auth()
    basic_auth()
    api_key_auth()
    oauth2_example()
    github_api_example()
    dynamic_auth_switching()
    session_based_auth()
    await async_auth_example()
    auth_validation_example()

    print("✅ All authentication examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
