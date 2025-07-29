#!/usr/bin/env python3
"""
Performance Benchmarking Examples
=================================

Examples demonstrating performance testing and benchmarking capabilities.
"""

import asyncio
import concurrent.futures
import statistics
import time

import ultrafast_client as uc


def basic_benchmark():
    """Basic benchmarking example."""
    print("=== Basic Benchmark ===")

    # Create benchmark runner
    benchmark = uc.BenchmarkRunner()

    def test_function():
        """Simple HTTP request function to benchmark."""
        client = uc.HttpClient()
        return client.get("https://httpbin.org/get")

    # Run benchmark
    print("Running benchmark with 50 iterations, 5 concurrent requests...")
    results = benchmark.run_benchmark(
        test_function, iterations=50, concurrent_requests=5
    )

    print("📊 Benchmark Results:")
    print(f"  Average response time: {results.average_time:.2f}ms")
    print(f"  Requests per second: {results.requests_per_second:.1f}")
    print(f"  Success rate: {results.success_rate:.1f}%")
    print(f"  Min response time: {results.min_time:.2f}ms")
    print(f"  Max response time: {results.max_time:.2f}ms")
    print()


def detailed_benchmark():
    """Detailed benchmark with custom metrics."""
    print("=== Detailed Benchmark ===")

    # Create detailed benchmark
    benchmark = uc.Benchmark(
        name="HTTP Performance Test",
        url="https://httpbin.org/delay/0.5",  # 500ms delay
        method="GET",
        headers={"User-Agent": "UltraFast-Benchmark/1.0"},
        concurrent_requests=10,
        total_requests=100,
        timeout=30.0,
    )

    print("Running detailed benchmark...")
    print(f"URL: {benchmark.url}")
    print(f"Concurrent requests: {benchmark.concurrent_requests}")
    print(f"Total requests: {benchmark.total_requests}")

    results = benchmark.run()

    print("\n📊 Detailed Results:")
    print(f"  Total time: {results.total_time:.2f}s")
    print(f"  Average response time: {results.avg_response_time:.2f}ms")
    print(f"  Median response time: {results.median_response_time:.2f}ms")
    print(f"  95th percentile: {results.p95_response_time:.2f}ms")
    print(f"  99th percentile: {results.p99_response_time:.2f}ms")
    print(f"  Requests per second: {results.requests_per_second:.1f}")
    print(f"  Error rate: {results.error_rate:.1f}%")
    print(f"  Throughput: {results.throughput_mbps:.2f} MB/s")
    print()


def memory_profiling():
    """Memory usage profiling example."""
    print("=== Memory Profiling ===")

    # Profile memory usage during HTTP requests
    with uc.MemoryProfiler() as profiler:
        print("Making 100 HTTP requests while profiling memory...")

        client = uc.HttpClient()
        responses = []

        for i in range(100):
            response = client.get("https://httpbin.org/get")
            responses.append(response)

            if (i + 1) % 25 == 0:
                print(f"  Completed {i + 1}/100 requests")

    # Get memory statistics
    memory_stats = profiler.get_stats()

    print("\n🧠 Memory Statistics:")
    print(f"  Peak memory usage: {memory_stats.peak_memory_mb:.2f} MB")
    print(f"  Memory growth: {memory_stats.memory_growth_mb:.2f} MB")
    print(f"  Final memory usage: {memory_stats.final_memory_mb:.2f} MB")
    print(f"  Allocations: {memory_stats.allocations}")
    print(f"  Deallocations: {memory_stats.deallocations}")
    print()


async def async_performance_comparison():
    """Compare sync vs async performance."""
    print("=== Sync vs Async Performance Comparison ===")

    num_requests = 50
    urls = ["https://httpbin.org/delay/0.1" for _ in range(num_requests)]

    # Measure sync performance (sequential)
    print(f"Testing sync performance with {num_requests} sequential requests...")
    sync_client = uc.HttpClient()

    sync_start = time.time()
    sync_responses = []
    for url in urls:
        response = sync_client.get(url)
        sync_responses.append(response)
    sync_time = time.time() - sync_start

    sync_rps = num_requests / sync_time
    print(f"  Sync (sequential): {sync_time:.2f}s ({sync_rps:.1f} req/s)")

    # Measure sync performance (threaded)
    print(f"Testing sync performance with {num_requests} threaded requests...")

    def make_sync_request(url):
        client = uc.HttpClient()
        return client.get(url)

    threaded_start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        threaded_responses = list(executor.map(make_sync_request, urls))
    threaded_time = time.time() - threaded_start

    threaded_rps = num_requests / threaded_time
    print(f"  Sync (threaded): {threaded_time:.2f}s ({threaded_rps:.1f} req/s)")

    # Measure async performance
    print(f"Testing async performance with {num_requests} concurrent requests...")
    async_client = uc.AsyncHttpClient()

    async_start = time.time()
    async_tasks = [async_client.get(url) for url in urls]
    async_responses = await asyncio.gather(*async_tasks)
    async_time = time.time() - async_start

    async_rps = num_requests / async_time
    print(f"  Async (concurrent): {async_time:.2f}s ({async_rps:.1f} req/s)")

    # Calculate speedups
    sync_speedup = sync_time / async_time
    threaded_speedup = threaded_time / async_time

    print("\n⚡ Performance Comparison:")
    print(f"  Async vs Sync Sequential: {sync_speedup:.1f}x faster")
    print(f"  Async vs Sync Threaded: {threaded_speedup:.1f}x faster")
    print(f"  Sync Threaded vs Sequential: {sync_time/threaded_time:.1f}x faster")
    print()


def rate_limiting_performance():
    """Test rate limiting performance."""
    print("=== Rate Limiting Performance ===")

    # Test different rate limiting configurations
    rate_configs = [
        ("No Rate Limiting", None),
        ("Conservative (1 req/s)", uc.RateLimitConfig.conservative()),
        ("Moderate (10 req/s)", uc.RateLimitConfig.moderate()),
        ("Aggressive (100 req/s)", uc.RateLimitConfig.aggressive()),
    ]

    num_requests = 10

    for config_name, rate_config in rate_configs:
        print(f"Testing {config_name}:")

        client = uc.HttpClient(rate_limit_config=rate_config)

        start_time = time.time()
        response_times = []

        for i in range(num_requests):
            request_start = time.time()
            response = client.get("https://httpbin.org/get")
            request_end = time.time()

            response_times.append(request_end - request_start)

            if response.ok():
                elapsed = time.time() - start_time
                print(f"  Request {i+1}: {response.status_code} at {elapsed:.2f}s")

        total_time = time.time() - start_time
        avg_response_time = statistics.mean(response_times)
        actual_rps = num_requests / total_time

        print(f"  Total time: {total_time:.2f}s")
        print(f"  Average response time: {avg_response_time:.3f}s")
        print(f"  Actual rate: {actual_rps:.1f} req/s")
        print()


def connection_pooling_benchmark():
    """Benchmark connection pooling performance."""
    print("=== Connection Pooling Benchmark ===")

    # Test with and without connection pooling
    pool_configs = [
        (
            "No Pooling",
            uc.PoolConfig(max_connections_per_host=1, max_idle_connections=0),
        ),
        (
            "Small Pool",
            uc.PoolConfig(max_connections_per_host=5, max_idle_connections=2),
        ),
        (
            "Large Pool",
            uc.PoolConfig(max_connections_per_host=20, max_idle_connections=10),
        ),
    ]

    num_requests = 20

    for config_name, pool_config in pool_configs:
        print(f"Testing {config_name}:")

        client = uc.HttpClient(pool_config=pool_config)

        # Warm up connection pool
        client.get("https://httpbin.org/get")

        # Measure performance
        start_time = time.time()
        for i in range(num_requests):
            response = client.get("https://httpbin.org/get")
            if not response.ok():
                print(f"  Request {i+1} failed: {response.status_code}")

        total_time = time.time() - start_time
        rps = num_requests / total_time

        print(f"  Time: {total_time:.2f}s")
        print(f"  Rate: {rps:.1f} req/s")
        print()


def compression_performance():
    """Test compression performance impact."""
    print("=== Compression Performance ===")

    # Test with different compression settings
    compression_configs = [
        (
            "No Compression",
            uc.CompressionConfig(
                enable_gzip=False, enable_deflate=False, enable_brotli=False
            ),
        ),
        (
            "Gzip Only",
            uc.CompressionConfig(
                enable_gzip=True, enable_deflate=False, enable_brotli=False
            ),
        ),
        ("All Compression", uc.CompressionConfig.all_algorithms()),
    ]

    # Use an endpoint that returns large data
    test_url = "https://httpbin.org/json"
    num_requests = 10

    for config_name, compression_config in compression_configs:
        print(f"Testing {config_name}:")

        client = uc.HttpClient(compression_config=compression_config)

        start_time = time.time()
        total_bytes = 0

        for i in range(num_requests):
            response = client.get(test_url)
            if response.ok():
                total_bytes += response.size()

        total_time = time.time() - start_time
        avg_size = total_bytes / num_requests
        throughput = total_bytes / total_time / 1024 / 1024  # MB/s

        print(f"  Time: {total_time:.2f}s")
        print(f"  Average response size: {avg_size:.0f} bytes")
        print(f"  Throughput: {throughput:.2f} MB/s")
        print()


def protocol_benchmark():
    """Benchmark different HTTP protocol versions."""
    print("\n=== Protocol Version Benchmark ===")

    # HTTP/1.1 client
    http1_client = uc.HttpClient(
        protocol_config=uc.ProtocolConfig(
            preferred_version=uc.HttpVersion.Http1, enable_http2=False
        )
    )

    # HTTP/2 client
    http2_client = uc.HttpClient(
        protocol_config=uc.ProtocolConfig(
            preferred_version=uc.HttpVersion.Http2,
            enable_http2=True,
            fallback_strategy=uc.ProtocolFallback.Http2ToHttp1,
        )
    )

    # Auto-negotiating client (recommended)
    auto_client = uc.HttpClient(
        protocol_config=uc.ProtocolConfig(
            preferred_version=uc.HttpVersion.Auto,
            enable_http2=True,
            fallback_strategy=uc.ProtocolFallback.Http2ToHttp1,
        )
    )

    clients = [
        ("HTTP/1.1", http1_client),
        ("HTTP/2", http2_client),
        ("Auto-Negotiate", auto_client),
    ]

    url = "https://httpbin.org/get"
    iterations = 10

    for name, client in clients:
        print(f"\nTesting {name}:")
        times = []

        for _ in range(iterations):
            start = time.time()
            try:
                response = client.get(url)
                end = time.time()
                if response.status_code == 200:
                    times.append(end - start)
            except Exception as e:
                print(f"  Error: {e}")

        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)

            print(f"  Average: {avg_time:.3f}s")
            print(f"  Min: {min_time:.3f}s")
            print(f"  Max: {max_time:.3f}s")
            print(f"  Requests/sec: {1/avg_time:.1f}")
        else:
            print("  No successful requests")


def custom_benchmark_suite():
    """Create a custom benchmark suite."""
    print("=== Custom Benchmark Suite ===")

    # Create benchmark suite
    suite = uc.BenchmarkSuite()

    # Add different test scenarios
    scenarios = [
        {
            "name": "Small Response",
            "url": "https://httpbin.org/get",
            "requests": 20,
            "concurrency": 5,
        },
        {
            "name": "Large Response",
            "url": "https://httpbin.org/json",
            "requests": 10,
            "concurrency": 3,
        },
        {
            "name": "Delayed Response",
            "url": "https://httpbin.org/delay/1",
            "requests": 5,
            "concurrency": 2,
        },
    ]

    for scenario in scenarios:
        print(f"Running scenario: {scenario['name']}")

        benchmark = uc.Benchmark(
            name=scenario["name"],
            url=scenario["url"],
            method="GET",
            concurrent_requests=scenario["concurrency"],
            total_requests=scenario["requests"],
        )

        results = benchmark.run()

        print(f"  Average time: {results.avg_response_time:.2f}ms")
        print(f"  Requests/sec: {results.requests_per_second:.1f}")
        print(f"  Success rate: {(100 - results.error_rate):.1f}%")
        print()


async def main():
    """Run all performance examples."""
    print("⚡ UltraFast HTTP Client - Performance Examples\n")

    basic_benchmark()
    detailed_benchmark()
    memory_profiling()
    await async_performance_comparison()
    rate_limiting_performance()
    connection_pooling_benchmark()
    compression_performance()
    protocol_benchmark()
    custom_benchmark_suite()

    print("✅ All performance examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
