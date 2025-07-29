// Session management for HTTP clients
use crate::config::{AuthConfig, PoolConfig, RetryConfig, SSLConfig, TimeoutConfig};
use crate::core::response::ClientResponse;
use pyo3::prelude::*;
use pyo3::{types::PyAny, Bound};
use pyo3_async_runtimes::tokio::future_into_py;
use std::collections::HashMap;

/// Synchronous HTTP session with persistent cookies and configuration
#[pyclass]
#[derive(Debug)]
pub struct Session {
    base_url: Option<String>,
    headers: HashMap<String, String>,
    auth_config: Option<AuthConfig>,
    persist_cookies: bool,
    client: reqwest::blocking::Client,
    auth: Option<(String, String)>,
    timeout_config: Option<TimeoutConfig>,
    session_data: HashMap<String, PyObject>,
}

#[pymethods]
impl Session {
    #[new]
    #[pyo3(signature = (base_url=None, auth_config=None, headers=None, timeout_config=None, pool_config=None, ssl_config=None, retry_config=None, persist_cookies=true))]
    pub fn new(
        base_url: Option<String>,
        auth_config: Option<AuthConfig>,
        headers: Option<HashMap<String, String>>,
        timeout_config: Option<TimeoutConfig>,
        pool_config: Option<PoolConfig>,
        ssl_config: Option<SSLConfig>,
        retry_config: Option<RetryConfig>,
        persist_cookies: bool,
    ) -> PyResult<Self> {
        let _pool_config = pool_config;
        let _ssl_config = ssl_config;
        let _retry_config = retry_config;

        let mut client_builder = reqwest::blocking::Client::builder();

        // Enable cookie store if persist_cookies is true
        if persist_cookies {
            client_builder = client_builder.cookie_store(true);
        }

        let client = client_builder
            .build()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        Ok(Session {
            base_url,
            headers: headers.unwrap_or_default(),
            auth_config,
            persist_cookies,
            client,
            auth: None,
            timeout_config,
            session_data: HashMap::new(),
        })
    }

    /// Base URL property
    #[getter]
    pub fn base_url(&self) -> Option<String> {
        self.base_url.clone()
    }

    /// Set base URL
    pub fn set_base_url(&mut self, base_url: Option<String>) {
        self.base_url = base_url;
    }

    /// Headers property
    #[getter]
    pub fn headers(&self) -> HashMap<String, String> {
        self.headers.clone()
    }

    /// Session headers property (alias for headers)
    #[getter]
    pub fn session_headers(&self) -> HashMap<String, String> {
        self.headers.clone()
    }

    /// Set session header
    pub fn set_header(&mut self, name: &str, value: &str) {
        self.headers.insert(name.to_string(), value.to_string());
    }

    /// Remove session header
    pub fn remove_header(&mut self, name: &str) -> Option<String> {
        self.headers.remove(name)
    }

    /// Auth config property
    #[getter]
    pub fn auth_config(&self) -> Option<AuthConfig> {
        self.auth_config.clone()
    }

    /// Set authentication
    pub fn set_auth(&mut self, username: &str, password: &str) {
        self.auth = Some((username.to_string(), password.to_string()));
    }

    /// Persist cookies property
    #[getter]
    pub fn persist_cookies(&self) -> bool {
        self.persist_cookies
    }

    /// Timeout config property
    #[getter]
    pub fn timeout_config(&self) -> Option<TimeoutConfig> {
        self.timeout_config.clone()
    }

    /// Set authentication config
    pub fn set_auth_config(&mut self, auth_config: Option<AuthConfig>) {
        self.auth_config = auth_config;
    }

    /// Set session data
    pub fn set_data(&mut self, key: &str, value: PyObject) {
        self.session_data.insert(key.to_string(), value);
    }

    /// Get session data
    pub fn get_data(&self, key: &str) -> Option<&PyObject> {
        self.session_data.get(key)
    }

    /// Remove session data
    pub fn remove_data(&mut self, key: &str) -> Option<PyObject> {
        self.session_data.remove(key)
    }

    /// Clear all session data
    pub fn clear_data(&mut self) {
        self.session_data.clear();
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

    /// Perform a GET request
    #[pyo3(signature = (url, params=None, headers=None, auth=None, timeout=None))]
    pub fn get(
        &self,
        url: &str,
        params: Option<HashMap<String, String>>,
        headers: Option<HashMap<String, String>>,
        auth: Option<(String, String)>,
        timeout: Option<f64>,
    ) -> PyResult<ClientResponse> {
        let final_url = self.build_url(url, params)?;
        let mut request = self.client.get(final_url);

        request = self.apply_headers(request, headers);
        request = self.apply_auth(request, auth);

        if let Some(timeout) = timeout {
            request = request.timeout(std::time::Duration::from_secs_f64(timeout));
        }

        let response = request
            .send()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        ClientResponse::from_reqwest_blocking(response)
    }

    /// Perform a POST request
    #[pyo3(signature = (url, data=None, json=None, files=None, headers=None, auth=None, timeout=None))]
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
        let final_url = self.build_url(url, None)?;
        let mut request = self.client.post(final_url);

        request = self.apply_body(request, data, json, files)?;
        request = self.apply_headers(request, headers);
        request = self.apply_auth(request, auth);

        if let Some(timeout) = timeout {
            request = request.timeout(std::time::Duration::from_secs_f64(timeout));
        }

        let response = request
            .send()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

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
        request = self.apply_auth(request, auth);

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
        request = self.apply_auth(request, auth);

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
        request = self.apply_auth(request, auth);

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
        request = self.apply_auth(request, auth);

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
        request = self.apply_auth(request, auth);

        if let Some(timeout) = timeout {
            request = request.timeout(std::time::Duration::from_secs_f64(timeout));
        }

        let response = request
            .send()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        ClientResponse::from_reqwest_blocking(response)
    }
}

// Helper methods for Session
impl Session {
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
        // Apply session headers first
        for (key, value) in &self.headers {
            request = request.header(key, value);
        }

        // Apply request-specific headers (can override session headers)
        if let Some(headers) = headers {
            for (key, value) in headers {
                request = request.header(&key, &value);
            }
        }

        request
    }

    fn apply_auth(
        &self,
        mut request: reqwest::blocking::RequestBuilder,
        auth: Option<(String, String)>,
    ) -> reqwest::blocking::RequestBuilder {
        // Use provided auth or fall back to session auth
        let auth_to_use = auth.or_else(|| self.auth.clone());

        if let Some((username, password)) = auth_to_use {
            request = request.basic_auth(username, Some(password));
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

/// Asynchronous HTTP session with persistent cookies and configuration
#[pyclass]
#[derive(Debug)]
pub struct AsyncSession {
    base_url: Option<String>,
    headers: HashMap<String, String>,
    auth_config: Option<AuthConfig>,
    persist_cookies: bool,
    client: reqwest::Client,
    auth: Option<(String, String)>,
    timeout_config: Option<TimeoutConfig>,
    session_data: HashMap<String, PyObject>,
}

#[pymethods]
impl AsyncSession {
    #[new]
    #[pyo3(signature = (base_url=None, auth_config=None, headers=None, timeout_config=None, pool_config=None, ssl_config=None, retry_config=None, persist_cookies=true))]
    pub fn new(
        base_url: Option<String>,
        auth_config: Option<AuthConfig>,
        headers: Option<HashMap<String, String>>,
        timeout_config: Option<TimeoutConfig>,
        pool_config: Option<PoolConfig>,
        ssl_config: Option<SSLConfig>,
        retry_config: Option<RetryConfig>,
        persist_cookies: bool,
    ) -> PyResult<Self> {
        let _pool_config = pool_config;
        let _ssl_config = ssl_config;
        let _retry_config = retry_config;

        let mut client_builder = reqwest::Client::builder();

        // Enable cookie store if persist_cookies is true
        if persist_cookies {
            client_builder = client_builder.cookie_store(true);
        }

        let client = client_builder
            .build()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        Ok(AsyncSession {
            base_url,
            headers: headers.unwrap_or_default(),
            auth_config,
            persist_cookies,
            client,
            auth: None,
            timeout_config,
            session_data: HashMap::new(),
        })
    }

    /// Base URL property
    #[getter]
    pub fn base_url(&self) -> Option<String> {
        self.base_url.clone()
    }

    /// Set base URL
    pub fn set_base_url(&mut self, base_url: Option<String>) {
        self.base_url = base_url;
    }

    /// Headers property
    #[getter]
    pub fn headers(&self) -> HashMap<String, String> {
        self.headers.clone()
    }

    /// Session headers property (alias for headers)
    #[getter]
    pub fn session_headers(&self) -> HashMap<String, String> {
        self.headers.clone()
    }

    /// Set session header
    pub fn set_header(&mut self, name: &str, value: &str) {
        self.headers.insert(name.to_string(), value.to_string());
    }

    /// Remove session header
    pub fn remove_header(&mut self, name: &str) -> Option<String> {
        self.headers.remove(name)
    }

    /// Auth config property
    #[getter]
    pub fn auth_config(&self) -> Option<AuthConfig> {
        self.auth_config.clone()
    }

    /// Set authentication
    pub fn set_auth(&mut self, username: &str, password: &str) {
        self.auth = Some((username.to_string(), password.to_string()));
    }

    /// Persist cookies property
    #[getter]
    pub fn persist_cookies(&self) -> bool {
        self.persist_cookies
    }

    /// Timeout config property
    #[getter]
    pub fn timeout_config(&self) -> Option<TimeoutConfig> {
        self.timeout_config.clone()
    }

    /// Set authentication config
    pub fn set_auth_config(&mut self, auth_config: Option<AuthConfig>) {
        self.auth_config = auth_config;
    }

    /// Set session data
    pub fn set_data(&mut self, key: &str, value: PyObject) {
        self.session_data.insert(key.to_string(), value);
    }

    /// Get session data
    pub fn get_data(&self, key: &str) -> Option<&PyObject> {
        self.session_data.get(key)
    }

    /// Remove session data
    pub fn remove_data(&mut self, key: &str) -> Option<PyObject> {
        self.session_data.remove(key)
    }

    /// Clear all session data
    pub fn clear_data(&mut self) {
        self.session_data.clear();
    }

    /// Context manager support - enter
    pub fn __aenter__<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        // Return a future that resolves immediately
        future_into_py(py, async move {
            // In async context managers, we typically return a value that represents the resource
            // For now, we'll return a success indicator
            Ok(true)
        })
    }

    /// Context manager support - exit
    pub fn __aexit__<'py>(
        &self,
        py: Python<'py>,
        _exc_type: Option<PyObject>,
        _exc_value: Option<PyObject>,
        _traceback: Option<PyObject>,
    ) -> PyResult<Bound<'py, PyAny>> {
        // Return a future that resolves to False
        future_into_py(py, async move { Ok(false) })
    }

    /// Perform an async GET request
    #[pyo3(signature = (url, params=None, headers=None, auth=None, timeout=None))]
    pub fn get<'py>(
        &self,
        py: Python<'py>,
        url: String,
        params: Option<HashMap<String, String>>,
        headers: Option<HashMap<String, String>>,
        auth: Option<(String, String)>,
        timeout: Option<f64>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let base_url = self.base_url.clone();
        let session_headers = self.headers.clone();
        let session_auth = self.auth.clone();
        let client = self.client.clone();

        future_into_py(py, async move {
            let final_url = Self::build_url_async(&base_url, &url, params)?;
            let mut request = client.get(final_url);

            request = Self::apply_headers_async(request, &session_headers, headers);
            request = Self::apply_auth_async(request, auth.or(session_auth));

            if let Some(timeout) = timeout {
                request = request.timeout(std::time::Duration::from_secs_f64(timeout));
            }

            let response = request
                .send()
                .await
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

            ClientResponse::from_reqwest_async(response).await
        })
    }

    /// Perform an async POST request
    #[pyo3(signature = (url, data=None, json=None, files=None, headers=None, auth=None, timeout=None))]
    pub fn post<'py>(
        &self,
        py: Python<'py>,
        url: String,
        data: Option<PyObject>,
        json: Option<PyObject>,
        files: Option<PyObject>,
        headers: Option<HashMap<String, String>>,
        auth: Option<(String, String)>,
        timeout: Option<f64>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let base_url = self.base_url.clone();
        let session_headers = self.headers.clone();
        let session_auth = self.auth.clone();
        let client = self.client.clone();

        future_into_py(py, async move {
            let final_url = Self::build_url_async(&base_url, &url, None)?;
            let mut request = client.post(final_url);

            request = Self::apply_body_async(request, data, json, files).await?;
            request = Self::apply_headers_async(request, &session_headers, headers);
            request = Self::apply_auth_async(request, auth.or(session_auth));

            if let Some(timeout) = timeout {
                request = request.timeout(std::time::Duration::from_secs_f64(timeout));
            }

            let response = request
                .send()
                .await
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

            ClientResponse::from_reqwest_async(response).await
        })
    }

    /// Perform an async PUT request
    #[pyo3(signature = (url, data=None, json=None, files=None, headers=None, auth=None, timeout=None))]
    pub fn put<'py>(
        &self,
        py: Python<'py>,
        url: String,
        data: Option<PyObject>,
        json: Option<PyObject>,
        files: Option<PyObject>,
        headers: Option<HashMap<String, String>>,
        auth: Option<(String, String)>,
        timeout: Option<f64>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let base_url = self.base_url.clone();
        let session_headers = self.headers.clone();
        let session_auth = self.auth.clone();
        let client = self.client.clone();

        future_into_py(py, async move {
            let final_url = Self::build_url_async(&base_url, &url, None)?;
            let mut request = client.put(final_url);

            request = Self::apply_body_async(request, data, json, files).await?;
            request = Self::apply_headers_async(request, &session_headers, headers);
            request = Self::apply_auth_async(request, auth.or(session_auth));

            if let Some(timeout) = timeout {
                request = request.timeout(std::time::Duration::from_secs_f64(timeout));
            }

            let response = request
                .send()
                .await
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

            ClientResponse::from_reqwest_async(response).await
        })
    }

    /// Perform an async PATCH request
    #[pyo3(signature = (url, data=None, json=None, files=None, headers=None, auth=None, timeout=None))]
    pub fn patch<'py>(
        &self,
        py: Python<'py>,
        url: String,
        data: Option<PyObject>,
        json: Option<PyObject>,
        files: Option<PyObject>,
        headers: Option<HashMap<String, String>>,
        auth: Option<(String, String)>,
        timeout: Option<f64>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let base_url = self.base_url.clone();
        let session_headers = self.headers.clone();
        let session_auth = self.auth.clone();
        let client = self.client.clone();

        future_into_py(py, async move {
            let final_url = Self::build_url_async(&base_url, &url, None)?;
            let mut request = client.patch(final_url);

            request = Self::apply_body_async(request, data, json, files).await?;
            request = Self::apply_headers_async(request, &session_headers, headers);
            request = Self::apply_auth_async(request, auth.or(session_auth));

            if let Some(timeout) = timeout {
                request = request.timeout(std::time::Duration::from_secs_f64(timeout));
            }

            let response = request
                .send()
                .await
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

            ClientResponse::from_reqwest_async(response).await
        })
    }

    /// Perform an async DELETE request
    #[pyo3(signature = (url, headers=None, auth=None, timeout=None))]
    pub fn delete<'py>(
        &self,
        py: Python<'py>,
        url: String,
        headers: Option<HashMap<String, String>>,
        auth: Option<(String, String)>,
        timeout: Option<f64>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let base_url = self.base_url.clone();
        let session_headers = self.headers.clone();
        let session_auth = self.auth.clone();
        let client = self.client.clone();

        future_into_py(py, async move {
            let final_url = Self::build_url_async(&base_url, &url, None)?;
            let mut request = client.delete(final_url);

            request = Self::apply_headers_async(request, &session_headers, headers);
            request = Self::apply_auth_async(request, auth.or(session_auth));

            if let Some(timeout) = timeout {
                request = request.timeout(std::time::Duration::from_secs_f64(timeout));
            }

            let response = request
                .send()
                .await
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

            ClientResponse::from_reqwest_async(response).await
        })
    }

    /// Perform an async HEAD request
    #[pyo3(signature = (url, headers=None, auth=None, timeout=None))]
    pub fn head<'py>(
        &self,
        py: Python<'py>,
        url: String,
        headers: Option<HashMap<String, String>>,
        auth: Option<(String, String)>,
        timeout: Option<f64>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let base_url = self.base_url.clone();
        let session_headers = self.headers.clone();
        let session_auth = self.auth.clone();
        let client = self.client.clone();

        future_into_py(py, async move {
            let final_url = Self::build_url_async(&base_url, &url, None)?;
            let mut request = client.head(final_url);

            request = Self::apply_headers_async(request, &session_headers, headers);
            request = Self::apply_auth_async(request, auth.or(session_auth));

            if let Some(timeout) = timeout {
                request = request.timeout(std::time::Duration::from_secs_f64(timeout));
            }

            let response = request
                .send()
                .await
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

            ClientResponse::from_reqwest_async(response).await
        })
    }

    /// Perform an async OPTIONS request
    #[pyo3(signature = (url, headers=None, auth=None, timeout=None))]
    pub fn options<'py>(
        &self,
        py: Python<'py>,
        url: String,
        headers: Option<HashMap<String, String>>,
        auth: Option<(String, String)>,
        timeout: Option<f64>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let base_url = self.base_url.clone();
        let session_headers = self.headers.clone();
        let session_auth = self.auth.clone();
        let client = self.client.clone();

        future_into_py(py, async move {
            let final_url = Self::build_url_async(&base_url, &url, None)?;
            let mut request = client.request(reqwest::Method::OPTIONS, final_url);

            request = Self::apply_headers_async(request, &session_headers, headers);
            request = Self::apply_auth_async(request, auth.or(session_auth));

            if let Some(timeout) = timeout {
                request = request.timeout(std::time::Duration::from_secs_f64(timeout));
            }

            let response = request
                .send()
                .await
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

            ClientResponse::from_reqwest_async(response).await
        })
    }
}

// Helper methods for AsyncSession
impl AsyncSession {
    fn build_url_async(
        base_url: &Option<String>,
        url: &str,
        params: Option<HashMap<String, String>>,
    ) -> PyResult<String> {
        let mut final_url = if let Some(base) = base_url {
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

    fn apply_headers_async(
        mut request: reqwest::RequestBuilder,
        session_headers: &HashMap<String, String>,
        headers: Option<HashMap<String, String>>,
    ) -> reqwest::RequestBuilder {
        // Apply session headers first
        for (key, value) in session_headers {
            request = request.header(key, value);
        }

        // Apply request-specific headers (can override session headers)
        if let Some(headers) = headers {
            for (key, value) in headers {
                request = request.header(&key, &value);
            }
        }

        request
    }

    fn apply_auth_async(
        mut request: reqwest::RequestBuilder,
        auth: Option<(String, String)>,
    ) -> reqwest::RequestBuilder {
        if let Some((username, password)) = auth {
            request = request.basic_auth(username, Some(password));
        }

        request
    }

    async fn apply_body_async(
        mut request: reqwest::RequestBuilder,
        data: Option<PyObject>,
        json: Option<PyObject>,
        files: Option<PyObject>,
    ) -> PyResult<reqwest::RequestBuilder> {
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
            let mut form = reqwest::multipart::Form::new();

            // Add file parts
            for (field_name, bytes) in file_parts {
                let part = reqwest::multipart::Part::bytes(bytes)
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
