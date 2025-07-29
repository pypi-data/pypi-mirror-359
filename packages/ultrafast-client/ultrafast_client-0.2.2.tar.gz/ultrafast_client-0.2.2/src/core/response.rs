// Response handling module
// This is a stub that re-exports from the original location during the transition

// Re-export from original location for backward compatibility
// pub use crate::response::*; // Commented out to reduce warnings

use pyo3::prelude::*;
use std::collections::HashMap;

/// HTTP Response wrapper for Python interface
#[pyclass]
#[derive(Debug, Clone)]
pub struct ClientResponse {
    #[pyo3(get)]
    pub status_code: u16,
    pub headers: HashMap<String, String>,
    pub body: Vec<u8>,
    #[pyo3(get)]
    pub url: String,
}

#[pymethods]
impl ClientResponse {
    #[new]
    pub fn new(
        status_code: u16,
        headers: HashMap<String, String>,
        body: Vec<u8>,
        url: String,
    ) -> Self {
        ClientResponse {
            status_code,
            headers,
            body,
            url,
        }
    }

    /// Get response body as text
    pub fn text(&self) -> PyResult<String> {
        String::from_utf8(self.body.clone())
            .map_err(|e| pyo3::exceptions::PyUnicodeDecodeError::new_err(e.to_string()))
    }

    /// Get response body as bytes
    pub fn content(&self, py: Python<'_>) -> PyResult<PyObject> {
        Ok(pyo3::types::PyBytes::new(py, &self.body).into())
    }

    /// Get response body as JSON
    pub fn json(&self, py: Python<'_>) -> PyResult<PyObject> {
        let text = self.text()?;
        let json_module = py.import("json")?;
        Ok(json_module.call_method1("loads", (text,))?.into())
    }

    /// Check if response is successful (2xx status code)
    pub fn is_success(&self) -> bool {
        self.status_code >= 200 && self.status_code < 300
    }

    /// Check if response is a client error (4xx status code)
    pub fn is_client_error(&self) -> bool {
        self.status_code >= 400 && self.status_code < 500
    }

    /// Check if response is a server error (5xx status code)
    pub fn is_server_error(&self) -> bool {
        self.status_code >= 500 && self.status_code < 600
    }

    /// Get header value by name
    pub fn get_header(&self, name: &str) -> Option<String> {
        self.headers.get(&name.to_lowercase()).cloned()
    }

    /// Get all headers
    pub fn get_headers(&self) -> HashMap<String, String> {
        self.headers.clone()
    }

    /// Get all headers (method version for compatibility)
    pub fn headers(&self) -> HashMap<String, String> {
        self.headers.clone()
    }

    /// Get URL (method version for compatibility)
    pub fn url(&self) -> String {
        self.url.clone()
    }

    /// Get response size in bytes
    pub fn size(&self) -> usize {
        self.body.len()
    }

    /// String representation
    pub fn __repr__(&self) -> String {
        format!("<ClientResponse {} {}>", self.status_code, self.url)
    }

    /// String representation
    pub fn __str__(&self) -> String {
        self.__repr__()
    }

    /// Check if response is successful (convenience method)
    pub fn ok(&self) -> bool {
        self.is_success()
    }

    /// Get elapsed time (placeholder - not implemented)
    pub fn elapsed(&self) -> f64 {
        0.0 // Placeholder, would need to track request timing
    }

    /// Get encoding (placeholder)
    pub fn encoding(&self) -> String {
        "utf-8".to_string() // Default encoding
    }

    /// Get reason phrase for status code
    pub fn reason(&self) -> String {
        match self.status_code {
            200 => "OK".to_string(),
            201 => "Created".to_string(),
            204 => "No Content".to_string(),
            400 => "Bad Request".to_string(),
            401 => "Unauthorized".to_string(),
            403 => "Forbidden".to_string(),
            404 => "Not Found".to_string(),
            500 => "Internal Server Error".to_string(),
            _ => "Unknown".to_string(),
        }
    }
}

impl ClientResponse {
    /// Create from reqwest blocking response
    pub fn from_reqwest_blocking(response: reqwest::blocking::Response) -> PyResult<Self> {
        let status_code = response.status().as_u16();
        let url = response.url().to_string();

        let mut headers = HashMap::new();
        for (name, value) in response.headers().iter() {
            headers.insert(
                name.as_str().to_lowercase(),
                value.to_str().unwrap_or("").to_string(),
            );
        }

        let body = response
            .bytes()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?
            .to_vec();

        Ok(ClientResponse {
            status_code,
            headers,
            body,
            url,
        })
    }

    /// Create from reqwest async response
    pub async fn from_reqwest_async(response: reqwest::Response) -> PyResult<Self> {
        let status_code = response.status().as_u16();
        let url = response.url().to_string();

        let mut headers = HashMap::new();
        for (name, value) in response.headers().iter() {
            headers.insert(
                name.as_str().to_lowercase(),
                value.to_str().unwrap_or("").to_string(),
            );
        }

        let body = response
            .bytes()
            .await
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?
            .to_vec();

        Ok(ClientResponse {
            status_code,
            headers,
            body,
            url,
        })
    }
}

// Type alias for backwards compatibility
#[allow(dead_code)]
pub type Response = ClientResponse;
