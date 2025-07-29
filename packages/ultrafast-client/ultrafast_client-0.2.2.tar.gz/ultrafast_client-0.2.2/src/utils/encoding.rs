// Encoding utilities module
use base64::{engine::general_purpose, Engine as _};
use pyo3::prelude::*;
use std::collections::HashMap;

/// Encoding utilities
#[pyclass]
#[derive(Debug)]
pub struct EncodingUtils;

#[pymethods]
impl EncodingUtils {
    /// Encode string to base64
    #[staticmethod]
    pub fn base64_encode(data: &str) -> String {
        general_purpose::STANDARD.encode(data.as_bytes())
    }

    /// Decode base64 string
    #[staticmethod]
    pub fn base64_decode(encoded: &str) -> PyResult<String> {
        general_purpose::STANDARD
            .decode(encoded)
            .map_err(|e| {
                pyo3::exceptions::PyValueError::new_err(format!("Base64 decode error: {}", e))
            })
            .and_then(|bytes| {
                String::from_utf8(bytes).map_err(|e| {
                    pyo3::exceptions::PyValueError::new_err(format!("UTF-8 decode error: {}", e))
                })
            })
    }

    /// URL encode string
    #[staticmethod]
    pub fn url_encode(data: &str) -> String {
        urlencoding::encode(data).to_string()
    }

    /// URL decode string
    #[staticmethod]
    pub fn url_decode(encoded: &str) -> PyResult<String> {
        urlencoding::decode(encoded)
            .map(|s| s.into_owned())
            .map_err(|e| {
                pyo3::exceptions::PyValueError::new_err(format!("URL decode error: {}", e))
            })
    }

    /// Encode form data
    #[staticmethod]
    pub fn encode_form_data(data: HashMap<String, String>) -> String {
        data.iter()
            .map(|(key, value)| {
                format!(
                    "{}={}",
                    urlencoding::encode(key),
                    urlencoding::encode(value)
                )
            })
            .collect::<Vec<_>>()
            .join("&")
    }

    /// Generate multipart boundary
    #[staticmethod]
    pub fn generate_multipart_boundary() -> String {
        use uuid::Uuid;
        format!("----UltraFastBoundary{}", Uuid::new_v4().simple())
    }

    /// Encode multipart form data
    #[staticmethod]
    pub fn encode_multipart_form_data(
        fields: HashMap<String, String>,
        files: HashMap<String, Vec<u8>>,
    ) -> (String, Vec<u8>) {
        let boundary = Self::generate_multipart_boundary();
        let mut body = Vec::new();

        // Add text fields
        for (name, value) in fields {
            body.extend_from_slice(format!("--{}\r\n", boundary).as_bytes());
            body.extend_from_slice(
                format!("Content-Disposition: form-data; name=\"{}\"\r\n\r\n", name).as_bytes(),
            );
            body.extend_from_slice(value.as_bytes());
            body.extend_from_slice(b"\r\n");
        }

        // Add file fields
        for (name, file_data) in files {
            body.extend_from_slice(format!("--{}\r\n", boundary).as_bytes());
            body.extend_from_slice(
                format!(
                    "Content-Disposition: form-data; name=\"{}\"; filename=\"{}\"\r\n",
                    name, name
                )
                .as_bytes(),
            );
            body.extend_from_slice(b"Content-Type: application/octet-stream\r\n\r\n");
            body.extend_from_slice(&file_data);
            body.extend_from_slice(b"\r\n");
        }

        // Add closing boundary
        body.extend_from_slice(format!("--{}--\r\n", boundary).as_bytes());

        let content_type = format!("multipart/form-data; boundary={}", boundary);
        (content_type, body)
    }

    /// Convert bytes to hex string
    #[staticmethod]
    pub fn bytes_to_hex(data: &[u8]) -> String {
        data.iter().map(|b| format!("{:02x}", b)).collect()
    }

    /// Convert hex string to bytes
    #[staticmethod]
    pub fn hex_to_bytes(hex: &str) -> PyResult<Vec<u8>> {
        if hex.len() % 2 != 0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Hex string must have even length",
            ));
        }

        (0..hex.len())
            .step_by(2)
            .map(|i| {
                u8::from_str_radix(&hex[i..i + 2], 16).map_err(|e| {
                    pyo3::exceptions::PyValueError::new_err(format!("Invalid hex: {}", e))
                })
            })
            .collect()
    }
}
