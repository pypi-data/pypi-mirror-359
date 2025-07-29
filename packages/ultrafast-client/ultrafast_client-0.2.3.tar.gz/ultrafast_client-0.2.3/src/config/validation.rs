// Configuration validation utilities
use crate::core::error::UltraFastError;
use std::time::Duration;

/// Validation trait for configuration objects
#[allow(dead_code)]
pub trait Validate {
    /// Validate the configuration and return any errors
    fn validate(&self) -> Result<(), UltraFastError>;
}

/// Utility functions for validating configuration values
#[allow(dead_code)]
pub struct ValidationUtils;

#[allow(dead_code)]
impl ValidationUtils {
    /// Validate timeout duration
    pub fn validate_timeout(timeout: Duration) -> Result<(), UltraFastError> {
        if timeout.as_secs_f64() <= 0.0 {
            return Err(UltraFastError::ConfigurationError(
                "Timeout must be greater than 0".to_string(),
            ));
        }
        if timeout.as_secs() > 3600 {
            return Err(UltraFastError::ConfigurationError(
                "Timeout cannot exceed 1 hour".to_string(),
            ));
        }
        Ok(())
    }

    /// Validate port number
    pub fn validate_port(port: u16) -> Result<(), UltraFastError> {
        if port == 0 {
            return Err(UltraFastError::ConfigurationError(
                "Port number cannot be 0".to_string(),
            ));
        }
        Ok(())
    }

    /// Validate URL format
    pub fn validate_url(url: &str) -> Result<(), UltraFastError> {
        if url.is_empty() {
            return Err(UltraFastError::ConfigurationError(
                "URL cannot be empty".to_string(),
            ));
        }

        // Basic URL validation
        if !url.starts_with("http://") && !url.starts_with("https://") {
            return Err(UltraFastError::ConfigurationError(
                "URL must start with http:// or https://".to_string(),
            ));
        }

        Ok(())
    }

    /// Validate connection pool size
    pub fn validate_pool_size(size: usize) -> Result<(), UltraFastError> {
        if size == 0 {
            return Err(UltraFastError::ConfigurationError(
                "Pool size must be greater than 0".to_string(),
            ));
        }
        if size > 10000 {
            return Err(UltraFastError::ConfigurationError(
                "Pool size cannot exceed 10000".to_string(),
            ));
        }
        Ok(())
    }

    /// Validate compression level
    pub fn validate_compression_level(level: u32, algorithm: &str) -> Result<(), UltraFastError> {
        match algorithm {
            "gzip" | "deflate" => {
                if level < 1 || level > 9 {
                    return Err(UltraFastError::ConfigurationError(format!(
                        "Compression level for {} must be between 1 and 9",
                        algorithm
                    )));
                }
            }
            "brotli" => {
                if level < 1 || level > 11 {
                    return Err(UltraFastError::ConfigurationError(
                        "Compression level for brotli must be between 1 and 11".to_string(),
                    ));
                }
            }
            _ => {
                return Err(UltraFastError::ConfigurationError(format!(
                    "Unknown compression algorithm: {}",
                    algorithm
                )));
            }
        }
        Ok(())
    }

    /// Validate HTTP header name
    pub fn validate_header_name(name: &str) -> Result<(), UltraFastError> {
        if name.is_empty() {
            return Err(UltraFastError::ConfigurationError(
                "Header name cannot be empty".to_string(),
            ));
        }

        // Basic header name validation (simplified)
        if name.contains(' ') || name.contains('\t') || name.contains('\n') || name.contains('\r') {
            return Err(UltraFastError::ConfigurationError(
                "Header name cannot contain whitespace characters".to_string(),
            ));
        }

        Ok(())
    }

    /// Validate HTTP header value
    pub fn validate_header_value(value: &str) -> Result<(), UltraFastError> {
        // Basic header value validation (simplified)
        if value.contains('\n') || value.contains('\r') {
            return Err(UltraFastError::ConfigurationError(
                "Header value cannot contain line breaks".to_string(),
            ));
        }

        Ok(())
    }

    /// Validate rate limiting parameters
    pub fn validate_rate_limit(
        requests_per_second: f64,
        burst_size: Option<u32>,
    ) -> Result<(), UltraFastError> {
        if requests_per_second <= 0.0 {
            return Err(UltraFastError::ConfigurationError(
                "Requests per second must be positive".to_string(),
            ));
        }

        if let Some(burst) = burst_size {
            if burst == 0 {
                return Err(UltraFastError::ConfigurationError(
                    "Burst size must be greater than 0".to_string(),
                ));
            }
            if burst as f64 > requests_per_second * 10.0 {
                return Err(UltraFastError::ConfigurationError(
                    "Burst size should not exceed 10x the requests per second".to_string(),
                ));
            }
        }

        Ok(())
    }

    /// Validate retry configuration
    pub fn validate_retry_config(
        max_retries: u32,
        initial_delay: f64,
        max_delay: f64,
    ) -> Result<(), UltraFastError> {
        if max_retries > 100 {
            return Err(UltraFastError::ConfigurationError(
                "Maximum retries cannot exceed 100".to_string(),
            ));
        }

        if initial_delay <= 0.0 {
            return Err(UltraFastError::ConfigurationError(
                "Initial delay must be positive".to_string(),
            ));
        }

        if max_delay <= initial_delay {
            return Err(UltraFastError::ConfigurationError(
                "Maximum delay must be greater than initial delay".to_string(),
            ));
        }

        if max_delay > 3600.0 {
            return Err(UltraFastError::ConfigurationError(
                "Maximum delay cannot exceed 1 hour".to_string(),
            ));
        }

        Ok(())
    }

    /// Validate proxy URL format
    pub fn validate_proxy_url(url: &str) -> Result<(), UltraFastError> {
        if url.is_empty() {
            return Err(UltraFastError::ConfigurationError(
                "Proxy URL cannot be empty".to_string(),
            ));
        }

        let supported_schemes = ["http://", "https://", "socks5://"];
        if !supported_schemes
            .iter()
            .any(|&scheme| url.starts_with(scheme))
        {
            return Err(UltraFastError::ConfigurationError(
                "Proxy URL must start with http://, https://, or socks5://".to_string(),
            ));
        }

        Ok(())
    }

    /// Validate SSL/TLS configuration
    pub fn validate_ssl_config(
        cert_file: Option<&str>,
        key_file: Option<&str>,
    ) -> Result<(), UltraFastError> {
        match (cert_file, key_file) {
            (Some(_), None) => {
                return Err(UltraFastError::ConfigurationError(
                    "Certificate file specified but key file is missing".to_string(),
                ));
            }
            (None, Some(_)) => {
                return Err(UltraFastError::ConfigurationError(
                    "Key file specified but certificate file is missing".to_string(),
                ));
            }
            _ => {}
        }

        Ok(())
    }

    /// Validate TLS version
    pub fn validate_tls_version(version: &str) -> Result<(), UltraFastError> {
        let supported_versions = ["1.0", "1.1", "1.2", "1.3"];
        if !supported_versions.contains(&version) {
            return Err(UltraFastError::ConfigurationError(format!(
                "Unsupported TLS version: {}. Supported versions: {:?}",
                version, supported_versions
            )));
        }

        Ok(())
    }

    /// Validate OAuth2 configuration
    pub fn validate_oauth2_config(
        client_id: &str,
        token_url: &str,
        client_secret: Option<&str>,
    ) -> Result<(), UltraFastError> {
        if client_id.is_empty() {
            return Err(UltraFastError::ConfigurationError(
                "OAuth2 client_id cannot be empty".to_string(),
            ));
        }

        Self::validate_url(token_url)?;

        if let Some(secret) = client_secret {
            if secret.is_empty() {
                return Err(UltraFastError::ConfigurationError(
                    "OAuth2 client_secret cannot be empty when provided".to_string(),
                ));
            }
        }

        Ok(())
    }
}
