#!/usr/bin/env python3
"""
Basic HTTP Requests Examples
=============================

Simple examples showing how to make basic HTTP requests with UltraFast HTTP Client.
"""

import ultrafast_client as uc


def basic_get_request():
    """Simple GET request example."""
    print("=== Basic GET Request ===")

    client = uc.HttpClient()
    response = client.get("https://httpbin.org/get")

    print(f"Status: {response.status_code}")
    print(f"URL: {response.url()}")
    print(f"Content Length: {response.size()} bytes")
    print(f"Success: {response.ok()}")

    # Parse JSON response
    data = response.json()
    print(f"User Agent: {data['headers']['User-Agent']}")
    print()


def post_with_json():
    """POST request with JSON data."""
    print("=== POST with JSON ===")

    client = uc.HttpClient()

    # Data to send
    payload = {"name": "John Doe", "email": "john@example.com", "age": 30}

    response = client.post("https://httpbin.org/post", json=payload)

    print(f"Status: {response.status_code}")
    print(f"Request successful: {response.ok()}")

    # Check what was sent
    data = response.json()
    print(f"Sent data: {data['json']}")
    print()


def custom_headers():
    """Request with custom headers."""
    print("=== Custom Headers ===")

    headers = {
        "User-Agent": "UltraFast-Example/1.0",
        "Accept": "application/json",
        "X-Custom-Header": "MyValue",
    }

    client = uc.HttpClient(headers=headers)
    response = client.get("https://httpbin.org/headers")

    data = response.json()
    print(f"Sent headers: {data['headers']}")
    print()


def query_parameters():
    """GET request with query parameters."""
    print("=== Query Parameters ===")

    client = uc.HttpClient()

    # Using params argument
    params = {"q": "python http client", "sort": "stars", "order": "desc"}

    response = client.get("https://httpbin.org/get", params=params)

    data = response.json()
    print(f"Final URL: {data['url']}")
    print(f"Query args: {data['args']}")
    print()


def different_http_methods():
    """Examples of different HTTP methods."""
    print("=== Different HTTP Methods ===")

    client = uc.HttpClient()
    base_url = "https://httpbin.org"

    # GET
    get_response = client.get(f"{base_url}/get")
    print(f"GET: {get_response.status_code}")

    # POST
    post_response = client.post(f"{base_url}/post", json={"test": "data"})
    print(f"POST: {post_response.status_code}")

    # PUT
    put_response = client.put(f"{base_url}/put", json={"update": "data"})
    print(f"PUT: {put_response.status_code}")

    # PATCH
    patch_response = client.patch(f"{base_url}/patch", json={"patch": "data"})
    print(f"PATCH: {patch_response.status_code}")

    # DELETE
    delete_response = client.delete(f"{base_url}/delete")
    print(f"DELETE: {delete_response.status_code}")

    # HEAD (only headers, no body)
    head_response = client.head(f"{base_url}/get")
    print(f"HEAD: {head_response.status_code} (body size: {head_response.size()})")

    # OPTIONS
    options_response = client.options(f"{base_url}/get")
    print(f"OPTIONS: {options_response.status_code}")
    print()


def error_handling():
    """Basic error handling example."""
    print("=== Error Handling ===")

    client = uc.HttpClient()

    try:
        # This will return a 404 error
        response = client.get("https://httpbin.org/status/404")

        if response.is_client_error():
            print(f"Client error: {response.status_code} - {response.reason()}")
        elif response.is_server_error():
            print(f"Server error: {response.status_code} - {response.reason()}")
        else:
            print(f"Success: {response.status_code}")

    except Exception as e:
        print(f"Request failed: {e}")

    print()


if __name__ == "__main__":
    print("🚀 UltraFast HTTP Client - Basic Examples\n")

    basic_get_request()
    post_with_json()
    custom_headers()
    query_parameters()
    different_http_methods()
    error_handling()

    print("✅ All examples completed!")
