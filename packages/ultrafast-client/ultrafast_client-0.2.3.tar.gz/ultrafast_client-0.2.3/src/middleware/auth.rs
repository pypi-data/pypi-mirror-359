// Authentication middleware
use super::manager::{HttpRequest, HttpResponse, Middleware};
use crate::config::auth_config::AuthConfig;
use pyo3::prelude::*;

/// Authentication middleware that applies auth headers to requests
#[pyclass]
#[derive(Debug, Clone)]
pub struct AuthMiddleware {
    #[pyo3(get)]
    pub name: String,
    pub auth_config: AuthConfig,
    #[pyo3(get)]
    pub priority: u32,
}

#[pymethods]
impl AuthMiddleware {
    #[new]
    #[pyo3(signature = (name, auth_config, priority=10))]
    pub fn new(name: String, auth_config: AuthConfig, priority: u32) -> Self {
        AuthMiddleware {
            name,
            auth_config,
            priority,
        }
    }

    /// Update authentication configuration
    pub fn update_auth(&mut self, auth_config: AuthConfig) {
        self.auth_config = auth_config;
    }
}

impl Middleware for AuthMiddleware {
    fn process_request(&self, request: &mut HttpRequest) -> PyResult<()> {
        // Apply authentication headers
        if let Ok(auth_headers) = self.auth_config.generate_headers() {
            for (key, value) in auth_headers {
                request.headers.insert(key, value);
            }
        }
        Ok(())
    }

    fn process_response(&self, _response: &mut HttpResponse) -> PyResult<()> {
        // Authentication middleware typically doesn't modify responses
        Ok(())
    }

    fn name(&self) -> &str {
        &self.name
    }

    fn priority(&self) -> u32 {
        self.priority
    }
}
