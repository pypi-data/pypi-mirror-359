#!/usr/bin/env python3
"""
Async HTTP Requests Examples
============================

Examples showing asynchronous HTTP requests for high-performance applications.
"""

import asyncio
import time

import ultrafast_client as uc


async def basic_async_request():
    """Simple async GET request."""
    print("=== Basic Async Request ===")

    client = uc.AsyncHttpClient()
    response = await client.get("https://httpbin.org/get")

    print(f"Status: {response.status_code}")
    print(f"Content: {response.text()[:100]}...")
    print()


async def concurrent_requests():
    """Multiple concurrent requests for better performance."""
    print("=== Concurrent Requests ===")

    client = uc.AsyncHttpClient()

    # URLs to fetch concurrently
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/get",
        "https://httpbin.org/uuid",
    ]

    start_time = time.time()

    # Execute all requests concurrently
    tasks = [client.get(url) for url in urls]
    responses = await asyncio.gather(*tasks)

    end_time = time.time()

    print(f"Made {len(responses)} requests in {end_time - start_time:.2f} seconds")
    for i, response in enumerate(responses):
        print(f"  Request {i+1}: {response.status_code}")
    print()


async def async_post_requests():
    """Async POST requests with different data types."""
    print("=== Async POST Requests ===")

    client = uc.AsyncHttpClient()

    # JSON POST
    json_response = await client.post(
        "https://httpbin.org/post",
        json={"message": "Hello from async!", "timestamp": time.time()},
    )

    print(f"JSON POST: {json_response.status_code}")

    # Form data POST
    form_response = await client.post(
        "https://httpbin.org/post", data={"username": "async_user", "action": "login"}
    )

    print(f"Form POST: {form_response.status_code}")
    print()


async def async_with_session():
    """Using async sessions for state management."""
    print("=== Async Session Example ===")

    async with uc.AsyncSession() as session:
        session.set_base_url("https://httpbin.org")
        session.set_header("User-Agent", "AsyncExample/1.0")

        # Multiple requests with shared session state
        response1 = await session.get("/get")
        response2 = await session.post("/post", json={"session": "test"})
        response3 = await session.get("/headers")

        print(f"Session request 1: {response1.status_code}")
        print(f"Session request 2: {response2.status_code}")
        print(f"Session request 3: {response3.status_code}")

    print("Session automatically closed")
    print()


async def async_error_handling():
    """Error handling in async requests."""
    print("=== Async Error Handling ===")

    client = uc.AsyncHttpClient()

    # List of URLs with different outcomes
    test_urls = [
        "https://httpbin.org/get",  # Success
        "https://httpbin.org/status/404",  # Client error
        "https://httpbin.org/status/500",  # Server error
        "https://httpbin.org/delay/10",  # Will timeout
    ]

    for url in test_urls:
        try:
            response = await client.get(url)

            if response.ok():
                print(f"✅ {url}: Success ({response.status_code})")
            elif response.is_client_error():
                print(f"⚠️  {url}: Client error ({response.status_code})")
            elif response.is_server_error():
                print(f"❌ {url}: Server error ({response.status_code})")

        except Exception as e:
            print(f"🔥 {url}: Exception - {e}")

    print()


async def producer_consumer_pattern():
    """Producer-consumer pattern with async requests."""
    print("=== Producer-Consumer Pattern ===")

    # Queue for URLs to process
    url_queue = asyncio.Queue()
    results_queue = asyncio.Queue()

    # Add URLs to process
    urls = [f"https://httpbin.org/delay/{i}" for i in range(1, 6)]
    for url in urls:
        await url_queue.put(url)

    async def producer():
        """Produce HTTP requests."""
        client = uc.AsyncHttpClient()

        while not url_queue.empty():
            try:
                url = await asyncio.wait_for(url_queue.get(), timeout=1.0)
                print(f"🔄 Processing: {url}")
                response = await client.get(url)
                await results_queue.put((url, response.status_code))
                url_queue.task_done()
            except asyncio.TimeoutError:
                break

    async def consumer():
        """Consume results."""
        while True:
            try:
                url, status = await asyncio.wait_for(results_queue.get(), timeout=2.0)
                print(f"✅ Completed: {url} -> {status}")
                results_queue.task_done()
            except asyncio.TimeoutError:
                break

    # Run producer and consumer concurrently
    await asyncio.gather(producer(), consumer())

    print("Producer-consumer pattern completed")
    print()


async def benchmark_async_performance():
    """Benchmark async vs sync performance."""
    print("=== Performance Comparison ===")

    num_requests = 20
    url = "https://httpbin.org/delay/0.1"

    # Async performance
    async_client = uc.AsyncHttpClient()

    start_time = time.time()
    async_tasks = [async_client.get(url) for _ in range(num_requests)]
    async_responses = await asyncio.gather(*async_tasks)
    async_time = time.time() - start_time

    print(
        f"Async: {num_requests} requests in {async_time:.2f}s ({num_requests/async_time:.1f} req/s)"
    )

    # Sync performance (sequential)
    sync_client = uc.HttpClient()

    start_time = time.time()
    sync_responses = []
    for _ in range(num_requests):
        response = sync_client.get(url)
        sync_responses.append(response)
    sync_time = time.time() - start_time

    print(
        f"Sync:  {num_requests} requests in {sync_time:.2f}s ({num_requests/sync_time:.1f} req/s)"
    )
    print(f"Speedup: {sync_time/async_time:.1f}x faster with async")
    print()


async def main():
    """Run all async examples."""
    print("🚀 UltraFast HTTP Client - Async Examples\n")

    await basic_async_request()
    await concurrent_requests()
    await async_post_requests()
    await async_with_session()
    await async_error_handling()
    await producer_consumer_pattern()
    await benchmark_async_performance()

    print("✅ All async examples completed!")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
