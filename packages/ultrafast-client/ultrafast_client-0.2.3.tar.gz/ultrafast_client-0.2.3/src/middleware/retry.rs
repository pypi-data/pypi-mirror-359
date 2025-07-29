// Retry middleware
use super::manager::{HttpRequest, HttpResponse, Middleware};
use crate::config::client_config::RetryConfig;
use pyo3::prelude::*;

/// Retry middleware that handles request retries
#[pyclass]
#[derive(Debug, Clone)]
pub struct RetryMiddleware {
    #[pyo3(get)]
    pub name: String,
    pub retry_config: RetryConfig,
    #[pyo3(get)]
    pub priority: u32,
}

#[pymethods]
impl RetryMiddleware {
    #[new]
    #[pyo3(signature = (name, retry_config, priority=50))]
    pub fn new(name: String, retry_config: RetryConfig, priority: u32) -> Self {
        RetryMiddleware {
            name,
            retry_config,
            priority,
        }
    }

    /// Update retry configuration
    pub fn update_config(&mut self, retry_config: RetryConfig) {
        self.retry_config = retry_config;
    }
}

impl Middleware for RetryMiddleware {
    fn process_request(&self, request: &mut HttpRequest) -> PyResult<()> {
        // Add retry metadata to request headers
        request.headers.insert(
            "X-Max-Retries".to_string(),
            self.retry_config.max_retries.to_string(),
        );
        Ok(())
    }

    fn process_response(&self, response: &mut HttpResponse) -> PyResult<()> {
        // Check if response indicates a retryable error
        if self.retry_config.should_retry_status(response.status_code) {
            response
                .headers
                .insert("X-Should-Retry".to_string(), "true".to_string());
        }
        Ok(())
    }

    fn name(&self) -> &str {
        &self.name
    }

    fn priority(&self) -> u32 {
        self.priority
    }
}
