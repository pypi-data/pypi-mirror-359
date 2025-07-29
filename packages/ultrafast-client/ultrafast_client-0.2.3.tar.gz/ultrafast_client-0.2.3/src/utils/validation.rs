// General validation utilities module
use pyo3::prelude::*;

/// General validation utilities
#[pyclass]
#[derive(Debug)]
pub struct ValidationUtils;

#[pymethods]
impl ValidationUtils {
    /// Validate email address format (simplified)
    #[staticmethod]
    pub fn validate_email(email: &str) -> bool {
        email.contains('@') && email.contains('.')
    }

    /// Validate IP address (IPv4)
    #[staticmethod]
    pub fn validate_ipv4(ip: &str) -> bool {
        let parts: Vec<&str> = ip.split('.').collect();
        if parts.len() != 4 {
            return false;
        }

        for part in parts {
            if part.parse::<u8>().is_err() {
                return false;
            }
        }
        true
    }

    /// Validate port number
    #[staticmethod]
    pub fn validate_port(port: u32) -> bool {
        port > 0 && port <= 65535
    }

    /// Validate domain name (simplified)
    #[staticmethod]
    pub fn validate_domain(domain: &str) -> bool {
        !domain.is_empty() && domain.contains('.') && domain.len() <= 253
    }

    /// Validate HTTP method
    #[staticmethod]
    pub fn validate_http_method(method: &str) -> bool {
        let method_upper = method.to_uppercase();
        method_upper == "GET"
            || method_upper == "POST"
            || method_upper == "PUT"
            || method_upper == "DELETE"
            || method_upper == "HEAD"
            || method_upper == "OPTIONS"
            || method_upper == "PATCH"
    }

    /// Validate JSON string
    #[staticmethod]
    pub fn validate_json(json_str: &str) -> bool {
        serde_json::from_str::<serde_json::Value>(json_str).is_ok()
    }

    /// Check if string is ASCII
    #[staticmethod]
    pub fn is_ascii(text: &str) -> bool {
        text.is_ascii()
    }

    /// Check if string is valid UTF-8
    #[staticmethod]
    pub fn is_valid_utf8(bytes: &[u8]) -> bool {
        std::str::from_utf8(bytes).is_ok()
    }

    /// Validate base64 string
    #[staticmethod]
    pub fn validate_base64(base64_str: &str) -> bool {
        use base64::{engine::general_purpose, Engine as _};
        general_purpose::STANDARD.decode(base64_str).is_ok()
    }

    /// Check if string contains only printable characters
    #[staticmethod]
    pub fn is_printable(text: &str) -> bool {
        text.chars()
            .all(|c| c.is_ascii_graphic() || c.is_ascii_whitespace())
    }

    /// Sanitize string for safe logging
    #[staticmethod]
    pub fn sanitize_for_logging(text: &str) -> String {
        text.chars()
            .map(|c| {
                if c.is_control() && c != '\n' && c != '\t' {
                    '?'
                } else {
                    c
                }
            })
            .collect()
    }
}
