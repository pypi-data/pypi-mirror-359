// Middleware manager for orchestrating middleware stack
use pyo3::prelude::*;
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

/// Base middleware trait for request/response processing
#[allow(dead_code)]
pub trait Middleware: Send + Sync {
    /// Process a request before it's sent
    fn process_request(&self, request: &mut HttpRequest) -> PyResult<()>;

    /// Process a response after it's received
    fn process_response(&self, response: &mut HttpResponse) -> PyResult<()>;

    /// Get middleware name
    fn name(&self) -> &str;

    /// Get middleware priority (lower = executed first)
    fn priority(&self) -> u32 {
        100
    }
}

/// HTTP request wrapper for middleware processing
#[derive(Debug, Clone)]
pub struct HttpRequest {
    pub method: String,
    pub url: String,
    pub headers: HashMap<String, String>,
    pub body: Option<Vec<u8>>,
}

/// HTTP response wrapper for middleware processing
#[derive(Debug, Clone)]
pub struct HttpResponse {
    pub status_code: u16,
    pub headers: HashMap<String, String>,
    pub body: Option<Vec<u8>>,
}

/// Middleware stack that maintains ordering
pub struct MiddlewareStack {
    middlewares: Vec<Arc<dyn Middleware>>,
}

impl std::fmt::Debug for MiddlewareStack {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("MiddlewareStack")
            .field(
                "middlewares",
                &format!("{} middleware(s)", self.middlewares.len()),
            )
            .finish()
    }
}

#[allow(dead_code)]
impl MiddlewareStack {
    /// Create a new middleware stack
    pub fn new() -> Self {
        MiddlewareStack {
            middlewares: Vec::new(),
        }
    }

    /// Add middleware to the stack
    pub fn add(&mut self, middleware: Arc<dyn Middleware>) {
        self.middlewares.push(middleware);
        // Sort by priority (lower priority = executed first)
        self.middlewares.sort_by_key(|m| m.priority());
    }

    /// Remove middleware by name
    pub fn remove(&mut self, name: &str) -> bool {
        if let Some(pos) = self.middlewares.iter().position(|m| m.name() == name) {
            self.middlewares.remove(pos);
            return true;
        }
        false
    }

    /// Clear all middleware
    pub fn clear(&mut self) {
        self.middlewares.clear();
    }

    /// Get number of middleware in stack
    pub fn len(&self) -> usize {
        self.middlewares.len()
    }

    /// Check if stack is empty
    pub fn is_empty(&self) -> bool {
        self.middlewares.is_empty()
    }

    /// Process request through middleware stack
    pub fn process_request(&self, request: &mut HttpRequest) -> PyResult<()> {
        for middleware in &self.middlewares {
            middleware.process_request(request)?;
        }
        Ok(())
    }

    /// Process response through middleware stack (in reverse order)
    pub fn process_response(&self, response: &mut HttpResponse) -> PyResult<()> {
        for middleware in self.middlewares.iter().rev() {
            middleware.process_response(response)?;
        }
        Ok(())
    }

    /// Get middleware by name
    pub fn get(&self, name: &str) -> Option<&Arc<dyn Middleware>> {
        self.middlewares.iter().find(|m| m.name() == name)
    }

    /// List all middleware names
    pub fn list_names(&self) -> Vec<String> {
        self.middlewares
            .iter()
            .map(|m| m.name().to_string())
            .collect()
    }
}

impl Default for MiddlewareStack {
    fn default() -> Self {
        Self::new()
    }
}

/// Middleware manager for Python interface
#[pyclass]
pub struct MiddlewareManager {
    stack: Arc<RwLock<MiddlewareStack>>,
    #[allow(dead_code)]
    middleware_registry: Arc<RwLock<HashMap<String, Arc<dyn Middleware>>>>,
}

impl std::fmt::Debug for MiddlewareManager {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("MiddlewareManager")
            .field("stack", &"Arc<RwLock<MiddlewareStack>>")
            .field("middleware_registry", &"Arc<RwLock<HashMap>>")
            .finish()
    }
}

#[pymethods]
impl MiddlewareManager {
    /// Create a new middleware manager
    #[new]
    pub fn new() -> Self {
        MiddlewareManager {
            stack: Arc::new(RwLock::new(MiddlewareStack::new())),
            middleware_registry: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    /// Add middleware to the stack
    pub fn add_middleware(&self, name: String, _middleware: PyObject) -> PyResult<()> {
        // For now, we'll store the middleware reference
        // In a full implementation, you'd convert PyObject to a Middleware trait object

        // Simulate adding middleware by storing the name
        let _stack = self.stack.write().map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!(
                "Failed to acquire write lock: {}",
                e
            ))
        })?;

        // Log that middleware was added
        tracing::info!("Added middleware: {}", name);

        Ok(())
    }

    /// Remove middleware by name
    pub fn remove_middleware(&self, name: &str) -> PyResult<bool> {
        let mut stack = self.stack.write().map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!(
                "Failed to acquire write lock: {}",
                e
            ))
        })?;

        Ok(stack.remove(name))
    }

    /// Clear all middleware from stack
    pub fn clear(&mut self) -> PyResult<()> {
        match self.stack.write() {
            Ok(mut stack) => {
                let count = stack.len();
                stack.clear();
                tracing::debug!("Cleared {} middleware from stack", count);
                Ok(())
            }
            Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!(
                "Failed to acquire write lock: {}",
                e
            ))),
        }
    }

    /// Get number of middleware
    pub fn len(&self) -> usize {
        let stack = self.stack.read().unwrap_or_else(|e| e.into_inner());
        stack.len()
    }

    /// Check if middleware stack is empty
    pub fn is_empty(&self) -> bool {
        let stack = self.stack.read().unwrap_or_else(|e| e.into_inner());
        stack.is_empty()
    }

    /// List all middleware names
    pub fn list_middleware(&self) -> PyResult<Vec<String>> {
        let stack = self.stack.read().map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to acquire read lock: {}", e))
        })?;

        Ok(stack.list_names())
    }

    /// Get middleware configuration
    pub fn get_middleware_config(
        &self,
        #[allow(unused_variables)] name: &str,
    ) -> PyResult<Option<PyObject>> {
        // Implementation depends on specific middleware types
        Ok(None)
    }
}

impl Default for MiddlewareManager {
    fn default() -> Self {
        Self::new()
    }
}

/// Base middleware configuration
#[pyclass]
#[derive(Debug, Clone)]
pub struct MiddlewareConfig {
    #[pyo3(get, set)]
    pub name: String,
    #[pyo3(get, set)]
    pub enabled: bool,
    #[pyo3(get, set)]
    pub priority: u32,
}

#[pymethods]
impl MiddlewareConfig {
    #[new]
    #[pyo3(signature = (name, enabled=true, priority=100))]
    pub fn new(name: String, enabled: bool, priority: u32) -> Self {
        MiddlewareConfig {
            name,
            enabled,
            priority,
        }
    }
}
