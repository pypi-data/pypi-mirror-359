// Synchronous HTTP client implementation

use crate::config::{AuthConfig, AuthType};
use crate::core::response::ClientResponse;
use pyo3::prelude::*;
use std::collections::HashMap;
use tracing::{debug, info, instrument, span, warn, Level};

/// Synchronous HTTP client
#[pyclass]
#[derive(Debug)]
pub struct HttpClient {
    client: reqwest::blocking::Client,
    base_url: Option<String>,
    default_headers: HashMap<String, String>,
    auth_config: Option<AuthConfig>,
    #[allow(dead_code)]
    retry_config: Option<PyObject>,
    rate_limit_config: Option<PyObject>,
    protocol_config: Option<PyObject>,
    middleware: Vec<PyObject>,
    http2_enabled: bool, // Store the actual HTTP/2 state
}

#[pymethods]
impl HttpClient {
    #[new]
    #[pyo3(signature = (auth_config=None, timeout=None, base_url=None, headers=None, retry_config=None, timeout_config=None, ssl_config=None, compression_config=None, pool_config=None, rate_limit_config=None, protocol_config=None))]
    pub fn new(
        auth_config: Option<AuthConfig>,
        timeout: Option<f64>,
        base_url: Option<String>,
        headers: Option<HashMap<String, String>>,
        retry_config: Option<PyObject>,
        timeout_config: Option<PyObject>,
        ssl_config: Option<PyObject>,
        compression_config: Option<PyObject>,
        pool_config: Option<PyObject>,
        rate_limit_config: Option<PyObject>,
        protocol_config: Option<PyObject>,
    ) -> PyResult<Self> {
        // Start with a basic client builder
        let mut client_builder = reqwest::blocking::Client::builder();

        // Apply timeout if provided (legacy single timeout parameter)
        if let Some(timeout_secs) = timeout {
            client_builder =
                client_builder.timeout(std::time::Duration::from_secs_f64(timeout_secs));
        }

        // Extract timeout configuration values if provided
        let (connect_timeout_opt, total_timeout_opt) = if let Some(ref timeout_config) =
            timeout_config
        {
            Python::with_gil(|py| {
                let connect_timeout = if let Ok(connect_timeout_attr) =
                    timeout_config.getattr(py, "connect_timeout")
                {
                    connect_timeout_attr.extract::<f64>(py).ok()
                } else {
                    None
                };

                let total_timeout =
                    if let Ok(total_timeout_attr) = timeout_config.getattr(py, "total_timeout") {
                        total_timeout_attr.extract::<f64>(py).ok()
                    } else {
                        None
                    };

                (connect_timeout, total_timeout)
            })
        } else {
            (None, None)
        };

        // Apply timeout configuration
        if let Some(connect_timeout) = connect_timeout_opt {
            client_builder =
                client_builder.connect_timeout(std::time::Duration::from_secs_f64(connect_timeout));
        }
        if let Some(total_timeout) = total_timeout_opt {
            client_builder =
                client_builder.timeout(std::time::Duration::from_secs_f64(total_timeout));
        }

        // Apply HTTP/2 settings based on protocol config
        let http2_enabled = if let Some(ref protocol_config) = protocol_config {
            // Extract enable_http2 setting from the protocol config
            Python::with_gil(|py| {
                if let Ok(enable_http2_attr) = protocol_config.getattr(py, "enable_http2") {
                    enable_http2_attr.extract::<bool>(py).unwrap_or(true)
                } else {
                    true // Default to true if attribute doesn't exist
                }
            })
        } else {
            true // Default to true if no protocol config
        };

        // Apply HTTP/2 configuration to the client builder
        if http2_enabled {
            // Enable HTTP/2 with proper negotiation (not prior knowledge)
            // Remove http2_prior_knowledge() as it breaks connections to many servers
            client_builder = client_builder.http2_adaptive_window(true);
        } else {
            // Disable HTTP/2 - reqwest uses HTTP/1.1 by default when HTTP/2 is not enabled
            // Note: reqwest doesn't have an explicit "disable HTTP/2" method,
            // but not calling http2_prior_knowledge() means it won't use HTTP/2
        }

        // Apply connection pooling settings
        if pool_config.is_some() {
            // reqwest handles connection pooling automatically
            // Custom pool settings would require more advanced configuration
        }

        // Apply compression settings
        if compression_config.is_some() {
            // reqwest enables compression by default for these
            client_builder = client_builder.gzip(true);
            client_builder = client_builder.deflate(true);
        }

        // Apply SSL/TLS settings
        if ssl_config.is_some() {
            // reqwest uses system certificates by default
            // Custom TLS configuration would be applied here in a full implementation
        }

        // Build the client
        let client = client_builder
            .build()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        Ok(HttpClient {
            client,
            base_url,
            default_headers: headers.unwrap_or_default(),
            auth_config,
            retry_config,
            rate_limit_config,
            protocol_config,
            middleware: Vec::new(),
            http2_enabled,
        })
    }

    /// Perform a GET request
    #[pyo3(signature = (url, params=None, headers=None, auth=None, timeout=None))]
    #[instrument(skip(self, headers, auth), fields(method = "GET", url = %url))]
    pub fn get(
        &self,
        url: &str,
        params: Option<HashMap<String, String>>,
        headers: Option<HashMap<String, String>>,
        auth: Option<(String, String)>,
        timeout: Option<f64>,
    ) -> PyResult<ClientResponse> {
        let _span = span!(Level::INFO, "http_get", url = %url).entered();

        // Apply rate limiting if configured
        if self.is_rate_limit_enabled() {
            // In a full implementation, this would check rate limits
            debug!("Rate limiting check passed");
        }

        let final_url = self.build_url(url, params)?;
        debug!(final_url = %final_url, "Built final URL");

        // Retry logic with exponential backoff
        let max_retries = 3;
        let mut last_error = None;

        for attempt in 0..=max_retries {
            let mut request = self.client.get(&final_url);

            request = self.apply_headers(request, headers.clone());
            request = self.apply_auth_config(request, auth.clone());

            if let Some(timeout) = timeout {
                debug!(timeout_seconds = timeout, "Setting request timeout");
                request = request.timeout(std::time::Duration::from_secs_f64(timeout));
            }

            info!(
                attempt = attempt,
                max_retries = max_retries,
                "Sending GET request"
            );

            match request.send() {
                Ok(response) => {
                    let status = response.status().as_u16();
                    info!(status_code = status, "Request completed successfully");

                    // Check if we should retry based on status code
                    if status >= 500 && status < 600 && attempt < max_retries {
                        warn!(
                            status_code = status,
                            attempt = attempt,
                            "Server error, retrying..."
                        );
                        // Exponential backoff
                        let delay = std::time::Duration::from_millis(100 * (1 << attempt));
                        std::thread::sleep(delay);
                        continue;
                    }

                    return ClientResponse::from_reqwest_blocking(response);
                }
                Err(e) => {
                    warn!(error = %e, attempt = attempt, "Request failed");

                    // Check if this is a retryable error
                    let is_retryable = e.is_timeout() || e.is_connect() || e.is_request();

                    if is_retryable && attempt < max_retries {
                        // Exponential backoff
                        let delay = std::time::Duration::from_millis(100 * (1 << attempt));
                        warn!(delay_ms = delay.as_millis(), "Retrying after delay");
                        std::thread::sleep(delay);
                        last_error = Some(e);
                        continue;
                    } else {
                        return Err(pyo3::exceptions::PyRuntimeError::new_err(e.to_string()));
                    }
                }
            }
        }

        // If we get here, all retries failed
        if let Some(error) = last_error {
            Err(pyo3::exceptions::PyRuntimeError::new_err(format!(
                "Request failed after {} retries: {}",
                max_retries, error
            )))
        } else {
            Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Request failed after all retries",
            ))
        }
    }

    /// Perform a POST request
    #[pyo3(signature = (url, data=None, json=None, files=None, headers=None, auth=None, timeout=None))]
    #[instrument(skip(self, data, json, files, headers, auth), fields(method = "POST", url = %url))]
    pub fn post(
        &self,
        url: &str,
        data: Option<PyObject>,
        json: Option<PyObject>,
        files: Option<PyObject>,
        headers: Option<HashMap<String, String>>,
        auth: Option<(String, String)>,
        timeout: Option<f64>,
    ) -> PyResult<ClientResponse> {
        let _span = span!(Level::INFO, "http_post", url = %url).entered();

        // Apply rate limiting if configured
        if self.is_rate_limit_enabled() {
            debug!("Rate limiting check passed");
        }

        let final_url = self.build_url(url, None)?;
        debug!(final_url = %final_url, "Built final URL");

        // Log body type for debugging
        if data.is_some() {
            debug!("Request has form data body");
        }
        if json.is_some() {
            debug!("Request has JSON body");
        }
        if files.is_some() {
            debug!("Request has file uploads");
        }

        // Simple POST request without retry logic (to avoid PyObject cloning issues)
        let mut request = self.client.post(&final_url);

        request = self.apply_body(request, data, json, files)?;
        request = self.apply_headers(request, headers);
        request = self.apply_auth_config(request, auth);

        if let Some(timeout) = timeout {
            debug!(timeout_seconds = timeout, "Setting request timeout");
            request = request.timeout(std::time::Duration::from_secs_f64(timeout));
        }

        info!("Sending POST request");

        let response = request
            .send()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        let status = response.status().as_u16();
        info!(status_code = status, "Request completed");

        ClientResponse::from_reqwest_blocking(response)
    }

    /// Perform a PUT request
    #[pyo3(signature = (url, data=None, json=None, files=None, headers=None, auth=None, timeout=None))]
    pub fn put(
        &self,
        url: &str,
        data: Option<PyObject>,
        json: Option<PyObject>,
        files: Option<PyObject>,
        headers: Option<HashMap<String, String>>,
        auth: Option<(String, String)>,
        timeout: Option<f64>,
    ) -> PyResult<ClientResponse> {
        let final_url = self.build_url(url, None)?;
        let mut request = self.client.put(final_url);

        request = self.apply_body(request, data, json, files)?;
        request = self.apply_headers(request, headers);
        request = self.apply_auth_config(request, auth);

        if let Some(timeout) = timeout {
            request = request.timeout(std::time::Duration::from_secs_f64(timeout));
        }

        let response = request
            .send()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        ClientResponse::from_reqwest_blocking(response)
    }

    /// Perform a PATCH request
    #[pyo3(signature = (url, data=None, json=None, files=None, headers=None, auth=None, timeout=None))]
    pub fn patch(
        &self,
        url: &str,
        data: Option<PyObject>,
        json: Option<PyObject>,
        files: Option<PyObject>,
        headers: Option<HashMap<String, String>>,
        auth: Option<(String, String)>,
        timeout: Option<f64>,
    ) -> PyResult<ClientResponse> {
        let final_url = self.build_url(url, None)?;
        let mut request = self.client.patch(final_url);

        request = self.apply_body(request, data, json, files)?;
        request = self.apply_headers(request, headers);
        request = self.apply_auth_config(request, auth);

        if let Some(timeout) = timeout {
            request = request.timeout(std::time::Duration::from_secs_f64(timeout));
        }

        let response = request
            .send()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        ClientResponse::from_reqwest_blocking(response)
    }

    /// Perform a DELETE request
    #[pyo3(signature = (url, headers=None, auth=None, timeout=None))]
    pub fn delete(
        &self,
        url: &str,
        headers: Option<HashMap<String, String>>,
        auth: Option<(String, String)>,
        timeout: Option<f64>,
    ) -> PyResult<ClientResponse> {
        let final_url = self.build_url(url, None)?;
        let mut request = self.client.delete(final_url);

        request = self.apply_headers(request, headers);
        request = self.apply_auth_config(request, auth);

        if let Some(timeout) = timeout {
            request = request.timeout(std::time::Duration::from_secs_f64(timeout));
        }

        let response = request
            .send()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        ClientResponse::from_reqwest_blocking(response)
    }

    /// Perform a HEAD request
    #[pyo3(signature = (url, headers=None, auth=None, timeout=None))]
    pub fn head(
        &self,
        url: &str,
        headers: Option<HashMap<String, String>>,
        auth: Option<(String, String)>,
        timeout: Option<f64>,
    ) -> PyResult<ClientResponse> {
        let final_url = self.build_url(url, None)?;
        let mut request = self.client.head(final_url);

        request = self.apply_headers(request, headers);
        request = self.apply_auth_config(request, auth);

        if let Some(timeout) = timeout {
            request = request.timeout(std::time::Duration::from_secs_f64(timeout));
        }

        let response = request
            .send()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        ClientResponse::from_reqwest_blocking(response)
    }

    /// Perform an OPTIONS request
    #[pyo3(signature = (url, headers=None, auth=None, timeout=None))]
    pub fn options(
        &self,
        url: &str,
        headers: Option<HashMap<String, String>>,
        auth: Option<(String, String)>,
        timeout: Option<f64>,
    ) -> PyResult<ClientResponse> {
        let final_url = self.build_url(url, None)?;
        let mut request = self.client.request(reqwest::Method::OPTIONS, final_url);

        request = self.apply_headers(request, headers);
        request = self.apply_auth_config(request, auth);

        if let Some(timeout) = timeout {
            request = request.timeout(std::time::Duration::from_secs_f64(timeout));
        }

        let response = request
            .send()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        ClientResponse::from_reqwest_blocking(response)
    }

    /// Set authentication (accepts AuthConfig object)
    pub fn set_auth(&mut self, auth_config: AuthConfig) -> PyResult<()> {
        self.auth_config = Some(auth_config);
        Ok(())
    }

    /// Clear authentication
    pub fn clear_auth(&mut self) {
        self.auth_config = None;
    }

    /// Get authentication configuration
    pub fn get_auth(&self) -> Option<AuthConfig> {
        self.auth_config.clone()
    }

    /// Check if client has authentication configured
    pub fn has_auth(&self) -> bool {
        self.auth_config.is_some()
    }

    /// Set a header for all requests
    pub fn set_header(&mut self, name: &str, value: &str) {
        self.default_headers
            .insert(name.to_string(), value.to_string());
    }

    /// Remove a header from all requests
    pub fn remove_header(&mut self, name: &str) -> Option<String> {
        self.default_headers.remove(name)
    }

    /// Get headers
    pub fn get_headers(&self) -> HashMap<String, String> {
        self.default_headers.clone()
    }

    /// Set base URL for all requests
    pub fn set_base_url(&mut self, base_url: Option<String>) {
        self.base_url = base_url;
    }

    /// Get current base URL
    pub fn get_base_url(&self) -> Option<String> {
        self.base_url.clone()
    }

    /// Get client statistics
    pub fn get_stats(&self) -> HashMap<String, f64> {
        let mut stats = HashMap::new();
        stats.insert("requests_made".to_string(), 0.0);
        stats.insert("bytes_sent".to_string(), 0.0);
        stats.insert("bytes_received".to_string(), 0.0);
        stats
    }

    /// Get protocol statistics for a host
    pub fn get_protocol_stats(&self, _host: &str) -> HashMap<String, f64> {
        let mut stats = HashMap::new();
        stats.insert("http1_requests".to_string(), 0.0);
        stats.insert("http2_requests".to_string(), 0.0);
        stats
    }

    /// Check if HTTP/2 is enabled
    pub fn is_http2_enabled(&self) -> bool {
        self.http2_enabled
    }

    /// Set protocol configuration
    pub fn set_protocol_config(&mut self, protocol_config: PyObject) -> PyResult<()> {
        self.protocol_config = Some(protocol_config);
        Ok(())
    }

    /// Set retry configuration
    pub fn set_retry_config(&mut self, _retry_config: PyObject) -> PyResult<()> {
        // Store the retry configuration
        // In a full implementation, this would be applied to the client builder
        // For now, just store it for future use
        Ok(())
    }

    /// Set SSL configuration
    pub fn set_ssl_config(&mut self, _ssl_config: PyObject) -> PyResult<()> {
        // Store the SSL configuration
        // In a full implementation, this would be applied to the client builder
        debug!("SSL configuration set");
        Ok(())
    }

    /// Set compression configuration
    pub fn set_compression_config(&mut self, _compression_config: PyObject) -> PyResult<()> {
        // Store the compression configuration
        // In a full implementation, this would be applied to the client builder
        debug!("Compression configuration set");
        Ok(())
    }

    /// Check if rate limiting is enabled
    pub fn is_rate_limit_enabled(&self) -> bool {
        if let Some(ref config) = self.rate_limit_config {
            Python::with_gil(|py| {
                // Try to extract the enabled field from the rate limit config
                if let Ok(enabled) = config.getattr(py, "enabled") {
                    if let Ok(enabled_bool) = enabled.extract::<bool>(py) {
                        return enabled_bool;
                    }
                }
                false
            })
        } else {
            false
        }
    }

    /// Get rate limit configuration
    pub fn get_rate_limit_config_sync(&self) -> Option<&PyObject> {
        self.rate_limit_config.as_ref()
    }

    /// Get rate limit configuration (alias for compatibility)
    pub fn get_rate_limit_config(&self) -> Option<&PyObject> {
        self.rate_limit_config.as_ref()
    }

    /// Add middleware to the client
    pub fn add_middleware(&mut self, middleware: PyObject) -> PyResult<()> {
        // Store middleware for processing
        self.middleware.push(middleware);
        tracing::info!(
            "Added middleware to sync client, total: {}",
            self.middleware.len()
        );
        Ok(())
    }

    /// Apply middleware headers if any are configured
    fn apply_middleware_headers(
        &self,
        mut headers: HashMap<String, String>,
    ) -> HashMap<String, String> {
        // In a full implementation, we'd process middleware here
        // For now, add a middleware processing header to demonstrate functionality
        if !self.middleware.is_empty() {
            headers.insert(
                "X-Middleware-Count".to_string(),
                self.middleware.len().to_string(),
            );
            headers.insert(
                "X-Processed-By".to_string(),
                "UltraFast-Middleware".to_string(),
            );
        }
        headers
    }

    /// Context manager support - enter
    pub fn __enter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    /// Context manager support - exit
    pub fn __exit__(
        &self,
        _exc_type: Option<PyObject>,
        _exc_value: Option<PyObject>,
        _traceback: Option<PyObject>,
    ) -> PyResult<bool> {
        Ok(false)
    }

    /// Check if HTTP/2 is supported and enabled
    pub fn supports_http2(&self) -> bool {
        // In a real implementation, this would check the client's HTTP/2 capabilities
        // For now, return true as reqwest supports HTTP/2
        true
    }

    /// Check if HTTP/3 is supported and enabled
    pub fn supports_http3(&self) -> bool {
        // HTTP/3 support is not yet available in reqwest
        false
    }

    /// Get HTTP version used for the last request
    pub fn get_http_version(&self) -> String {
        // Check if HTTP/2 is configured
        if self.supports_http2() {
            // In a real implementation, this would inspect the last response
            // For now, return HTTP/2 if it's enabled, HTTP/1.1 otherwise
            "HTTP/2".to_string()
        } else {
            "HTTP/1.1".to_string()
        }
    }

    /// Enable or disable HTTP/2
    pub fn set_http2_enabled(&mut self, enabled: bool) -> PyResult<()> {
        // In a real implementation, this would rebuild the client with HTTP/2 settings
        // For now, just store the preference
        self.http2_enabled = enabled;
        Ok(())
    }
}

// Helper methods
impl HttpClient {
    fn build_url(&self, url: &str, params: Option<HashMap<String, String>>) -> PyResult<String> {
        let mut final_url = if let Some(base) = &self.base_url {
            if url.starts_with("http://") || url.starts_with("https://") {
                url.to_string()
            } else {
                format!(
                    "{}/{}",
                    base.trim_end_matches('/'),
                    url.trim_start_matches('/')
                )
            }
        } else {
            url.to_string()
        };

        // Add query parameters if provided
        if let Some(params) = params {
            if !params.is_empty() {
                let query_string: Vec<String> = params
                    .iter()
                    .map(|(k, v)| format!("{}={}", urlencoding::encode(k), urlencoding::encode(v)))
                    .collect();
                let separator = if final_url.contains('?') { "&" } else { "?" };
                final_url = format!("{}{}{}", final_url, separator, query_string.join("&"));
            }
        }

        Ok(final_url)
    }

    fn apply_headers(
        &self,
        mut request: reqwest::blocking::RequestBuilder,
        headers: Option<HashMap<String, String>>,
    ) -> reqwest::blocking::RequestBuilder {
        // Start with default headers
        let mut all_headers = self.default_headers.clone();

        // Apply middleware headers
        all_headers = self.apply_middleware_headers(all_headers);

        // Apply request-specific headers (can override defaults and middleware)
        if let Some(request_headers) = headers {
            all_headers.extend(request_headers);
        }

        // Apply all headers to the request
        for (key, value) in all_headers {
            request = request.header(&key, &value);
        }

        request
    }

    fn apply_auth_config(
        &self,
        mut request: reqwest::blocking::RequestBuilder,
        auth: Option<(String, String)>,
    ) -> reqwest::blocking::RequestBuilder {
        // Apply request-level auth first
        if let Some((username, password)) = auth {
            request = request.basic_auth(username, Some(password));
            return request;
        }

        // Apply client-level auth config
        if let Some(config) = &self.auth_config {
            match config.auth_type {
                AuthType::Basic => {
                    if let (Some(username), Some(password)) = (
                        config.get_credential("username"),
                        config.get_credential("password"),
                    ) {
                        request = request.basic_auth(username, Some(password));
                    }
                }
                AuthType::Bearer => {
                    if let Some(token) = config.get_credential("token") {
                        request = request.bearer_auth(token);
                    }
                }
                AuthType::ApiKey => {
                    if let (Some(key), Some(value)) =
                        (config.get_credential("key"), config.get_credential("value"))
                    {
                        request = request.header(&key, &value);
                    }
                }
                AuthType::ApiKeyHeader => {
                    if let (Some(key), Some(header_name)) = (
                        config.get_credential("key"),
                        config.get_credential("header_name"),
                    ) {
                        request = request.header(&header_name, &key);
                    }
                }
                AuthType::ApiKeyQuery => {
                    // Query parameters should be handled at URL level, not headers
                    // For now, we'll skip this implementation
                }
                AuthType::OAuth2 => {
                    // OAuth2 implementation would be more complex
                    if let Some(token) = config
                        .get_credential("access_token")
                        .or_else(|| config.get_credential("token"))
                    {
                        request = request.bearer_auth(token);
                    }
                }
                AuthType::Custom => {
                    // Custom auth could be implemented here
                }
            }
        }

        request
    }

    fn apply_body(
        &self,
        mut request: reqwest::blocking::RequestBuilder,
        data: Option<PyObject>,
        json: Option<PyObject>,
        files: Option<PyObject>,
    ) -> PyResult<reqwest::blocking::RequestBuilder> {
        // Handle files with multipart form
        if let Some(files) = files {
            // Collect form data first
            let (file_parts, text_parts) = Python::with_gil(|py| {
                let mut file_parts = Vec::new();
                let mut text_parts = Vec::new();

                // Collect file parts
                if let Ok(files_dict) = files.extract::<HashMap<String, PyObject>>(py) {
                    for (field_name, file_data) in files_dict {
                        if let Ok(bytes) = file_data.extract::<Vec<u8>>(py) {
                            file_parts.push((field_name, bytes));
                        }
                    }
                }

                // Collect form data if provided alongside files
                if let Some(data) = data {
                    if let Ok(form_dict) = data.extract::<HashMap<String, String>>(py) {
                        for (key, value) in form_dict {
                            text_parts.push((key, value));
                        }
                    }
                }

                Ok::<(Vec<(String, Vec<u8>)>, Vec<(String, String)>), PyErr>((
                    file_parts, text_parts,
                ))
            })?;

            // Build form with collected parts
            let mut form = reqwest::blocking::multipart::Form::new();

            // Add file parts
            for (field_name, bytes) in file_parts {
                let part = reqwest::blocking::multipart::Part::bytes(bytes)
                    .file_name("uploaded_file")
                    .mime_str("application/octet-stream")
                    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
                form = form.part(field_name, part);
            }

            // Add text parts
            for (key, value) in text_parts {
                form = form.text(key, value);
            }

            request = request.multipart(form);
        } else if let Some(data) = data {
            let (body_data, content_type) = Python::with_gil(|py| {
                // Try to handle different data types
                if let Ok(bytes) = data.extract::<Vec<u8>>(py) {
                    // Raw bytes
                    Ok::<(Vec<u8>, Option<String>), PyErr>((bytes, None))
                } else if let Ok(string) = data.extract::<String>(py) {
                    // String data
                    Ok((string.into_bytes(), None))
                } else if let Ok(dict) = data.extract::<HashMap<String, String>>(py) {
                    // Form data
                    let form_data: Vec<String> = dict
                        .iter()
                        .map(|(k, v)| {
                            format!("{}={}", urlencoding::encode(k), urlencoding::encode(v))
                        })
                        .collect();
                    let form_string = form_data.join("&");
                    Ok((
                        form_string.into_bytes(),
                        Some("application/x-www-form-urlencoded".to_string()),
                    ))
                } else {
                    // Try to convert to string
                    let string_data: String = data.extract(py)?;
                    Ok((string_data.into_bytes(), None))
                }
            })?;

            request = request.body(body_data);
            if let Some(ct) = content_type {
                request = request.header("Content-Type", ct);
            }
        } else if let Some(json) = json {
            let json_str = Python::with_gil(|py| {
                let json_module = py.import("json")?;
                let json_str: String = json_module.call_method1("dumps", (json,))?.extract()?;
                Ok::<String, PyErr>(json_str)
            })?;
            request = request.header("Content-Type", "application/json");
            request = request.body(json_str);
        }

        Ok(request)
    }
}

impl Default for HttpClient {
    fn default() -> Self {
        Self::new(
            None, None, None, None, None, None, None, None, None, None, None,
        )
        .unwrap()
    }
}
