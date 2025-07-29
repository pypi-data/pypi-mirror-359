// Headers middleware
use super::manager::{HttpRequest, HttpResponse, Middleware};
use pyo3::prelude::*;
use std::collections::HashMap;

/// Headers middleware that adds custom headers to requests
#[pyclass]
#[derive(Debug, Clone)]
pub struct HeadersMiddleware {
    #[pyo3(get)]
    pub name: String,
    pub headers: HashMap<String, String>,
    #[pyo3(get)]
    pub priority: u32,
}

#[pymethods]
impl HeadersMiddleware {
    #[new]
    #[pyo3(signature = (name, headers=None, priority=50))]
    pub fn new(name: String, headers: Option<HashMap<String, String>>, priority: u32) -> Self {
        HeadersMiddleware {
            name,
            headers: headers.unwrap_or_default(),
            priority,
        }
    }

    /// Add header
    pub fn add_header(&mut self, name: &str, value: &str) {
        self.headers.insert(name.to_string(), value.to_string());
    }

    /// Remove header
    pub fn remove_header(&mut self, name: &str) -> Option<String> {
        self.headers.remove(name)
    }

    /// Get headers
    pub fn get_headers(&self) -> HashMap<String, String> {
        self.headers.clone()
    }

    /// Set headers
    pub fn set_headers(&mut self, headers: HashMap<String, String>) {
        self.headers = headers;
    }
}

impl Middleware for HeadersMiddleware {
    fn process_request(&self, request: &mut HttpRequest) -> PyResult<()> {
        // Add all configured headers to the request
        for (key, value) in &self.headers {
            request.headers.insert(key.clone(), value.clone());
        }
        Ok(())
    }

    fn process_response(&self, _response: &mut HttpResponse) -> PyResult<()> {
        // Headers middleware typically doesn't modify responses
        Ok(())
    }

    fn name(&self) -> &str {
        &self.name
    }

    fn priority(&self) -> u32 {
        self.priority
    }
}
