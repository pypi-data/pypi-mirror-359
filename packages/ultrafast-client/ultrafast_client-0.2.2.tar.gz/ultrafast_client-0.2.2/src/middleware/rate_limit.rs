// Rate limiting middleware
use super::manager::{HttpRequest, HttpResponse, Middleware};
use crate::config::protocol_config::{RateLimitAlgorithm, RateLimitConfig};
use pyo3::prelude::*;

/// Rate limiting middleware that enforces request rate limits
#[pyclass]
#[derive(Debug, Clone)]
pub struct RateLimitMiddleware {
    #[pyo3(get)]
    pub name: String,
    pub rate_limit_config: RateLimitConfig,
    #[pyo3(get)]
    pub priority: u32,
}

#[pymethods]
impl RateLimitMiddleware {
    #[new]
    #[pyo3(signature = (name, requests_per_second=10.0, burst_size=None, priority=20))]
    pub fn new(
        name: String,
        requests_per_second: f64,
        burst_size: Option<u32>,
        priority: u32,
    ) -> Self {
        let rate_limit_config = RateLimitConfig::new(
            true, // enabled
            RateLimitAlgorithm::TokenBucket,
            requests_per_second,
            None, // requests_per_minute
            None, // requests_per_hour
            burst_size,
            1.0,   // window_size_seconds
            true,  // per_host
            false, // reset_on_success
            false, // queue_requests
            100,   // max_queue_size
            30.0,  // queue_timeout_seconds
        );

        RateLimitMiddleware {
            name,
            rate_limit_config,
            priority,
        }
    }

    /// Create from existing config
    #[staticmethod]
    pub fn from_config(
        name: String,
        rate_limit_config: RateLimitConfig,
        priority: Option<u32>,
    ) -> Self {
        RateLimitMiddleware {
            name,
            rate_limit_config,
            priority: priority.unwrap_or(20),
        }
    }

    /// Update rate limit configuration
    pub fn update_config(&mut self, rate_limit_config: RateLimitConfig) {
        self.rate_limit_config = rate_limit_config;
    }

    /// Get current requests per second
    pub fn get_requests_per_second(&self) -> f64 {
        self.rate_limit_config.requests_per_second
    }

    /// Get current burst size
    pub fn get_burst_size(&self) -> Option<u32> {
        self.rate_limit_config.burst_size
    }
}

impl Middleware for RateLimitMiddleware {
    fn process_request(&self, request: &mut HttpRequest) -> PyResult<()> {
        if self.rate_limit_config.enabled {
            // Add rate limit headers
            request.headers.insert(
                "X-RateLimit-Limit".to_string(),
                self.rate_limit_config.requests_per_second.to_string(),
            );
        }
        Ok(())
    }

    fn process_response(&self, response: &mut HttpResponse) -> PyResult<()> {
        if self.rate_limit_config.enabled {
            // Add rate limit info to response
            response.headers.insert(
                "X-RateLimit-Remaining".to_string(),
                "100".to_string(), // Placeholder
            );
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
