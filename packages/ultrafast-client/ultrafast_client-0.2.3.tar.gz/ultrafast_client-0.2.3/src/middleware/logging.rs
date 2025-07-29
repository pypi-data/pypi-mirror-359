// Logging middleware
use super::manager::{HttpRequest, HttpResponse, Middleware};
use pyo3::prelude::*;
use std::time::Instant;
use tracing::{debug, info, span, Level};

/// Logging middleware that logs requests and responses
#[pyclass]
#[derive(Debug, Clone)]
pub struct LoggingMiddleware {
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub log_requests: bool,
    #[pyo3(get)]
    pub log_responses: bool,
    #[pyo3(get)]
    pub log_request_body: bool,
    #[pyo3(get)]
    pub log_response_body: bool,
    #[pyo3(get)]
    pub priority: u32,
}

#[pymethods]
impl LoggingMiddleware {
    #[new]
    #[pyo3(signature = (name, log_requests=true, log_responses=true, log_request_body=false, log_response_body=false, priority=200))]
    pub fn new(
        name: String,
        log_requests: bool,
        log_responses: bool,
        log_request_body: bool,
        log_response_body: bool,
        priority: u32,
    ) -> Self {
        LoggingMiddleware {
            name,
            log_requests,
            log_responses,
            log_request_body,
            log_response_body,
            priority,
        }
    }
}

impl Middleware for LoggingMiddleware {
    fn process_request(&self, request: &mut HttpRequest) -> PyResult<()> {
        let _span = span!(Level::INFO, "http_request",
            middleware = %self.name,
            method = %request.method,
            url = %request.url
        )
        .entered();

        if self.log_requests {
            let header_names: Vec<&String> = request.headers.keys().collect();
            info!(
                middleware = %self.name,
                method = %request.method,
                url = %request.url,
                headers = ?header_names,
                "Processing HTTP request"
            );

            if self.log_request_body {
                if let Some(body) = &request.body {
                    debug!(
                        middleware = %self.name,
                        body_size = body.len(),
                        "Request body details"
                    );
                }
            }
        }

        // Add request timestamp for duration calculation
        request.headers.insert(
            "X-Request-Start".to_string(),
            Instant::now().elapsed().as_millis().to_string(),
        );

        Ok(())
    }

    fn process_response(&self, response: &mut HttpResponse) -> PyResult<()> {
        let _span = span!(Level::INFO, "http_response",
            middleware = %self.name,
            status_code = response.status_code
        )
        .entered();

        if self.log_responses {
            let header_names: Vec<&String> = response.headers.keys().collect();
            info!(
                middleware = %self.name,
                status_code = response.status_code,
                headers = ?header_names,
                "Processing HTTP response"
            );

            if self.log_response_body {
                if let Some(body) = &response.body {
                    debug!(
                        middleware = %self.name,
                        body_size = body.len(),
                        "Response body details"
                    );
                }
            }
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
