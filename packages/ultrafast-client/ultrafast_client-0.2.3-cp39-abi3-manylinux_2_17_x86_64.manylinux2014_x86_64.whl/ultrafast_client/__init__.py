"""
UltraFast HTTP Client

A blazingly fast HTTP client for Python, built with Rust and Tokio.
"""

from typing import Any, Dict

from ._ultrafast_client import (  # type: ignore[import-not-found]
    AsyncHttpClient,
    AsyncSession,
    AsyncSSEClient,
    AsyncWebSocketClient,
    AuthConfig,
    AuthMiddleware,
    AuthType,
    Benchmark,
    BenchmarkRunner,
    BenchmarkSuite,
    ClientResponse,
    CompressionConfig,
    HeadersMiddleware,
    Http2Settings,
    HttpClient,
    HttpVersion,
    LoggingMiddleware,
    MemoryProfiler,
    MiddlewareConfig,
    MiddlewareManager,
    OAuth2Token,
    PoolConfig,
    ProtocolConfig,
    ProtocolFallback,
    ProxyConfig,
    RateLimitAlgorithm,
    RateLimitConfig,
    RateLimitMiddleware,
    RetryConfig,
    RetryMiddleware,
    Session,
    SSEClient,
    SSEEvent,
    SSEEventIterator,
    SSLConfig,
    TimeoutConfig,
    WebSocketClient,
    WebSocketMessage,
    build_sse_event,
    parse_sse_line,
)


# Backward compatibility aliases and helpers
def create_session(**kwargs: Any) -> Session:
    """Create a new session - alias for Session()"""
    return Session(**kwargs)


def create_async_session(**kwargs: Any) -> AsyncSession:
    """Create a new async session - alias for AsyncSession()"""
    return AsyncSession(**kwargs)


def get(url: str, **kwargs: Any) -> "ClientResponse":
    """Perform a GET request using default client"""
    client = HttpClient()
    return client.get(url, **kwargs)


def post(url: str, **kwargs: Any) -> "ClientResponse":
    """Perform a POST request using default client"""
    client = HttpClient()
    return client.post(url, **kwargs)


def put(url: str, **kwargs: Any) -> "ClientResponse":
    """Perform a PUT request using default client"""
    client = HttpClient()
    return client.put(url, **kwargs)


def delete(url: str, **kwargs: Any) -> "ClientResponse":
    """Perform a DELETE request using default client"""
    client = HttpClient()
    return client.delete(url, **kwargs)


def patch(url: str, **kwargs: Any) -> "ClientResponse":
    """Perform a PATCH request using default client"""
    client = HttpClient()
    return client.patch(url, **kwargs)


def head(url: str, **kwargs: Any) -> "ClientResponse":
    """Perform a HEAD request using default client"""
    client = HttpClient()
    return client.head(url, **kwargs)


def options(url: str, **kwargs: Any) -> "ClientResponse":
    """Perform an OPTIONS request using default client"""
    client = HttpClient()
    return client.options(url, **kwargs)


__version__ = "0.2.3"
__author__ = "UltraFast Team"

__all__ = [
    # Core classes
    "HttpClient",
    "AsyncHttpClient",
    "Session",
    "AsyncSession",
    "ClientResponse",
    # Real-time communication
    "WebSocketClient",
    "AsyncWebSocketClient",
    "WebSocketMessage",
    "SSEClient",
    "AsyncSSEClient",
    "SSEEvent",
    "SSEEventIterator",
    # Configuration classes
    "RetryConfig",
    "SSLConfig",
    "PoolConfig",
    "AuthConfig",
    "AuthType",
    "OAuth2Token",
    "TimeoutConfig",
    "ProxyConfig",
    "CompressionConfig",
    # Protocol configuration
    "ProtocolConfig",
    "HttpVersion",
    "Http2Settings",
    # Middleware
    "MiddlewareManager",
    "MiddlewareConfig",
    "AuthMiddleware",
    "RetryMiddleware",
    "LoggingMiddleware",
    "RateLimitMiddleware",
    "HeadersMiddleware",
    # Rate limiting
    "RateLimitConfig",
    "RateLimitAlgorithm",
    # Performance tools
    "BenchmarkRunner",
    "BenchmarkSuite",
    "Benchmark",
    "MemoryProfiler",
    # Utility functions
    "parse_sse_line",
    "build_sse_event",
    # Convenience functions
    "get",
    "post",
    "put",
    "delete",
    "patch",
    "head",
    "options",
]
