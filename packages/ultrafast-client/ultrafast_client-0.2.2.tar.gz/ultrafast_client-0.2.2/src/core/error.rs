// Enhanced error handling for the HTTP client
use pyo3::prelude::*;
use std::fmt;
use tracing::{error, warn};

/// Main error type for the UltraFast HTTP client
#[derive(Debug, Clone)]
pub enum UltraFastError {
    /// Network-related errors
    NetworkError(String),
    /// HTTP-related errors (status codes, etc.)
    HttpError(u16, String),
    /// Request timeout
    TimeoutError(String),
    /// Authentication errors
    AuthenticationError(String),
    /// Configuration errors
    ConfigurationError(String),
    /// Serialization/deserialization errors
    SerializationError(String),
    /// Invalid URL
    InvalidUrl(String),
    /// Rate limiting errors
    RateLimitError(String),
    /// Middleware errors
    MiddlewareError(String),
    /// SSL/TLS errors
    SslError(String),
    /// Protocol errors (HTTP/2, HTTP/3)
    ProtocolError(String),
    /// WebSocket errors
    WebSocketError(String),
    /// Server-Sent Events errors
    SseError(String),
    /// Connection pool errors
    ConnectionPoolError(String),
    /// General client errors
    ClientError(String),
    /// Unknown/unexpected errors
    UnknownError(String),
}

impl fmt::Display for UltraFastError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            UltraFastError::NetworkError(msg) => write!(f, "Network error: {}", msg),
            UltraFastError::HttpError(status, msg) => write!(f, "HTTP error {}: {}", status, msg),
            UltraFastError::TimeoutError(msg) => write!(f, "Timeout error: {}", msg),
            UltraFastError::AuthenticationError(msg) => write!(f, "Authentication error: {}", msg),
            UltraFastError::ConfigurationError(msg) => write!(f, "Configuration error: {}", msg),
            UltraFastError::SerializationError(msg) => write!(f, "Serialization error: {}", msg),
            UltraFastError::InvalidUrl(msg) => write!(f, "Invalid URL: {}", msg),
            UltraFastError::RateLimitError(msg) => write!(f, "Rate limit error: {}", msg),
            UltraFastError::MiddlewareError(msg) => write!(f, "Middleware error: {}", msg),
            UltraFastError::SslError(msg) => write!(f, "SSL/TLS error: {}", msg),
            UltraFastError::ProtocolError(msg) => write!(f, "Protocol error: {}", msg),
            UltraFastError::WebSocketError(msg) => write!(f, "WebSocket error: {}", msg),
            UltraFastError::SseError(msg) => write!(f, "SSE error: {}", msg),
            UltraFastError::ConnectionPoolError(msg) => write!(f, "Connection pool error: {}", msg),
            UltraFastError::ClientError(msg) => write!(f, "Client error: {}", msg),
            UltraFastError::UnknownError(msg) => write!(f, "Unknown error: {}", msg),
        }
    }
}

impl std::error::Error for UltraFastError {}

impl From<UltraFastError> for PyErr {
    fn from(err: UltraFastError) -> Self {
        match err {
            UltraFastError::NetworkError(msg) => pyo3::exceptions::PyConnectionError::new_err(msg),
            UltraFastError::HttpError(status, msg) => {
                if status >= 400 && status < 500 {
                    pyo3::exceptions::PyValueError::new_err(format!("HTTP {}: {}", status, msg))
                } else {
                    pyo3::exceptions::PyRuntimeError::new_err(format!("HTTP {}: {}", status, msg))
                }
            }
            UltraFastError::TimeoutError(msg) => pyo3::exceptions::PyTimeoutError::new_err(msg),
            UltraFastError::AuthenticationError(msg) => {
                pyo3::exceptions::PyPermissionError::new_err(msg)
            }
            UltraFastError::ConfigurationError(msg) => pyo3::exceptions::PyValueError::new_err(msg),
            UltraFastError::SerializationError(msg) => pyo3::exceptions::PyValueError::new_err(msg),
            UltraFastError::InvalidUrl(msg) => pyo3::exceptions::PyValueError::new_err(msg),
            UltraFastError::RateLimitError(msg) => pyo3::exceptions::PyRuntimeError::new_err(msg),
            UltraFastError::MiddlewareError(msg) => pyo3::exceptions::PyRuntimeError::new_err(msg),
            UltraFastError::SslError(msg) => pyo3::exceptions::PyConnectionError::new_err(msg),
            UltraFastError::ProtocolError(msg) => pyo3::exceptions::PyRuntimeError::new_err(msg),
            UltraFastError::WebSocketError(msg) => {
                pyo3::exceptions::PyConnectionError::new_err(msg)
            }
            UltraFastError::SseError(msg) => pyo3::exceptions::PyConnectionError::new_err(msg),
            UltraFastError::ConnectionPoolError(msg) => {
                pyo3::exceptions::PyConnectionError::new_err(msg)
            }
            UltraFastError::ClientError(msg) => pyo3::exceptions::PyRuntimeError::new_err(msg),
            UltraFastError::UnknownError(msg) => pyo3::exceptions::PyRuntimeError::new_err(msg),
        }
    }
}

/// Map a reqwest error to UltraFastError
#[allow(dead_code)]
pub fn map_reqwest_error(err: reqwest::Error) -> UltraFastError {
    if err.is_timeout() {
        error!(error = %err, "Request timeout occurred");
        UltraFastError::TimeoutError(format!("Request timeout: {}", err))
    } else if err.is_connect() {
        error!(error = %err, "Connection error occurred");
        UltraFastError::NetworkError(format!("Connection error: {}", err))
    } else if err.is_request() {
        warn!(error = %err, "Request configuration error");
        UltraFastError::ConfigurationError(format!("Request error: {}", err))
    } else {
        error!(error = %err, "Unknown reqwest error occurred");
        UltraFastError::NetworkError(format!("Network error: {}", err))
    }
}

/// Map URL parsing error to UltraFastError
#[allow(dead_code)]
pub fn map_url_error(err: url::ParseError) -> UltraFastError {
    warn!(error = %err, "URL parsing error occurred");
    UltraFastError::ConfigurationError(format!("Invalid URL: {}", err))
}

/// Map JSON error to UltraFastError
#[allow(dead_code)]
pub fn map_json_error(err: serde_json::Error) -> UltraFastError {
    warn!(error = %err, "JSON serialization error occurred");
    UltraFastError::SerializationError(format!("JSON error: {}", err))
}

/// Map join error to UltraFastError
#[allow(dead_code)]
pub fn map_join_error(err: tokio::task::JoinError) -> UltraFastError {
    error!(error = %err, "Async task join error occurred");
    UltraFastError::NetworkError(format!("Task join error: {}", err))
}

/// Convenience type alias for results
#[allow(dead_code)]
pub type UltraFastResult<T> = Result<T, UltraFastError>;

/// Create a Python exception from an UltraFastError
#[allow(dead_code)]
pub fn create_py_exception(err: UltraFastError) -> PyResult<()> {
    Err(PyErr::from(err))
}

/// Enhanced error context for debugging
#[derive(Debug, Clone)]
pub struct ErrorContext {
    pub operation: String,
    pub url: Option<String>,
    pub method: Option<String>,
    pub status_code: Option<u16>,
    pub timestamp: std::time::SystemTime,
}

impl ErrorContext {
    pub fn new(operation: impl Into<String>) -> Self {
        Self {
            operation: operation.into(),
            url: None,
            method: None,
            status_code: None,
            timestamp: std::time::SystemTime::now(),
        }
    }

    pub fn with_url(mut self, url: impl Into<String>) -> Self {
        self.url = Some(url.into());
        self
    }

    pub fn with_method(mut self, method: impl Into<String>) -> Self {
        self.method = Some(method.into());
        self
    }

    pub fn with_status_code(mut self, status_code: u16) -> Self {
        self.status_code = Some(status_code);
        self
    }
}

/// Enhanced error with context
#[derive(Debug, Clone)]
pub struct ContextualError {
    pub error: UltraFastError,
    pub context: ErrorContext,
}

impl ContextualError {
    pub fn new(error: UltraFastError, context: ErrorContext) -> Self {
        Self { error, context }
    }
}

impl fmt::Display for ContextualError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} (operation: {}", self.error, self.context.operation)?;

        if let Some(url) = &self.context.url {
            write!(f, ", url: {}", url)?;
        }

        if let Some(method) = &self.context.method {
            write!(f, ", method: {}", method)?;
        }

        if let Some(status) = self.context.status_code {
            write!(f, ", status: {}", status)?;
        }

        write!(f, ")")
    }
}

impl std::error::Error for ContextualError {}

impl From<ContextualError> for PyErr {
    fn from(err: ContextualError) -> Self {
        PyErr::from(err.error)
    }
}
