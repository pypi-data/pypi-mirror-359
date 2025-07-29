// URL utilities module
use pyo3::prelude::*;
use std::collections::HashMap;
use urlencoding;

/// URL utilities
#[pyclass]
#[derive(Debug)]
pub struct UrlUtils;

#[pymethods]
impl UrlUtils {
    /// Encode URL component
    #[staticmethod]
    pub fn encode_component(component: &str) -> String {
        urlencoding::encode(component).to_string()
    }

    /// Decode URL component
    #[staticmethod]
    pub fn decode_component(component: &str) -> PyResult<String> {
        urlencoding::decode(component)
            .map(|s| s.into_owned())
            .map_err(|e| {
                pyo3::exceptions::PyValueError::new_err(format!(
                    "Failed to decode URL component: {}",
                    e
                ))
            })
    }

    /// Join URL path components
    #[staticmethod]
    pub fn join_path(base: &str, path: &str) -> String {
        let base = base.trim_end_matches('/');
        let path = path.trim_start_matches('/');
        format!("{}/{}", base, path)
    }

    /// Parse query string into parameters
    #[staticmethod]
    pub fn parse_query_string(query: &str) -> HashMap<String, String> {
        let mut params = HashMap::new();

        for pair in query.split('&') {
            if let Some((key, value)) = pair.split_once('=') {
                let key = urlencoding::decode(key).unwrap_or_default().into_owned();
                let value = urlencoding::decode(value).unwrap_or_default().into_owned();
                params.insert(key, value);
            }
        }

        params
    }

    /// Build query string from parameters
    #[staticmethod]
    pub fn build_query_string(params: HashMap<String, String>) -> String {
        let mut query_parts = Vec::new();

        for (key, value) in params {
            let encoded_key = urlencoding::encode(&key);
            let encoded_value = urlencoding::encode(&value);
            query_parts.push(format!("{}={}", encoded_key, encoded_value));
        }

        query_parts.join("&")
    }

    /// Extract domain from URL
    #[staticmethod]
    pub fn extract_domain(url: &str) -> PyResult<String> {
        if let Some(domain_start) = url.find("://") {
            let after_protocol = &url[domain_start + 3..];
            if let Some(domain_end) = after_protocol.find('/') {
                Ok(after_protocol[..domain_end].to_string())
            } else if let Some(domain_end) = after_protocol.find('?') {
                Ok(after_protocol[..domain_end].to_string())
            } else {
                Ok(after_protocol.to_string())
            }
        } else {
            Err(pyo3::exceptions::PyValueError::new_err(
                "Invalid URL format",
            ))
        }
    }

    /// Validate URL format
    #[staticmethod]
    pub fn validate_url(url: &str) -> bool {
        url.starts_with("http://") || url.starts_with("https://")
    }

    /// Normalize URL (remove trailing slash, etc.)
    #[staticmethod]
    pub fn normalize_url(url: &str) -> String {
        let mut normalized = url.to_string();

        // Remove trailing slash unless it's the root
        if normalized.len() > 1 && normalized.ends_with('/') {
            normalized.pop();
        }

        // Ensure protocol is lowercase
        if normalized.starts_with("HTTP://") {
            normalized = normalized.replacen("HTTP://", "http://", 1);
        } else if normalized.starts_with("HTTPS://") {
            normalized = normalized.replacen("HTTPS://", "https://", 1);
        }

        normalized
    }
}
