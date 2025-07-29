//! UltraFast HTTP Client
//!
//! A high-performance HTTP client library for Python, built with Rust and PyO3.
//! Provides both synchronous and asynchronous interfaces with comprehensive features.

#![allow(clippy::too_many_arguments)]
#![allow(clippy::enum_variant_names)]
#![allow(clippy::type_complexity)]
#![allow(clippy::derivable_impls)]
#![allow(clippy::field_reassign_with_default)]
#![allow(clippy::declare_interior_mutable_const)]
#![allow(clippy::needless_lifetimes)]
#![allow(clippy::redundant_closure)]
#![allow(clippy::unwrap_or_default)]
#![allow(clippy::assign_op_pattern)]
#![allow(clippy::iter_next_slice)]
#![allow(clippy::while_let_loop)]
#![allow(clippy::implicit_saturating_add)]
#![allow(clippy::manual_range_contains)]
#![allow(clippy::unnecessary_map_or)]
#![allow(non_local_definitions)]

use pyo3::prelude::*;
use tracing_subscriber::{fmt, layer::SubscriberExt, util::SubscriberInitExt, EnvFilter};

// New modular structure
mod clients;
mod config;
mod core;
mod middleware;
mod performance;
mod realtime;
mod utils;

// Import from new modular structure
use clients::{AsyncHttpClient, AsyncSession, HttpClient, Session};
use config::{
    AuthConfig, AuthType, CompressionConfig, Http2Settings, HttpVersion, OAuth2Token, PoolConfig,
    ProtocolConfig, ProtocolFallback, ProxyConfig, RateLimitAlgorithm, RateLimitConfig,
    RetryConfig, SSLConfig, TimeoutConfig,
};
use core::response::ClientResponse;
use middleware::{
    AuthMiddleware, HeadersMiddleware, LoggingMiddleware, MiddlewareConfig, MiddlewareManager,
    RateLimitMiddleware, RetryMiddleware,
};
use performance::benchmarks::Benchmark as BenchmarkConfig;
use performance::{BenchmarkRunner, BenchmarkSuite, MemoryProfiler};
use realtime::{
    build_sse_event, parse_sse_line, AsyncSSEClient, AsyncWebSocketClient, SSEClient, SSEEvent,
    SSEEventIterator, WebSocketClient, WebSocketMessage,
};

/// Initialize tracing for the UltraFast HTTP Client
///
/// Sets up structured logging with configurable levels and output format.
/// Uses the RUST_LOG environment variable for level configuration.
///
/// # Arguments
/// * `level` - Optional log level (trace, debug, info, warn, error). Defaults to "info"
/// * `json_format` - Whether to use JSON format for structured logging. Defaults to false
///
/// # Examples
/// ```python
/// import ultrafast_client as uc
///
/// # Initialize with default settings (info level, pretty format)
/// uc.init_tracing()
///
/// # Initialize with custom level and JSON format
/// uc.init_tracing(level="debug", json_format=True)
/// ```
#[pyfunction]
#[pyo3(signature = (level=None, json_format=false))]
fn init_tracing(level: Option<String>, json_format: bool) -> PyResult<()> {
    // Set default level
    let log_level = level.unwrap_or_else(|| "info".to_string());

    // Create env filter with the specified level
    let env_filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new(format!("ultrafast_client={}", log_level)));

    // Initialize subscriber based on format preference
    if json_format {
        tracing_subscriber::registry()
            .with(env_filter)
            .with(fmt::layer().json())
            .try_init()
            .map_err(|e| {
                pyo3::exceptions::PyRuntimeError::new_err(format!(
                    "Failed to initialize tracing: {}",
                    e
                ))
            })?;
    } else {
        tracing_subscriber::registry()
            .with(env_filter)
            .with(fmt::layer().pretty())
            .try_init()
            .map_err(|e| {
                pyo3::exceptions::PyRuntimeError::new_err(format!(
                    "Failed to initialize tracing: {}",
                    e
                ))
            })?;
    }

    tracing::info!(
        "UltraFast HTTP Client tracing initialized with level: {}",
        log_level
    );
    Ok(())
}

/// Get current tracing configuration information
#[pyfunction]
fn get_tracing_info() -> PyResult<std::collections::HashMap<String, String>> {
    let mut info = std::collections::HashMap::new();
    info.insert("library".to_string(), "ultrafast-client".to_string());
    info.insert("tracing_crate".to_string(), "tracing".to_string());
    info.insert("subscriber".to_string(), "tracing-subscriber".to_string());
    info.insert(
        "features".to_string(),
        "structured logging, spans, events".to_string(),
    );
    Ok(info)
}

/// UltraFast HTTP Client - Production-Ready HTTP Client for Python
///
/// A blazingly fast HTTP client built with Rust and Tokio, providing:
///
/// ## Features
/// - **High Performance**: 2-7x faster than popular Python HTTP libraries
/// - **Protocol Support**: HTTP/1.1, HTTP/2, WebSocket, Server-Sent Events
/// - **Async/Sync APIs**: Both synchronous and asynchronous interfaces
/// - **Advanced Features**: Connection pooling, middleware, rate limiting, compression
/// - **Enterprise Ready**: Authentication, retries, circuit breakers, observability
///
/// ## Quick Start
/// ```python
/// import ultrafast_client as uc
///
/// # Synchronous usage
/// client = uc.HttpClient()
/// response = client.get("https://api.example.com/data")
/// print(response.text())
///
/// # Asynchronous usage  
/// async def main():
///     client = uc.AsyncHttpClient()
///     response = await client.get("https://api.example.com/data")
///     data = response.json()
/// ```
#[pymodule]
fn _ultrafast_client(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Core client classes
    m.add_class::<HttpClient>()?;
    m.add_class::<AsyncHttpClient>()?;
    m.add_class::<Session>()?;
    m.add_class::<AsyncSession>()?;

    // Response
    m.add_class::<ClientResponse>()?;

    // Configuration classes
    m.add_class::<AuthConfig>()?;
    m.add_class::<AuthType>()?;
    m.add_class::<RetryConfig>()?;
    m.add_class::<TimeoutConfig>()?;
    m.add_class::<PoolConfig>()?;
    m.add_class::<SSLConfig>()?;
    m.add_class::<OAuth2Token>()?;
    m.add_class::<ProxyConfig>()?;
    m.add_class::<CompressionConfig>()?;

    // Protocol configuration classes (Phase 5)
    m.add_class::<ProtocolConfig>()?;
    m.add_class::<HttpVersion>()?;
    m.add_class::<Http2Settings>()?;
    m.add_class::<ProtocolFallback>()?;

    // Real-time communication
    m.add_class::<WebSocketClient>()?;
    m.add_class::<AsyncWebSocketClient>()?;
    m.add_class::<WebSocketMessage>()?;
    m.add_class::<SSEClient>()?;
    m.add_class::<AsyncSSEClient>()?;
    m.add_class::<SSEEvent>()?;

    // Add SSEEvent.new as a static method alias
    let sse_event_class = m.getattr("SSEEvent")?;
    sse_event_class.setattr("new", sse_event_class.getattr("new_static")?)?;

    m.add_class::<SSEEventIterator>()?;

    // Middleware
    m.add_class::<MiddlewareManager>()?;
    m.add_class::<MiddlewareConfig>()?;
    m.add_class::<AuthMiddleware>()?;
    m.add_class::<RetryMiddleware>()?;
    m.add_class::<LoggingMiddleware>()?;
    m.add_class::<RateLimitMiddleware>()?;
    m.add_class::<HeadersMiddleware>()?;

    // Performance tools
    m.add_class::<BenchmarkRunner>()?;
    m.add_class::<BenchmarkSuite>()?;
    m.add_class::<BenchmarkConfig>()?;
    m.add_class::<MemoryProfiler>()?;

    // Rate limiting (Phase 5)
    m.add_class::<RateLimitConfig>()?;
    m.add_class::<RateLimitAlgorithm>()?;

    // Performance and benchmarking
    m.add_class::<performance::benchmarks::BenchmarkResult>()?;
    m.add_class::<performance::benchmarks::BenchmarkRunner>()?;
    m.add_class::<performance::benchmarks::BenchmarkSuite>()?;
    m.add_class::<BenchmarkConfig>()?;

    // Performance and Caching
    m.add_class::<performance::benchmarks::BenchmarkResult>()?;
    m.add_class::<performance::benchmarks::BenchmarkRunner>()?;
    m.add_class::<performance::benchmarks::BenchmarkSuite>()?;
    m.add_class::<performance::benchmarks::Benchmark>()?;
    m.add_class::<performance::caching::Cache>()?;
    m.add_class::<performance::caching::CacheStats>()?;
    m.add_class::<performance::caching::ThreadSafeCache>()?;
    m.add_class::<performance::connection_pool::ConnectionPoolImpl>()?;
    m.add_class::<performance::connection_pool::PoolStats>()?;
    m.add_class::<performance::connection_pool::ThreadSafeConnectionPool>()?;

    // Utility functions
    m.add_function(wrap_pyfunction!(parse_sse_line, m)?)?;
    m.add_function(wrap_pyfunction!(build_sse_event, m)?)?;

    // Tracing functions
    m.add_function(wrap_pyfunction!(init_tracing, m)?)?;
    m.add_function(wrap_pyfunction!(get_tracing_info, m)?)?;

    // Add version
    m.add("__version__", "0.1.0")?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_module_creation() -> PyResult<()> {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let module = PyModule::new(py, "_ultrafast_client").map_err(|e| {
                pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to create module: {}", e))
            })?;
            assert!(_ultrafast_client(py, &module).is_ok());
            Ok(())
        })
    }
}
