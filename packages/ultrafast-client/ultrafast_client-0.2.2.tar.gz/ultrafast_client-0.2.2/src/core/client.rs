//! Core client functionality and configurations

use crate::config::*;
use crate::core::error::UltraFastError;
use crate::core::response::ClientResponse;
use reqwest::Method;
use std::collections::HashMap;
use std::time::Duration;

/// Base trait for HTTP client functionality
#[allow(dead_code)]
pub trait HttpClientCore {
    /// Execute an HTTP request
    fn execute_request(
        &mut self,
        method: Method,
        url: &str,
        params: Option<HashMap<String, String>>,
        body: Option<Vec<u8>>,
        headers: Option<HashMap<String, String>>,
    ) -> Result<ClientResponse, UltraFastError>;

    /// Get client configuration
    fn get_config(&self) -> &ClientConfig;

    /// Set base URL for the client
    fn set_base_url(&mut self, base_url: Option<String>);

    /// Add a header to all requests
    fn set_header(&mut self, key: String, value: String);

    /// Remove a header from all requests
    fn remove_header(&mut self, key: &str) -> Option<String>;

    /// Get all headers
    fn get_headers(&self) -> HashMap<String, String>;
}

/// Async version of the base client trait
#[allow(dead_code)]
pub trait AsyncHttpClientCore {
    /// Execute an async HTTP request
    async fn execute_request(
        &self,
        method: Method,
        url: &str,
        params: Option<HashMap<String, String>>,
        body: Option<Vec<u8>>,
        headers: Option<HashMap<String, String>>,
    ) -> Result<ClientResponse, UltraFastError>;

    /// Get client configuration
    fn get_config(&self) -> &ClientConfig;

    /// Set base URL for the client
    fn set_base_url(&mut self, base_url: Option<String>);

    /// Add a header to all requests
    fn set_header(&mut self, key: String, value: String);

    /// Remove a header from all requests
    fn remove_header(&mut self, key: &str) -> Option<String>;

    /// Get all headers
    fn get_headers(&self) -> HashMap<String, String>;
}

/// Comprehensive client configuration
#[allow(dead_code)]
#[derive(Debug, Clone)]
pub struct ClientConfig {
    pub base_url: Option<String>,
    pub timeout: Duration,
    pub auth_config: Option<AuthConfig>,
    pub retry_config: Option<RetryConfig>,
    pub timeout_config: TimeoutConfig,
    pub pool_config: PoolConfig,
    pub ssl_config: SSLConfig,
    pub proxy_config: Option<ProxyConfig>,
    pub compression_config: CompressionConfig,
    pub protocol_config: ProtocolConfig,
    pub rate_limit_config: Option<RateLimitConfig>,
}

impl Default for ClientConfig {
    fn default() -> Self {
        Self {
            base_url: None,
            timeout: Duration::from_secs(30),
            auth_config: None,
            retry_config: None,
            timeout_config: TimeoutConfig::default(),
            pool_config: PoolConfig::new(100, 10, 5, 90.0, 30.0, 30.0),
            ssl_config: SSLConfig::new(true, None, None, None, None, None, None, None),
            proxy_config: None,
            compression_config: CompressionConfig::new(false, true, None, None, 1024),
            protocol_config: ProtocolConfig::default(),
            rate_limit_config: None,
        }
    }
}

#[allow(dead_code)]
impl ClientConfig {
    /// Create a new client configuration with default values
    pub fn new() -> Self {
        Self::default()
    }

    /// Set base URL
    pub fn with_base_url(mut self, base_url: impl Into<String>) -> Self {
        self.base_url = Some(base_url.into());
        self
    }

    /// Set timeout
    pub fn with_timeout(mut self, timeout: Duration) -> Self {
        self.timeout = timeout;
        self
    }

    /// Set authentication configuration
    pub fn with_auth(mut self, auth_config: AuthConfig) -> Self {
        self.auth_config = Some(auth_config);
        self
    }

    /// Set retry configuration
    pub fn with_retry(mut self, retry_config: RetryConfig) -> Self {
        self.retry_config = Some(retry_config);
        self
    }

    /// Set SSL configuration
    pub fn with_ssl(mut self, ssl_config: SSLConfig) -> Self {
        self.ssl_config = ssl_config;
        self
    }

    /// Set proxy configuration
    pub fn with_proxy(mut self, proxy_config: ProxyConfig) -> Self {
        self.proxy_config = Some(proxy_config);
        self
    }

    /// Set compression configuration
    pub fn with_compression(mut self, compression_config: CompressionConfig) -> Self {
        self.compression_config = compression_config;
        self
    }

    /// Set protocol configuration
    pub fn with_protocol(mut self, protocol_config: ProtocolConfig) -> Self {
        self.protocol_config = protocol_config;
        self
    }

    /// Set rate limiting configuration
    pub fn with_rate_limit(mut self, rate_limit_config: RateLimitConfig) -> Self {
        self.rate_limit_config = Some(rate_limit_config);
        self
    }

    /// Validate the configuration
    pub fn validate(&self) -> Result<(), UltraFastError> {
        // Validate timeout settings
        if self.timeout.as_secs_f64() <= 0.0 {
            return Err(UltraFastError::ConfigurationError(
                "Timeout must be greater than 0".to_string(),
            ));
        }

        // Validate protocol configuration
        self.protocol_config
            .validate()
            .map_err(|e| UltraFastError::ConfigurationError(e.to_string()))?;

        // Validate rate limit configuration if present
        if let Some(rate_limit_config) = &self.rate_limit_config {
            if rate_limit_config.enabled && rate_limit_config.requests_per_second <= 0.0 {
                return Err(UltraFastError::ConfigurationError(
                    "Rate limit requests per second must be greater than 0".to_string(),
                ));
            }
        }

        Ok(())
    }
}

/// Shared utilities for client implementations
pub mod utils {
    use super::*;
    use std::collections::HashMap;
    use url::Url;

    /// Build the final URL with base URL and query parameters
    #[allow(dead_code)]
    pub fn build_url(
        base_url: Option<&str>,
        url: &str,
        params: Option<&HashMap<String, String>>,
    ) -> Result<String, UltraFastError> {
        let final_url = if let Some(base) = base_url {
            if url.starts_with("http://") || url.starts_with("https://") {
                url.to_string()
            } else {
                format!(
                    "{}/{}",
                    base.trim_end_matches('/'),
                    url.trim_start_matches('/')
                )
            }
        } else {
            url.to_string()
        };

        if let Some(params) = params {
            if !params.is_empty() {
                let mut url = Url::parse(&final_url)
                    .map_err(|e| UltraFastError::InvalidUrl(e.to_string()))?;

                {
                    let mut query_pairs = url.query_pairs_mut();
                    for (key, value) in params {
                        query_pairs.append_pair(key, value);
                    }
                }

                Ok(url.to_string())
            } else {
                Ok(final_url)
            }
        } else {
            Ok(final_url)
        }
    }

    /// Merge headers from multiple sources
    #[allow(dead_code)]
    pub fn merge_headers(
        base_headers: Option<&HashMap<String, String>>,
        request_headers: Option<&HashMap<String, String>>,
    ) -> HashMap<String, String> {
        let mut merged = HashMap::new();

        if let Some(base) = base_headers {
            merged.extend(base.clone());
        }

        if let Some(request) = request_headers {
            merged.extend(request.clone());
        }

        merged
    }

    /// Prepare request body from various input formats
    #[allow(dead_code)]
    pub fn prepare_body(
        json: Option<&serde_json::Value>,
        data: Option<&HashMap<String, String>>,
        files: Option<&HashMap<String, Vec<u8>>>,
    ) -> Result<(Option<Vec<u8>>, Option<String>), UltraFastError> {
        if let Some(json_data) = json {
            let body = serde_json::to_vec(json_data)
                .map_err(|e| UltraFastError::SerializationError(e.to_string()))?;
            Ok((Some(body), Some("application/json".to_string())))
        } else if let Some(form_data) = data {
            if files.is_some() {
                // Multipart form data
                let boundary = format!("----formdata-ultrafast-{}", uuid::Uuid::new_v4());
                let mut body = Vec::new();

                // Add form fields
                for (key, value) in form_data {
                    body.extend_from_slice(format!("--{}\r\n", boundary).as_bytes());
                    body.extend_from_slice(
                        format!("Content-Disposition: form-data; name=\"{}\"\r\n\r\n", key)
                            .as_bytes(),
                    );
                    body.extend_from_slice(value.as_bytes());
                    body.extend_from_slice(b"\r\n");
                }

                // Add files if present
                if let Some(files) = files {
                    for (name, data) in files {
                        body.extend_from_slice(format!("--{}\r\n", boundary).as_bytes());
                        body.extend_from_slice(
                            format!(
                                "Content-Disposition: form-data; name=\"{}\"; filename=\"{}\"\r\n",
                                name, name
                            )
                            .as_bytes(),
                        );
                        body.extend_from_slice(b"Content-Type: application/octet-stream\r\n\r\n");
                        body.extend_from_slice(data);
                        body.extend_from_slice(b"\r\n");
                    }
                }

                body.extend_from_slice(format!("--{}--\r\n", boundary).as_bytes());

                Ok((
                    Some(body),
                    Some(format!("multipart/form-data; boundary={}", boundary)),
                ))
            } else {
                // URL-encoded form data
                let encoded = form_data
                    .iter()
                    .map(|(k, v)| format!("{}={}", urlencoding::encode(k), urlencoding::encode(v)))
                    .collect::<Vec<_>>()
                    .join("&");
                Ok((
                    Some(encoded.into_bytes()),
                    Some("application/x-www-form-urlencoded".to_string()),
                ))
            }
        } else if let Some(files) = files {
            // Files only
            let boundary = format!("----formdata-ultrafast-{}", uuid::Uuid::new_v4());
            let mut body = Vec::new();

            for (name, data) in files {
                body.extend_from_slice(format!("--{}\r\n", boundary).as_bytes());
                body.extend_from_slice(
                    format!(
                        "Content-Disposition: form-data; name=\"{}\"; filename=\"{}\"\r\n",
                        name, name
                    )
                    .as_bytes(),
                );
                body.extend_from_slice(b"Content-Type: application/octet-stream\r\n\r\n");
                body.extend_from_slice(data);
                body.extend_from_slice(b"\r\n");
            }

            body.extend_from_slice(format!("--{}--\r\n", boundary).as_bytes());

            Ok((
                Some(body),
                Some(format!("multipart/form-data; boundary={}", boundary)),
            ))
        } else {
            Ok((None, None))
        }
    }
}
