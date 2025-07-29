// Client configuration module
use crate::core::error::UltraFastError;
use pyo3::prelude::*;

/// Retry policy configuration
#[pyclass]
#[derive(Clone, Debug)]
pub struct RetryConfig {
    #[pyo3(get, set)]
    pub max_retries: u32,
    #[pyo3(get, set)]
    pub initial_delay: f64, // seconds
    #[pyo3(get, set)]
    pub max_delay: f64, // seconds
    #[pyo3(get, set)]
    pub exponential_base: f64,
    #[pyo3(get, set)]
    pub retry_on_status_codes: Vec<u16>,
    #[pyo3(get, set)]
    pub retry_on_connection_errors: bool,
    #[pyo3(get, set)]
    pub jitter: bool,
    #[pyo3(get, set)]
    pub backoff_factor: f64,
    #[pyo3(get, set)]
    pub retry_on_timeout: bool,
}

#[pymethods]
impl RetryConfig {
    #[new]
    #[pyo3(signature = (max_retries=3, initial_delay=1.0, max_delay=30.0, backoff_factor=1.0, retry_on_timeout=true, retry_on_connection_error=true, retry_on_status_codes=None))]
    pub fn new(
        max_retries: u32,
        initial_delay: f64,
        max_delay: f64,
        backoff_factor: f64,
        retry_on_timeout: bool,
        retry_on_connection_error: bool,
        retry_on_status_codes: Option<Vec<u16>>,
    ) -> Self {
        RetryConfig {
            max_retries,
            initial_delay,
            max_delay,
            exponential_base: 2.0, // Default exponential base
            retry_on_status_codes: retry_on_status_codes.unwrap_or_default(),
            retry_on_connection_errors: retry_on_connection_error,
            jitter: true, // Default to enabled
            backoff_factor,
            retry_on_timeout,
        }
    }

    /// Factory method for high-throughput scenarios with minimal delays
    #[staticmethod]
    pub fn for_high_throughput() -> Self {
        RetryConfig {
            max_retries: 2,
            initial_delay: 0.1,
            max_delay: 5.0,
            exponential_base: 1.5,
            retry_on_status_codes: vec![429, 503, 504], // Rate limiting and server errors
            retry_on_connection_errors: true,
            jitter: true,
            backoff_factor: 1.0,
            retry_on_timeout: true,
        }
    }

    /// Factory method for critical operations requiring robust retry logic
    #[staticmethod]
    pub fn for_critical_operations() -> Self {
        RetryConfig {
            max_retries: 5,
            initial_delay: 1.0,
            max_delay: 120.0,
            exponential_base: 2.5,
            retry_on_status_codes: vec![408, 429, 500, 502, 503, 504, 522, 524],
            retry_on_connection_errors: true,
            jitter: true,
            backoff_factor: 1.0,
            retry_on_timeout: true,
        }
    }

    /// Factory method for development/testing with fast retries
    #[staticmethod]
    pub fn for_development() -> Self {
        RetryConfig {
            max_retries: 1,
            initial_delay: 0.05,
            max_delay: 2.0,
            exponential_base: 1.5,
            retry_on_status_codes: vec![429, 500, 502, 503, 504],
            retry_on_connection_errors: true,
            jitter: false,
            backoff_factor: 1.0,
            retry_on_timeout: true,
        }
    }

    /// Calculate delay for a given attempt with jitter and exponential backoff
    pub fn calculate_delay(&self, attempt: u32) -> f64 {
        let base_delay = self.initial_delay * self.exponential_base.powi(attempt as i32);
        let delay = base_delay.min(self.max_delay);

        if self.jitter {
            // Add jitter: ±25% of the calculated delay
            let jitter_range = delay * 0.25;
            let jitter = (rand::random::<f64>() - 0.5) * 2.0 * jitter_range;
            (delay + jitter).max(0.0)
        } else {
            delay
        }
    }

    /// Calculate delay with adaptive backoff based on consecutive failures
    pub fn calculate_delay_with_backoff(&self, attempt: u32, consecutive_failures: u32) -> f64 {
        let mut base_delay = self.calculate_delay(attempt);

        // Increase delay based on consecutive failures
        if consecutive_failures > 0 {
            let backoff_multiplier = 1.0 + (consecutive_failures as f64 * self.backoff_factor);
            base_delay *= backoff_multiplier;
        }

        base_delay.min(self.max_delay)
    }

    /// Check if we should retry based on status code
    pub fn should_retry_status(&self, status_code: u16) -> bool {
        self.retry_on_status_codes.contains(&status_code)
    }

    /// Check if we should retry with circuit breaker pattern
    pub fn should_retry_with_circuit_breaker(&self, status_code: u16, failure_rate: f64) -> bool {
        // If failure rate is too high, don't retry to prevent cascade failures
        if failure_rate > 0.8 {
            return false;
        }
        self.should_retry_status(status_code)
    }

    /// Get adaptive retry config based on current performance metrics
    pub fn get_adaptive_config(&self, avg_response_time: f64, error_rate: f64) -> RetryConfig {
        let mut config = self.clone();

        // Adjust retry behavior based on performance
        if avg_response_time > 5.0 || error_rate > 0.1 {
            // Slow responses or high error rate: reduce retries
            config.max_retries = (config.max_retries / 2).max(1);
            config.initial_delay *= 1.5;
        } else if avg_response_time < 1.0 && error_rate < 0.01 {
            // Fast responses and low error rate: allow more retries
            config.max_retries = (config.max_retries * 3 / 2).min(10);
            config.initial_delay *= 0.8;
        }

        config
    }
}

/// Connection pool configuration
#[pyclass]
#[derive(Clone, Debug)]
pub struct PoolConfig {
    #[pyo3(get, set)]
    pub max_idle_connections: usize,
    #[pyo3(get, set)]
    pub max_idle_per_host: usize,
    #[pyo3(get, set)]
    pub max_idle_per_host_per_proxy: usize,
    #[pyo3(get, set)]
    pub idle_timeout: f64, // seconds
    #[pyo3(get, set)]
    pub pool_timeout: f64, // seconds
    #[pyo3(get, set)]
    pub keep_alive_timeout: f64, // seconds
}

#[pymethods]
impl PoolConfig {
    #[new]
    #[pyo3(signature = (max_idle_connections=100, max_idle_per_host=10, max_idle_per_host_per_proxy=5, idle_timeout=90.0, pool_timeout=30.0, keep_alive_timeout=30.0))]
    pub fn new(
        max_idle_connections: usize,
        max_idle_per_host: usize,
        max_idle_per_host_per_proxy: usize,
        idle_timeout: f64,
        pool_timeout: f64,
        keep_alive_timeout: f64,
    ) -> Self {
        PoolConfig {
            max_idle_connections,
            max_idle_per_host,
            max_idle_per_host_per_proxy,
            idle_timeout,
            pool_timeout,
            keep_alive_timeout,
        }
    }
}

/// Timeout configuration
#[pyclass]
#[derive(Clone, Debug)]
pub struct TimeoutConfig {
    #[pyo3(get, set)]
    pub connect_timeout: Option<f64>, // seconds
    #[pyo3(get, set)]
    pub read_timeout: Option<f64>, // seconds
    #[pyo3(get, set)]
    pub write_timeout: Option<f64>, // seconds
    #[pyo3(get, set)]
    pub pool_timeout: Option<f64>, // seconds
    #[pyo3(get, set)]
    pub total_timeout: Option<f64>, // seconds - total request timeout
}

#[pymethods]
impl TimeoutConfig {
    #[new]
    #[pyo3(signature = (connect_timeout=None, read_timeout=None, write_timeout=None, pool_timeout=None, total_timeout=None))]
    pub fn new(
        connect_timeout: Option<f64>,
        read_timeout: Option<f64>,
        write_timeout: Option<f64>,
        pool_timeout: Option<f64>,
        total_timeout: Option<f64>,
    ) -> Self {
        TimeoutConfig {
            connect_timeout,
            read_timeout,
            write_timeout,
            pool_timeout,
            total_timeout,
        }
    }

    #[staticmethod]
    pub fn default() -> Self {
        TimeoutConfig {
            connect_timeout: Some(10.0),
            read_timeout: Some(30.0),
            write_timeout: Some(30.0),
            pool_timeout: Some(10.0),
            total_timeout: Some(60.0),
        }
    }
}

/// SSL/TLS configuration
#[pyclass]
#[derive(Clone, Debug)]
pub struct SSLConfig {
    #[pyo3(get, set)]
    pub verify: bool,
    #[pyo3(get, set)]
    pub cert_file: Option<String>,
    #[pyo3(get, set)]
    pub key_file: Option<String>,
    #[pyo3(get, set)]
    pub ca_bundle: Option<String>,
    #[pyo3(get, set)]
    pub min_tls_version: Option<String>,
}

#[pymethods]
impl SSLConfig {
    #[new]
    #[pyo3(signature = (verify=true, cert_file=None, key_file=None, ca_bundle=None, ca_bundle_path=None, cert_path=None, key_path=None, min_tls_version=None))]
    pub fn new(
        verify: bool,
        cert_file: Option<String>,
        key_file: Option<String>,
        ca_bundle: Option<String>,
        ca_bundle_path: Option<String>,
        cert_path: Option<String>,
        key_path: Option<String>,
        min_tls_version: Option<String>,
    ) -> Self {
        SSLConfig {
            verify,
            cert_file: cert_file.or(cert_path),
            key_file: key_file.or(key_path),
            ca_bundle: ca_bundle.or(ca_bundle_path),
            min_tls_version,
        }
    }

    /// Get certificate path (alias for cert_file)
    #[getter]
    pub fn cert_path(&self) -> Option<String> {
        self.cert_file.clone()
    }

    /// Set certificate path
    #[setter]
    pub fn set_cert_path(&mut self, path: Option<String>) {
        self.cert_file = path;
    }

    /// Get key path (alias for key_file)
    #[getter]
    pub fn key_path(&self) -> Option<String> {
        self.key_file.clone()
    }

    /// Set key path
    #[setter]
    pub fn set_key_path(&mut self, path: Option<String>) {
        self.key_file = path;
    }

    /// Get CA bundle path (alias for ca_bundle)
    #[getter]
    pub fn ca_bundle_path(&self) -> Option<String> {
        self.ca_bundle.clone()
    }

    /// Set CA bundle path
    #[setter]
    pub fn set_ca_bundle_path(&mut self, path: Option<String>) {
        self.ca_bundle = path;
    }
}

/// Proxy configuration
#[pyclass]
#[derive(Clone, Debug)]
pub struct ProxyConfig {
    #[pyo3(get)]
    pub url: String,
    #[pyo3(get)]
    pub username: Option<String>,
    #[pyo3(get)]
    pub password: Option<String>,
    #[pyo3(get)]
    pub no_proxy: Option<Vec<String>>, // Domains to bypass proxy
}

#[pymethods]
impl ProxyConfig {
    #[new]
    pub fn new(
        url: String,
        username: Option<String>,
        password: Option<String>,
        no_proxy: Option<Vec<String>>,
    ) -> Self {
        ProxyConfig {
            url,
            username,
            password,
            no_proxy,
        }
    }

    #[staticmethod]
    pub fn http(url: &str, username: Option<String>, password: Option<String>) -> Self {
        ProxyConfig {
            url: format!("http://{}", url),
            username,
            password,
            no_proxy: None,
        }
    }

    #[staticmethod]
    pub fn https(url: &str, username: Option<String>, password: Option<String>) -> Self {
        ProxyConfig {
            url: format!("https://{}", url),
            username,
            password,
            no_proxy: None,
        }
    }

    #[staticmethod]
    pub fn socks5(url: &str, username: Option<String>, password: Option<String>) -> Self {
        ProxyConfig {
            url: format!("socks5://{}", url),
            username,
            password,
            no_proxy: None,
        }
    }

    pub fn set_no_proxy(&mut self, domains: Vec<String>) {
        self.no_proxy = Some(domains);
    }
}

/// Compression configuration
#[pyclass]
#[derive(Clone, Debug)]
pub struct CompressionConfig {
    #[pyo3(get)]
    pub enable_request_compression: bool,
    #[pyo3(get)]
    pub enable_response_compression: bool,
    #[pyo3(get)]
    pub compression_algorithms: Vec<String>, // gzip, deflate, brotli
    #[pyo3(get)]
    pub compression_level: Option<u32>, // 1-9 for gzip/deflate, 1-11 for brotli
    #[pyo3(get)]
    pub min_compression_size: usize, // Minimum size to compress
}

#[pymethods]
impl CompressionConfig {
    #[new]
    #[pyo3(signature = (enable_request_compression=false, enable_response_compression=true, compression_algorithms=None, compression_level=None, min_compression_size=1024))]
    pub fn new(
        enable_request_compression: bool,
        enable_response_compression: bool,
        compression_algorithms: Option<Vec<String>>,
        compression_level: Option<u32>,
        min_compression_size: usize,
    ) -> Self {
        CompressionConfig {
            enable_request_compression,
            enable_response_compression,
            compression_algorithms: compression_algorithms
                .unwrap_or_else(|| vec!["gzip".to_string(), "deflate".to_string()]),
            compression_level,
            min_compression_size,
        }
    }

    /// Create gzip-only compression config
    #[staticmethod]
    pub fn gzip_only() -> Self {
        CompressionConfig {
            enable_request_compression: false,
            enable_response_compression: true,
            compression_algorithms: vec!["gzip".to_string()],
            compression_level: Some(6),
            min_compression_size: 1024,
        }
    }

    /// Create compression config with all algorithms
    #[staticmethod]
    pub fn all_algorithms() -> Self {
        CompressionConfig {
            enable_request_compression: false,
            enable_response_compression: true,
            compression_algorithms: vec![
                "brotli".to_string(),
                "gzip".to_string(),
                "deflate".to_string(),
            ],
            compression_level: Some(6),
            min_compression_size: 1024,
        }
    }

    /// Create disabled compression config
    #[staticmethod]
    pub fn disabled() -> Self {
        CompressionConfig {
            enable_request_compression: false,
            enable_response_compression: false,
            compression_algorithms: vec![],
            compression_level: None,
            min_compression_size: 0,
        }
    }

    /// Check if request should be compressed
    pub fn should_compress_request(&self, content_length: usize, content_type: &str) -> bool {
        self.enable_request_compression
            && content_length >= self.min_compression_size
            && self.is_compressible_content_type(content_type)
    }

    /// Check if content type is compressible
    pub fn is_compressible_content_type(&self, content_type: &str) -> bool {
        let compressible_types = [
            "text/",
            "application/json",
            "application/xml",
            "application/javascript",
            "application/x-www-form-urlencoded",
            "application/graphql",
            "application/ld+json",
        ];

        compressible_types
            .iter()
            .any(|&compressible| content_type.starts_with(compressible))
    }

    /// Get Accept-Encoding header value
    pub fn get_accept_encoding_header(&self) -> String {
        if self.enable_response_compression {
            // Prioritize brotli if available
            let mut algorithms = self.compression_algorithms.clone();
            algorithms.sort_by(|a, b| match (a.as_str(), b.as_str()) {
                ("brotli", _) => std::cmp::Ordering::Less,
                (_, "brotli") => std::cmp::Ordering::Greater,
                ("gzip", "deflate") => std::cmp::Ordering::Less,
                ("deflate", "gzip") => std::cmp::Ordering::Greater,
                _ => std::cmp::Ordering::Equal,
            });
            algorithms.join(", ")
        } else {
            "identity".to_string()
        }
    }

    /// Check if algorithm is supported
    pub fn supports_algorithm(&self, algorithm: &str) -> bool {
        self.compression_algorithms.contains(&algorithm.to_string())
    }

    /// Compress request body using specified algorithm
    pub fn compress_request_body(
        &self,
        body: &[u8],
        algorithm: &str,
    ) -> Result<Vec<u8>, UltraFastError> {
        if !self.enable_request_compression {
            return Err(UltraFastError::ConfigurationError(
                "Request compression is disabled".to_string(),
            ));
        }

        match algorithm {
            "gzip" => {
                use flate2::{write::GzEncoder, Compression};
                use std::io::Write;

                let mut encoder = GzEncoder::new(
                    Vec::new(),
                    Compression::new(self.compression_level.unwrap_or(6)),
                );
                encoder
                    .write_all(body)
                    .map_err(|e| UltraFastError::SerializationError(e.to_string()))?;
                encoder
                    .finish()
                    .map_err(|e| UltraFastError::SerializationError(e.to_string()))
            }
            "deflate" => {
                use flate2::{write::DeflateEncoder, Compression};
                use std::io::Write;

                let mut encoder = DeflateEncoder::new(
                    Vec::new(),
                    Compression::new(self.compression_level.unwrap_or(6)),
                );
                encoder
                    .write_all(body)
                    .map_err(|e| UltraFastError::SerializationError(e.to_string()))?;
                encoder
                    .finish()
                    .map_err(|e| UltraFastError::SerializationError(e.to_string()))
            }
            "brotli" => {
                // Simplified brotli compression - just return original for now
                Ok(body.to_vec())
            }
            _ => Err(UltraFastError::ConfigurationError(format!(
                "Unsupported compression algorithm: {}",
                algorithm
            ))),
        }
    }
}
