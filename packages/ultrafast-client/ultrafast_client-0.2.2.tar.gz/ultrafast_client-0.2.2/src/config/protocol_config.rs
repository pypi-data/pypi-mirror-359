// Protocol configuration module
use crate::core::error::UltraFastError;
use pyo3::prelude::*;

/// HTTP version enumeration
#[pyclass]
#[derive(Clone, Debug, PartialEq)]
pub enum HttpVersion {
    /// HTTP/1.1
    #[pyo3(name = "Http1")]
    Http1,
    /// HTTP/2
    #[pyo3(name = "Http2")]
    Http2,
    /// Automatic version selection
    #[pyo3(name = "Auto")]
    Auto,
}

#[pymethods]
impl HttpVersion {
    /// HTTP/1.1 constant
    #[classattr]
    #[allow(non_snake_case)]
    fn HTTP1() -> HttpVersion {
        HttpVersion::Http1
    }

    /// HTTP/2 constant
    #[classattr]
    #[allow(non_snake_case)]
    fn HTTP2() -> HttpVersion {
        HttpVersion::Http2
    }

    /// Automatic version selection constant
    #[classattr]
    #[allow(non_snake_case)]
    fn AUTO() -> HttpVersion {
        HttpVersion::Auto
    }

    /// Convert to string representation
    fn __str__(&self) -> String {
        match self {
            HttpVersion::Http1 => "HTTP/1.1".to_string(),
            HttpVersion::Http2 => "HTTP/2".to_string(),
            HttpVersion::Auto => "Auto".to_string(),
        }
    }

    /// Convert to string representation
    fn __repr__(&self) -> String {
        format!("HttpVersion.{}", self.__str__())
    }

    /// Equality comparison
    fn __eq__(&self, other: Bound<PyAny>) -> bool {
        if let Ok(other_version) = other.extract::<HttpVersion>() {
            std::mem::discriminant(self) == std::mem::discriminant(&other_version)
        } else {
            false
        }
    }

    /// Hash function
    fn __hash__(&self) -> u64 {
        match self {
            HttpVersion::Http1 => 1,
            HttpVersion::Http2 => 2,
            HttpVersion::Auto => 3,
        }
    }
}

/// HTTP/2 specific settings
#[pyclass]
#[derive(Clone, Debug)]
pub struct Http2Settings {
    #[pyo3(get, set)]
    pub max_concurrent_streams: Option<u32>,
    #[pyo3(get, set)]
    pub initial_window_size: Option<u32>,
    #[pyo3(get, set)]
    pub initial_connection_window_size: Option<u32>,
    #[pyo3(get, set)]
    pub max_frame_size: Option<u32>,
    #[pyo3(get, set)]
    pub max_header_list_size: Option<u32>,
    #[pyo3(get, set)]
    pub enable_push: bool,
    #[pyo3(get, set)]
    pub keep_alive_interval: Option<u64>, // seconds
    #[pyo3(get, set)]
    pub keep_alive_timeout: Option<u64>, // seconds
    #[pyo3(get, set)]
    pub adaptive_window: bool, // Enable adaptive flow control
    #[pyo3(get, set)]
    pub max_idle_timeout: Option<u64>, // seconds
    #[pyo3(get, set)]
    pub max_udp_payload_size: Option<u32>, // bytes (for HTTP/3)
    #[pyo3(get, set)]
    pub initial_max_data: Option<u64>, // bytes (for HTTP/3)
}

#[pymethods]
impl Http2Settings {
    #[new]
    #[pyo3(signature = (
        max_concurrent_streams=None,
        initial_window_size=None,
        initial_connection_window_size=None,
        max_frame_size=None,
        max_header_list_size=None,
        enable_push=false,
        keep_alive_interval=None,
        keep_alive_timeout=None,
        adaptive_window=true,
        max_idle_timeout=None,
        max_udp_payload_size=None,
        initial_max_data=None
    ))]
    pub fn new(
        max_concurrent_streams: Option<u32>,
        initial_window_size: Option<u32>,
        initial_connection_window_size: Option<u32>,
        max_frame_size: Option<u32>,
        max_header_list_size: Option<u32>,
        enable_push: bool,
        keep_alive_interval: Option<u64>,
        keep_alive_timeout: Option<u64>,
        adaptive_window: bool,
        max_idle_timeout: Option<u64>,
        max_udp_payload_size: Option<u32>,
        initial_max_data: Option<u64>,
    ) -> Self {
        Http2Settings {
            max_concurrent_streams,
            initial_window_size,
            initial_connection_window_size,
            max_frame_size,
            max_header_list_size,
            enable_push,
            keep_alive_interval,
            keep_alive_timeout,
            adaptive_window,
            max_idle_timeout,
            max_udp_payload_size,
            initial_max_data,
        }
    }

    /// High-performance settings for HTTP/2
    #[staticmethod]
    pub fn high_performance() -> Self {
        Http2Settings {
            max_concurrent_streams: Some(256),
            initial_window_size: Some(1048576), // 1MB
            initial_connection_window_size: Some(1048576),
            max_frame_size: Some(32768),
            max_header_list_size: Some(16384),
            enable_push: false,
            keep_alive_interval: Some(30),
            keep_alive_timeout: Some(60),
            adaptive_window: true,
            max_idle_timeout: None,
            max_udp_payload_size: None,
            initial_max_data: None,
        }
    }

    /// Conservative settings for HTTP/2
    #[staticmethod]
    pub fn conservative() -> Self {
        Http2Settings {
            max_concurrent_streams: Some(16),
            initial_window_size: Some(65536), // 64KB
            initial_connection_window_size: Some(65536),
            max_frame_size: Some(16384),
            max_header_list_size: Some(8192),
            enable_push: false,
            keep_alive_interval: Some(60),
            keep_alive_timeout: Some(120),
            adaptive_window: false,
            max_idle_timeout: None,
            max_udp_payload_size: None,
            initial_max_data: None,
        }
    }

    /// Default settings for HTTP/2
    #[staticmethod]
    pub fn default() -> Self {
        Http2Settings {
            max_concurrent_streams: Some(100),
            initial_window_size: Some(262144), // 256KB
            initial_connection_window_size: Some(262144),
            max_frame_size: Some(16384),
            max_header_list_size: Some(8192),
            enable_push: false,
            keep_alive_interval: Some(45),
            keep_alive_timeout: Some(90),
            adaptive_window: true,
            max_idle_timeout: None,
            max_udp_payload_size: None,
            initial_max_data: None,
        }
    }
}

/// Protocol fallback strategy
#[pyclass]
#[derive(Clone, Debug, PartialEq)]
pub enum ProtocolFallback {
    /// No fallback
    #[pyo3(name = "None")]
    None,
    /// Fallback to HTTP/1.1 if HTTP/2 fails
    #[pyo3(name = "Http2ToHttp1")]
    Http2ToHttp1,
    /// Fallback from HTTP/2 to HTTP/2 to HTTP/1.1 (with retry)
    #[pyo3(name = "Http2ToHttp2ToHttp1")]
    Http2ToHttp2ToHttp1,
}

#[pymethods]
impl ProtocolFallback {
    /// No fallback constant
    #[classattr]
    #[allow(non_snake_case)]
    fn NONE() -> ProtocolFallback {
        ProtocolFallback::None
    }

    /// HTTP/2 to HTTP/1.1 fallback constant
    #[classattr]
    #[allow(non_snake_case)]
    fn HTTP2_TO_HTTP1() -> ProtocolFallback {
        ProtocolFallback::Http2ToHttp1
    }

    /// HTTP/2 to HTTP/2 to HTTP/1.1 fallback constant (with retry)
    #[classattr]
    #[allow(non_snake_case)]
    fn HTTP2_TO_HTTP2_TO_HTTP1() -> ProtocolFallback {
        ProtocolFallback::Http2ToHttp2ToHttp1
    }

    /// Convert to string representation
    fn __str__(&self) -> String {
        match self {
            ProtocolFallback::None => "None".to_string(),
            ProtocolFallback::Http2ToHttp1 => "Http2ToHttp1".to_string(),
            ProtocolFallback::Http2ToHttp2ToHttp1 => "Http2ToHttp2ToHttp1".to_string(),
        }
    }

    /// Convert to string representation
    fn __repr__(&self) -> String {
        format!("ProtocolFallback.{}", self.__str__())
    }

    /// Equality comparison
    fn __eq__(&self, other: Bound<PyAny>) -> bool {
        if let Ok(other_fallback) = other.extract::<ProtocolFallback>() {
            std::mem::discriminant(self) == std::mem::discriminant(&other_fallback)
        } else {
            false
        }
    }

    /// Hash function
    fn __hash__(&self) -> u64 {
        match self {
            ProtocolFallback::None => 1,
            ProtocolFallback::Http2ToHttp1 => 2,
            ProtocolFallback::Http2ToHttp2ToHttp1 => 3,
        }
    }
}

/// Protocol configuration
#[pyclass]
#[derive(Clone, Debug)]
pub struct ProtocolConfig {
    #[pyo3(get, set)]
    pub preferred_version: HttpVersion,
    #[pyo3(get, set)]
    pub enable_http2: bool,
    #[pyo3(get, set)]
    pub fallback_strategy: ProtocolFallback,
    #[pyo3(get, set)]
    pub http2_settings: Http2Settings,
    #[pyo3(get, set)]
    pub protocol_negotiation_timeout: f64, // seconds
    #[pyo3(get, set)]
    pub enable_http2_prior_knowledge: bool,
}

#[pymethods]
impl ProtocolConfig {
    #[new]
    #[pyo3(signature = (
        preferred_version=HttpVersion::Auto,
        enable_http2=true,
        fallback_strategy=ProtocolFallback::Http2ToHttp1,
        http2_settings=None,
        protocol_negotiation_timeout=10.0,
        enable_http2_prior_knowledge=false
    ))]
    pub fn new(
        preferred_version: HttpVersion,
        enable_http2: bool,
        fallback_strategy: ProtocolFallback,
        http2_settings: Option<Http2Settings>,
        protocol_negotiation_timeout: f64,
        enable_http2_prior_knowledge: bool,
    ) -> Self {
        ProtocolConfig {
            preferred_version,
            enable_http2,
            fallback_strategy,
            http2_settings: http2_settings.unwrap_or_else(Http2Settings::default),
            protocol_negotiation_timeout,
            enable_http2_prior_knowledge,
        }
    }

    /// Check if HTTP/2 is enabled
    pub fn is_http2_enabled(&self) -> bool {
        // If HTTP/2 is explicitly disabled, respect that setting
        if !self.enable_http2 {
            return false;
        }

        // Otherwise, check other conditions
        (self.preferred_version == HttpVersion::Http2
            || self.preferred_version == HttpVersion::Auto)
            || matches!(
                self.fallback_strategy,
                ProtocolFallback::Http2ToHttp1 | ProtocolFallback::Http2ToHttp2ToHttp1
            )
    }

    /// Check if HTTP/3 is enabled (always false now)
    pub fn is_http3_enabled(&self) -> bool {
        false
    }

    /// Default protocol configuration
    #[staticmethod]
    pub fn default() -> Self {
        ProtocolConfig {
            preferred_version: HttpVersion::Auto,
            enable_http2: true,
            fallback_strategy: ProtocolFallback::Http2ToHttp1,
            http2_settings: Http2Settings::default(),
            protocol_negotiation_timeout: 10.0,
            enable_http2_prior_knowledge: false,
        }
    }

    /// Validate protocol configuration
    pub fn validate(&self) -> PyResult<()> {
        if self.protocol_negotiation_timeout <= 0.0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Protocol negotiation timeout must be positive",
            ));
        }

        Ok(())
    }
}

/// Rate limiting algorithm options
#[pyclass]
#[derive(Clone, Debug, PartialEq)]
pub enum RateLimitAlgorithm {
    TokenBucket,
    SlidingWindow,
    FixedWindow,
}

#[pymethods]
impl RateLimitAlgorithm {
    #[classattr]
    #[allow(non_snake_case)]
    fn TOKEN_BUCKET() -> RateLimitAlgorithm {
        RateLimitAlgorithm::TokenBucket
    }

    #[classattr]
    #[allow(non_snake_case)]
    fn SLIDING_WINDOW() -> RateLimitAlgorithm {
        RateLimitAlgorithm::SlidingWindow
    }

    #[classattr]
    #[allow(non_snake_case)]
    fn FIXED_WINDOW() -> RateLimitAlgorithm {
        RateLimitAlgorithm::FixedWindow
    }

    #[classattr]
    #[allow(non_snake_case)]
    fn LeakyBucket() -> RateLimitAlgorithm {
        RateLimitAlgorithm::TokenBucket // Map to TokenBucket for now
    }

    /// Convert to string representation
    fn __str__(&self) -> String {
        match self {
            RateLimitAlgorithm::TokenBucket => "TokenBucket".to_string(),
            RateLimitAlgorithm::SlidingWindow => "SlidingWindow".to_string(),
            RateLimitAlgorithm::FixedWindow => "FixedWindow".to_string(),
        }
    }

    /// Convert to string representation
    fn __repr__(&self) -> String {
        format!("RateLimitAlgorithm.{}", self.__str__())
    }

    /// Equality comparison
    fn __eq__(&self, other: Bound<PyAny>) -> bool {
        if let Ok(other_algorithm) = other.extract::<RateLimitAlgorithm>() {
            std::mem::discriminant(self) == std::mem::discriminant(&other_algorithm)
        } else {
            false
        }
    }

    /// Hash function
    fn __hash__(&self) -> u64 {
        match self {
            RateLimitAlgorithm::TokenBucket => 1,
            RateLimitAlgorithm::SlidingWindow => 2,
            RateLimitAlgorithm::FixedWindow => 3,
        }
    }
}

/// Rate limiting configuration
#[pyclass]
#[derive(Clone, Debug)]
pub struct RateLimitConfig {
    #[pyo3(get, set)]
    pub enabled: bool,

    #[pyo3(get, set)]
    pub algorithm: RateLimitAlgorithm,

    #[pyo3(get, set)]
    pub requests_per_second: f64,

    #[pyo3(get, set)]
    pub requests_per_minute: Option<u32>,

    #[pyo3(get, set)]
    pub requests_per_hour: Option<u32>,

    #[pyo3(get, set)]
    pub burst_size: Option<u32>,

    #[pyo3(get, set)]
    pub window_size_seconds: f64,

    #[pyo3(get, set)]
    pub per_host: bool,

    #[pyo3(get, set)]
    pub reset_on_success: bool,

    #[pyo3(get, set)]
    pub queue_requests: bool,

    #[pyo3(get, set)]
    pub max_queue_size: usize,

    #[pyo3(get, set)]
    pub queue_timeout_seconds: f64,
}

#[pymethods]
impl RateLimitConfig {
    #[new]
    #[pyo3(signature = (
        enabled=true,
        algorithm=RateLimitAlgorithm::TokenBucket,
        requests_per_second=10.0,
        requests_per_minute=None,
        requests_per_hour=None,
        burst_size=None,
        window_size_seconds=1.0,
        per_host=true,
        reset_on_success=false,
        queue_requests=false,
        max_queue_size=100,
        queue_timeout_seconds=30.0
    ))]
    pub fn new(
        enabled: bool,
        algorithm: RateLimitAlgorithm,
        requests_per_second: f64,
        requests_per_minute: Option<u32>,
        requests_per_hour: Option<u32>,
        burst_size: Option<u32>,
        window_size_seconds: f64,
        per_host: bool,
        reset_on_success: bool,
        queue_requests: bool,
        max_queue_size: usize,
        queue_timeout_seconds: f64,
    ) -> Self {
        RateLimitConfig {
            enabled,
            algorithm,
            requests_per_second,
            requests_per_minute,
            requests_per_hour,
            burst_size,
            window_size_seconds,
            per_host,
            reset_on_success,
            queue_requests,
            max_queue_size,
            queue_timeout_seconds,
        }
    }

    /// Conservative rate limiting settings
    #[staticmethod]
    pub fn conservative() -> Self {
        RateLimitConfig {
            enabled: true,
            algorithm: RateLimitAlgorithm::TokenBucket,
            requests_per_second: 1.0,
            requests_per_minute: Some(30),
            requests_per_hour: Some(1000),
            burst_size: Some(5),
            window_size_seconds: 1.0,
            per_host: true,
            reset_on_success: true,
            queue_requests: true,
            max_queue_size: 50,
            queue_timeout_seconds: 30.0,
        }
    }

    /// Moderate rate limiting settings
    #[staticmethod]
    pub fn moderate() -> Self {
        RateLimitConfig {
            enabled: true,
            algorithm: RateLimitAlgorithm::TokenBucket,
            requests_per_second: 10.0,
            requests_per_minute: Some(500),
            requests_per_hour: Some(10000),
            burst_size: Some(20),
            window_size_seconds: 1.0,
            per_host: true,
            reset_on_success: false,
            queue_requests: false,
            max_queue_size: 100,
            queue_timeout_seconds: 30.0,
        }
    }

    /// Aggressive rate limiting settings (high throughput)
    #[staticmethod]
    pub fn aggressive() -> Self {
        RateLimitConfig {
            enabled: true,
            algorithm: RateLimitAlgorithm::SlidingWindow,
            requests_per_second: 100.0,
            requests_per_minute: Some(5000),
            requests_per_hour: Some(100000),
            burst_size: Some(200),
            window_size_seconds: 1.0,
            per_host: false,
            reset_on_success: false,
            queue_requests: false,
            max_queue_size: 500,
            queue_timeout_seconds: 10.0,
        }
    }

    /// Disabled rate limiting
    #[staticmethod]
    pub fn disabled() -> Self {
        RateLimitConfig {
            enabled: false,
            algorithm: RateLimitAlgorithm::TokenBucket,
            requests_per_second: 0.0,
            requests_per_minute: None,
            requests_per_hour: None,
            burst_size: None,
            window_size_seconds: 1.0,
            per_host: false,
            reset_on_success: false,
            queue_requests: false,
            max_queue_size: 0,
            queue_timeout_seconds: 0.0,
        }
    }

    /// Validate rate limiting configuration
    pub fn validate(&self) -> Result<(), UltraFastError> {
        if self.enabled {
            if self.requests_per_second <= 0.0 {
                return Err(UltraFastError::ConfigurationError(
                    "Requests per second must be positive when rate limiting is enabled"
                        .to_string(),
                ));
            }

            if self.window_size_seconds <= 0.0 {
                return Err(UltraFastError::ConfigurationError(
                    "Window size must be positive".to_string(),
                ));
            }

            if self.queue_requests && self.queue_timeout_seconds <= 0.0 {
                return Err(UltraFastError::ConfigurationError(
                    "Queue timeout must be positive when queueing is enabled".to_string(),
                ));
            }
        }

        Ok(())
    }
}
