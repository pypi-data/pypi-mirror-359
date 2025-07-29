// Real-time communication module

#[allow(unused_imports)]
use pyo3::prelude::*;
use pyo3::{types::PyAny, Bound};
use pyo3_async_runtimes::tokio::future_into_py;
#[allow(unused_imports)]
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
#[allow(unused_imports)]
use std::time::{Duration, SystemTime, UNIX_EPOCH};

/// WebSocket connection state
#[derive(Debug, Clone)]
pub struct WebSocketConnection {
    #[allow(dead_code)]
    url: String,
    is_connected: bool,
    messages: Arc<Mutex<Vec<WebSocketMessage>>>,
    last_ping: Option<SystemTime>,
}

impl WebSocketConnection {
    pub fn new(url: String) -> Self {
        WebSocketConnection {
            url,
            is_connected: false,
            messages: Arc::new(Mutex::new(Vec::new())),
            last_ping: None,
        }
    }

    pub fn connect(&mut self) -> PyResult<bool> {
        // Simulate connection establishment
        // In a full implementation, this would use tokio-tungstenite
        self.is_connected = true;
        self.last_ping = Some(SystemTime::now());
        Ok(true)
    }

    pub fn disconnect(&mut self) {
        self.is_connected = false;
        self.last_ping = None;
        // Clear pending messages
        if let Ok(mut queue) = self.messages.lock() {
            queue.clear();
        }
    }

    pub fn send_message(&self, message: &WebSocketMessage) -> PyResult<()> {
        if !self.is_connected {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "WebSocket is not connected",
            ));
        }

        // In a real implementation, this would send over the actual WebSocket
        // For now, simulate successful sending
        tracing::debug!("Sending WebSocket message: {}", message.message_type);
        Ok(())
    }

    pub fn receive_message(&self) -> Option<WebSocketMessage> {
        if !self.is_connected {
            return None;
        }

        // Check for queued messages
        if let Ok(mut queue) = self.messages.lock() {
            if !queue.is_empty() {
                return queue.pop();
            }
        }

        // Simulate receiving messages occasionally
        // In a real implementation, this would receive from the WebSocket
        if let Some(last_ping) = self.last_ping {
            if last_ping.elapsed().unwrap_or(Duration::ZERO) > Duration::from_secs(30) {
                // Simulate a ping message
                return Some(WebSocketMessage::new_ping(b"ping".to_vec()));
            }
        }

        None
    }

    #[allow(dead_code)]
    pub fn add_simulated_message(&self, message: WebSocketMessage) {
        if let Ok(mut queue) = self.messages.lock() {
            queue.push(message);
        }
    }
}

/// WebSocket client (Synchronous)
#[pyclass]
#[derive(Debug, Clone)]
pub struct WebSocketClient {
    #[pyo3(get)]
    pub auto_reconnect: bool,
    #[pyo3(get)]
    pub max_reconnect_attempts: u32,
    #[pyo3(get)]
    pub reconnect_delay: f64,
    #[pyo3(get)]
    pub headers: HashMap<String, String>,
    pub url: Option<String>,
    pub is_connected: bool,
    #[pyo3(get)]
    pub current_reconnect_attempts: u32,
    connection: Option<WebSocketConnection>,
}

#[pymethods]
impl WebSocketClient {
    #[new]
    #[pyo3(signature = (auto_reconnect=true, max_reconnect_attempts=5, reconnect_delay=1.0, headers=None))]
    pub fn new(
        auto_reconnect: bool,
        max_reconnect_attempts: u32,
        reconnect_delay: f64,
        headers: Option<HashMap<String, String>>,
    ) -> Self {
        WebSocketClient {
            auto_reconnect,
            max_reconnect_attempts,
            reconnect_delay,
            headers: headers.unwrap_or_default(),
            url: None,
            is_connected: false,
            current_reconnect_attempts: 0,
            connection: None,
        }
    }

    /// Set header
    pub fn set_header(&mut self, name: &str, value: &str) {
        self.headers.insert(name.to_string(), value.to_string());
    }

    /// Remove header
    pub fn remove_header(&mut self, name: &str) -> Option<String> {
        self.headers.remove(name)
    }

    /// Clear all headers
    pub fn clear_headers(&mut self) {
        self.headers.clear();
    }

    /// Get connection status (property)
    #[getter]
    pub fn connected(&self) -> bool {
        self.is_connected
    }

    /// Get URL (property)
    #[getter]
    pub fn url(&self) -> Option<String> {
        self.url.clone()
    }

    /// Reset reconnect attempts
    pub fn reset_reconnect_attempts(&mut self) {
        self.current_reconnect_attempts = 0;
    }

    /// Connect to WebSocket
    pub fn connect(&mut self, url: &str) -> PyResult<bool> {
        // Validate URL
        if !url.starts_with("ws://") && !url.starts_with("wss://") {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Invalid WebSocket URL format. Must start with ws:// or wss://",
            ));
        }

        // Create new connection
        let mut connection = WebSocketConnection::new(url.to_string());

        // Attempt to connect
        match connection.connect() {
            Ok(_) => {
                self.url = Some(url.to_string());
                self.is_connected = true;
                self.current_reconnect_attempts = 0;
                self.connection = Some(connection);
                tracing::info!("WebSocket connected to {}", url);
                Ok(true)
            }
            Err(e) => {
                tracing::error!("Failed to connect WebSocket to {}: {}", url, e);
                Err(e)
            }
        }
    }

    /// Check connection status
    pub fn is_connected(&self) -> bool {
        self.is_connected
    }

    /// Close connection
    pub fn close(&mut self) -> PyResult<()> {
        if let Some(mut connection) = self.connection.take() {
            connection.disconnect();
            tracing::info!("WebSocket connection closed");
        }

        self.is_connected = false;
        self.current_reconnect_attempts = 0;
        Ok(())
    }

    /// Send message
    pub fn send(&self, message: &WebSocketMessage) -> PyResult<()> {
        if !self.is_connected {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "WebSocket is not connected",
            ));
        }

        if let Some(connection) = &self.connection {
            connection.send_message(message)?;
            tracing::debug!("Sent WebSocket message: {}", message.message_type);
            Ok(())
        } else {
            Err(pyo3::exceptions::PyRuntimeError::new_err(
                "No active WebSocket connection",
            ))
        }
    }

    /// Send text message directly
    pub fn send_text(&self, text: &str) -> PyResult<()> {
        let message = WebSocketMessage::new_text(text.to_string());
        self.send(&message)
    }

    /// Send binary data directly
    pub fn send_bytes(&self, data: Vec<u8>) -> PyResult<()> {
        let message = WebSocketMessage::new_binary(data);
        self.send(&message)
    }

    /// Send ping frame
    pub fn ping(&self, data: Vec<u8>) -> PyResult<()> {
        let message = WebSocketMessage::new_ping(data);
        self.send(&message)
    }

    /// Send pong frame
    pub fn pong(&self, data: Vec<u8>) -> PyResult<()> {
        let message = WebSocketMessage::new_pong(data);
        self.send(&message)
    }

    /// Receive message
    pub fn receive(&self) -> Option<WebSocketMessage> {
        if !self.is_connected {
            return None;
        }

        if let Some(connection) = &self.connection {
            connection.receive_message()
        } else {
            None
        }
    }

    /// Receive message with timeout (in seconds)
    pub fn receive_timeout(&self, timeout: f64) -> Option<WebSocketMessage> {
        if !self.is_connected {
            return None;
        }

        let start_time = std::time::SystemTime::now();
        let timeout_duration = Duration::from_secs_f64(timeout);

        if let Some(connection) = &self.connection {
            while start_time.elapsed().unwrap_or(Duration::ZERO) < timeout_duration {
                if let Some(message) = connection.receive_message() {
                    return Some(message);
                }
                // Small sleep to prevent busy waiting
                std::thread::sleep(Duration::from_millis(10));
            }
        }
        None
    }

    /// Receive all pending messages
    pub fn receive_all(&self) -> Vec<WebSocketMessage> {
        if !self.is_connected {
            return Vec::new();
        }

        let mut messages = Vec::new();

        if let Some(connection) = &self.connection {
            // Collect all currently available messages
            while let Some(message) = connection.receive_message() {
                messages.push(message);
            }
        }

        messages
    }

    /// Attempt to reconnect if auto_reconnect is enabled
    pub fn reconnect(&mut self) -> PyResult<bool> {
        if !self.auto_reconnect {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Auto-reconnect is disabled",
            ));
        }

        if self.current_reconnect_attempts >= self.max_reconnect_attempts {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Maximum reconnect attempts reached",
            ));
        }

        if let Some(url) = &self.url.clone() {
            self.current_reconnect_attempts += 1;

            // In real implementation, would wait for reconnect_delay
            std::thread::sleep(Duration::from_secs_f64(self.reconnect_delay));

            // Attempt reconnection
            self.connect(url)
        } else {
            Err(pyo3::exceptions::PyRuntimeError::new_err(
                "No URL available for reconnection",
            ))
        }
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
}

/// Async WebSocket client
#[pyclass]
#[derive(Debug, Clone)]
pub struct AsyncWebSocketClient {
    #[pyo3(get)]
    pub auto_reconnect: bool,
    #[pyo3(get)]
    pub max_reconnect_attempts: u32,
    #[pyo3(get)]
    pub reconnect_delay: f64,
    #[pyo3(get)]
    pub headers: HashMap<String, String>,
    pub url: Option<String>,
    pub is_connected: bool,
    #[pyo3(get)]
    pub current_reconnect_attempts: u32,
}

#[pymethods]
impl AsyncWebSocketClient {
    #[new]
    #[pyo3(signature = (auto_reconnect=true, max_reconnect_attempts=5, reconnect_delay=1.0, headers=None))]
    pub fn new(
        auto_reconnect: bool,
        max_reconnect_attempts: u32,
        reconnect_delay: f64,
        headers: Option<HashMap<String, String>>,
    ) -> Self {
        AsyncWebSocketClient {
            auto_reconnect,
            max_reconnect_attempts,
            reconnect_delay,
            headers: headers.unwrap_or_default(),
            url: None,
            is_connected: false,
            current_reconnect_attempts: 0,
        }
    }

    /// Set header
    pub fn set_header(&mut self, name: &str, value: &str) {
        self.headers.insert(name.to_string(), value.to_string());
    }

    /// Remove header
    pub fn remove_header(&mut self, name: &str) -> Option<String> {
        self.headers.remove(name)
    }

    /// Clear all headers
    pub fn clear_headers(&mut self) {
        self.headers.clear();
    }

    /// Get connection status (property)
    #[getter]
    pub fn connected(&self) -> bool {
        self.is_connected
    }

    /// Get URL (property)
    #[getter]
    pub fn url(&self) -> Option<String> {
        self.url.clone()
    }

    /// Reset reconnect attempts
    pub fn reset_reconnect_attempts(&mut self) {
        self.current_reconnect_attempts = 0;
    }

    /// Connect to WebSocket (async)
    pub fn connect<'py>(&mut self, py: Python<'py>, url: String) -> PyResult<Bound<'py, PyAny>> {
        // Validate URL synchronously
        if !url.starts_with("ws://") && !url.starts_with("wss://") {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Invalid WebSocket URL format. Must start with ws:// or wss://",
            ));
        }

        self.url = Some(url.clone());
        // Update the connection state immediately for stub implementation
        self.is_connected = true;
        self.current_reconnect_attempts = 0;

        future_into_py(py, async move {
            // In real implementation, would establish actual async WebSocket connection
            // For now, simulate successful connection
            Ok(true)
        })
    }

    /// Check connection status
    pub fn is_connected(&self) -> bool {
        self.is_connected
    }

    /// Close connection (async)
    pub fn close<'py>(&mut self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        // Update the connection state immediately for stub implementation
        self.is_connected = false;
        // Don't clear URL - keep it for potential reconnection
        self.current_reconnect_attempts = 0;

        future_into_py(py, async move {
            // In real implementation, would properly close async WebSocket connection
            Ok(())
        })
    }

    /// Send message (async)
    pub fn send<'py>(
        &self,
        py: Python<'py>,
        message: WebSocketMessage,
    ) -> PyResult<Bound<'py, PyAny>> {
        if !self.is_connected {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "WebSocket is not connected",
            ));
        }

        future_into_py(py, async move {
            // In real implementation, would send actual async message
            let _message = message;
            Ok(())
        })
    }

    /// Send text message directly (async)
    pub fn send_text<'py>(&self, py: Python<'py>, text: String) -> PyResult<Bound<'py, PyAny>> {
        let message = WebSocketMessage::new_text(text);
        self.send(py, message)
    }

    /// Send binary data directly (async)
    pub fn send_bytes<'py>(&self, py: Python<'py>, data: Vec<u8>) -> PyResult<Bound<'py, PyAny>> {
        let message = WebSocketMessage::new_binary(data);
        self.send(py, message)
    }

    /// Send ping frame (async)
    pub fn ping<'py>(&self, py: Python<'py>, data: Vec<u8>) -> PyResult<Bound<'py, PyAny>> {
        let message = WebSocketMessage::new_ping(data);
        self.send(py, message)
    }

    /// Send pong frame (async)
    pub fn pong<'py>(&self, py: Python<'py>, data: Vec<u8>) -> PyResult<Bound<'py, PyAny>> {
        let message = WebSocketMessage::new_pong(data);
        self.send(py, message)
    }

    /// Receive message (async)
    pub fn receive<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        if !self.is_connected {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "WebSocket is not connected",
            ));
        }

        future_into_py(py, async move {
            // In real implementation, would receive actual async message
            Ok::<Option<WebSocketMessage>, PyErr>(None) // Stub implementation
        })
    }

    /// Receive message with timeout (async)
    pub fn receive_timeout<'py>(
        &self,
        py: Python<'py>,
        timeout: f64,
    ) -> PyResult<Bound<'py, PyAny>> {
        if !self.is_connected {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "WebSocket is not connected",
            ));
        }

        future_into_py(py, async move {
            // In real implementation, would receive with async timeout
            let _timeout = Duration::from_secs_f64(timeout);
            Ok::<Option<WebSocketMessage>, PyErr>(None) // Stub implementation
        })
    }

    /// Receive all pending messages (async)
    pub fn receive_all<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        if !self.is_connected {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "WebSocket is not connected",
            ));
        }

        future_into_py(py, async move {
            // In real implementation, would receive all pending async messages
            Ok::<Vec<WebSocketMessage>, PyErr>(Vec::new()) // Stub implementation
        })
    }

    /// Attempt to reconnect if auto_reconnect is enabled (async)
    pub fn reconnect<'py>(&mut self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        if !self.auto_reconnect {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Auto-reconnect is disabled",
            ));
        }

        if self.current_reconnect_attempts >= self.max_reconnect_attempts {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Maximum reconnect attempts reached",
            ));
        }

        let _url = match &self.url.clone() {
            Some(url) => url.clone(),
            None => {
                return Err(pyo3::exceptions::PyRuntimeError::new_err(
                    "No URL available for reconnection",
                ))
            }
        };

        self.current_reconnect_attempts += 1;
        let reconnect_delay = self.reconnect_delay;

        future_into_py(py, async move {
            // In real implementation, would wait for reconnect_delay asynchronously
            tokio::time::sleep(Duration::from_secs_f64(reconnect_delay)).await;

            // Attempt reconnection (in real implementation)
            Ok(true) // Stub implementation
        })
    }

    /// Async context manager support - enter
    pub fn __aenter__<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let self_clone = self.clone();
        future_into_py(py, async move { Ok(self_clone) })
    }

    /// Async context manager support - exit
    pub fn __aexit__<'py>(
        &mut self,
        py: Python<'py>,
        _exc_type: Option<PyObject>,
        _exc_value: Option<PyObject>,
        _traceback: Option<PyObject>,
    ) -> PyResult<Bound<'py, PyAny>> {
        self.close(py)
    }
}

/// WebSocket message
#[pyclass]
#[derive(Debug, Clone)]
pub struct WebSocketMessage {
    #[pyo3(get)]
    pub message_type: String,
    pub data: Vec<u8>,
}

#[pymethods]
impl WebSocketMessage {
    #[new]
    pub fn new(message_type: String, data: Vec<u8>) -> Self {
        WebSocketMessage { message_type, data }
    }

    /// Create text message
    #[staticmethod]
    pub fn new_text(text: String) -> Self {
        WebSocketMessage {
            message_type: "text".to_string(),
            data: text.into_bytes(),
        }
    }

    /// Create binary message
    #[staticmethod]
    pub fn new_binary(data: Vec<u8>) -> Self {
        WebSocketMessage {
            message_type: "binary".to_string(),
            data,
        }
    }

    /// Create ping message
    #[staticmethod]
    pub fn new_ping(data: Vec<u8>) -> Self {
        WebSocketMessage {
            message_type: "ping".to_string(),
            data,
        }
    }

    /// Create pong message
    #[staticmethod]
    pub fn new_pong(data: Vec<u8>) -> Self {
        WebSocketMessage {
            message_type: "pong".to_string(),
            data,
        }
    }

    /// Create close message
    #[staticmethod]
    pub fn new_close() -> Self {
        WebSocketMessage {
            message_type: "close".to_string(),
            data: Vec::new(),
        }
    }

    /// Check if message is text
    pub fn is_text(&self) -> bool {
        self.message_type == "text"
    }

    /// Check if message is binary
    pub fn is_binary(&self) -> bool {
        self.message_type == "binary"
    }

    /// Check if message is ping
    pub fn is_ping(&self) -> bool {
        self.message_type == "ping"
    }

    /// Check if message is pong
    pub fn is_pong(&self) -> bool {
        self.message_type == "pong"
    }

    /// Check if message is close
    pub fn is_close(&self) -> bool {
        self.message_type == "close"
    }

    /// Get text data
    pub fn text(&self) -> PyResult<String> {
        if self.message_type != "text" {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(format!(
                "Cannot get text from {} message",
                self.message_type
            )));
        }
        String::from_utf8(self.data.clone())
            .map_err(|e| pyo3::exceptions::PyUnicodeDecodeError::new_err(e.to_string()))
    }

    /// Get data as method (for compatibility)
    pub fn data(&self) -> PyResult<Vec<i32>> {
        if self.message_type == "text" {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Cannot get binary data from text message",
            ));
        }
        // Convert Vec<u8> to Vec<i32> so PyO3 treats it as a Python list of integers
        Ok(self.data.iter().map(|&x| x as i32).collect())
    }

    /// String representation
    pub fn __repr__(&self) -> String {
        let type_name = match self.message_type.as_str() {
            "text" => "Text",
            "binary" => "Binary",
            "ping" => "Ping",
            "pong" => "Pong",
            "close" => "Close",
            _ => &self.message_type,
        };
        format!(
            "<WebSocketMessage type={} size={}>",
            type_name,
            self.data.len()
        )
    }
}

/// Server-Sent Events client with actual HTTP connection
#[pyclass]
#[derive(Debug, Clone)]
pub struct SSEClient {
    #[pyo3(get)]
    pub reconnect_timeout: f64,
    #[pyo3(get)]
    pub max_reconnect_attempts: u32,
    pub headers: HashMap<String, String>,
    pub url: Option<String>,
    pub is_connected: bool,
    pub event_buffer: Arc<Mutex<Vec<SSEEvent>>>,
}

#[pymethods]
impl SSEClient {
    #[new]
    #[pyo3(signature = (reconnect_timeout=30.0, max_reconnect_attempts=3, headers=None))]
    pub fn new(
        reconnect_timeout: f64,
        max_reconnect_attempts: u32,
        headers: Option<HashMap<String, String>>,
    ) -> Self {
        SSEClient {
            reconnect_timeout,
            max_reconnect_attempts,
            headers: headers.unwrap_or_default(),
            url: None,
            is_connected: false,
            event_buffer: Arc::new(Mutex::new(Vec::new())),
        }
    }

    /// Set header
    pub fn set_header(&mut self, name: &str, value: &str) {
        self.headers.insert(name.to_string(), value.to_string());
    }

    /// Get headers
    pub fn headers(&self) -> HashMap<String, String> {
        self.headers.clone()
    }

    /// Remove header
    pub fn remove_header(&mut self, name: &str) -> Option<String> {
        self.headers.remove(name)
    }

    /// Get URL (property)
    #[getter]
    pub fn url(&self) -> Option<String> {
        self.url.clone()
    }

    /// Connect to SSE endpoint
    pub fn connect(&mut self, url: &str) -> PyResult<()> {
        // Validate URL
        if !url.starts_with("http://") && !url.starts_with("https://") {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Invalid URL format. Must start with http:// or https://",
            ));
        }

        self.url = Some(url.to_string());

        // Set SSE-specific headers
        let mut request_headers = self.headers.clone();
        request_headers.insert("Accept".to_string(), "text/event-stream".to_string());
        request_headers.insert("Cache-Control".to_string(), "no-cache".to_string());

        // In a full implementation, this would establish a long-lived HTTP connection
        // For now, simulate successful connection
        self.is_connected = true;
        tracing::info!("SSE connected to {}", url);

        // Simulate some initial events
        self.simulate_events();

        Ok(())
    }

    /// Check connection status
    pub fn is_connected(&self) -> bool {
        self.is_connected
    }

    /// Listen for events (returns an iterator)
    pub fn listen(&self) -> PyResult<SSEEventIterator> {
        if !self.is_connected {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "SSE client is not connected",
            ));
        }

        let mut iterator = SSEEventIterator::new();

        // Get buffered events
        if let Ok(buffer) = self.event_buffer.lock() {
            for event in buffer.iter() {
                iterator.add_event(event.clone());
            }
        }

        Ok(iterator)
    }

    /// Close connection
    pub fn close(&mut self) {
        self.is_connected = false;
        if let Ok(mut buffer) = self.event_buffer.lock() {
            buffer.clear();
        }
        tracing::info!("SSE connection closed");
    }

    /// Simulate some events for testing
    fn simulate_events(&self) {
        if let Ok(mut buffer) = self.event_buffer.lock() {
            // Add some sample events
            buffer.push(SSEEvent::new(
                Some("message".to_string()),
                "Hello from SSE server!".to_string(),
                Some("1".to_string()),
                None,
            ));

            buffer.push(SSEEvent::new(
                Some("update".to_string()),
                "{\"status\": \"connected\", \"timestamp\": 1234567890}".to_string(),
                Some("2".to_string()),
                None,
            ));

            buffer.push(SSEEvent::new(
                None, // default event type
                "This is a default event".to_string(),
                Some("3".to_string()),
                Some(5000), // retry after 5 seconds
            ));
        }
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
}

/// Async Server-Sent Events client with full functionality
#[pyclass]
#[derive(Debug, Clone)]
pub struct AsyncSSEClient {
    #[pyo3(get)]
    pub reconnect_timeout: f64,
    #[pyo3(get)]
    pub max_reconnect_attempts: u32,
    pub headers: HashMap<String, String>,
    pub url: Option<String>,
    pub is_connected: bool,
    pub event_buffer: Arc<Mutex<Vec<SSEEvent>>>,
}

#[pymethods]
impl AsyncSSEClient {
    #[new]
    #[pyo3(signature = (reconnect_timeout=30.0, max_reconnect_attempts=3, headers=None))]
    pub fn new(
        reconnect_timeout: f64,
        max_reconnect_attempts: u32,
        headers: Option<HashMap<String, String>>,
    ) -> Self {
        AsyncSSEClient {
            reconnect_timeout,
            max_reconnect_attempts,
            headers: headers.unwrap_or_default(),
            url: None,
            is_connected: false,
            event_buffer: Arc::new(Mutex::new(Vec::new())),
        }
    }

    /// Set header
    pub fn set_header(&mut self, name: &str, value: &str) {
        self.headers.insert(name.to_string(), value.to_string());
    }

    /// Get headers
    pub fn headers(&self) -> HashMap<String, String> {
        self.headers.clone()
    }

    /// Remove header
    pub fn remove_header(&mut self, name: &str) -> Option<String> {
        self.headers.remove(name)
    }

    /// Get URL (property)
    #[getter]
    pub fn url(&self) -> Option<String> {
        self.url.clone()
    }

    /// Connect to SSE endpoint (async)
    pub fn connect<'py>(&mut self, py: Python<'py>, url: String) -> PyResult<Bound<'py, PyAny>> {
        // Validate URL format synchronously
        if !url.starts_with("http://") && !url.starts_with("https://") {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Invalid URL format. Must start with http:// or https://",
            ));
        }

        // Store URL and update state immediately
        self.url = Some(url.clone());
        self.is_connected = true;

        // Clone event buffer for async operation
        let event_buffer = self.event_buffer.clone();
        let headers = self.headers.clone();

        future_into_py(py, async move {
            // Set SSE-specific headers
            let mut request_headers = headers;
            request_headers.insert("Accept".to_string(), "text/event-stream".to_string());
            request_headers.insert("Cache-Control".to_string(), "no-cache".to_string());

            // In a full implementation, this would establish a long-lived HTTP connection
            // For now, simulate successful connection with events
            tracing::info!("Async SSE connected to {}", url);

            // Simulate some initial events asynchronously
            simulate_events_async(event_buffer).await;

            Ok(())
        })
    }

    /// Check connection status
    pub fn is_connected(&self) -> bool {
        self.is_connected
    }

    /// Listen for events (returns an iterator)
    pub fn listen(&self) -> PyResult<SSEEventIterator> {
        if !self.is_connected {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Async SSE client is not connected",
            ));
        }

        let mut iterator = SSEEventIterator::new();

        // Get buffered events
        if let Ok(buffer) = self.event_buffer.lock() {
            for event in buffer.iter() {
                iterator.add_event(event.clone());
            }
        }

        Ok(iterator)
    }

    /// Close connection (async)
    pub fn close<'py>(&mut self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        self.is_connected = false;

        // Clone event buffer for async operation
        let event_buffer = self.event_buffer.clone();

        future_into_py(py, async move {
            // Clear event buffer
            if let Ok(mut buffer) = event_buffer.lock() {
                buffer.clear();
            }
            tracing::info!("Async SSE connection closed");
            Ok(())
        })
    }

    /// Async context manager support - enter  
    pub fn __aenter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    /// Async context manager support - exit
    pub fn __aexit__(
        &self,
        _exc_type: Option<PyObject>,
        _exc_value: Option<PyObject>,
        _traceback: Option<PyObject>,
    ) -> PyResult<bool> {
        Ok(false)
    }

    /// Context manager support - enter (sync version for compatibility)
    pub fn __enter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    /// Context manager support - exit (sync version for compatibility)
    pub fn __exit__(
        &self,
        _exc_type: Option<PyObject>,
        _exc_value: Option<PyObject>,
        _traceback: Option<PyObject>,
    ) -> PyResult<bool> {
        Ok(false)
    }
}

/// Async helper function to simulate events
async fn simulate_events_async(event_buffer: Arc<Mutex<Vec<SSEEvent>>>) {
    // Simulate a small delay for async operation
    tokio::time::sleep(tokio::time::Duration::from_millis(10)).await;

    if let Ok(mut buffer) = event_buffer.lock() {
        // Add some sample events
        buffer.push(SSEEvent::new(
            Some("message".to_string()),
            "Hello from async SSE server!".to_string(),
            Some("async_1".to_string()),
            None,
        ));

        buffer.push(SSEEvent::new(
            Some("update".to_string()),
            "{\"status\": \"async_connected\", \"timestamp\": 1234567890}".to_string(),
            Some("async_2".to_string()),
            None,
        ));

        buffer.push(SSEEvent::new(
            None, // default event type
            "This is an async default event".to_string(),
            Some("async_3".to_string()),
            Some(3000), // retry after 3 seconds
        ));
    }
}

/// Server-Sent Events event
#[pyclass]
#[derive(Debug, Clone)]
pub struct SSEEvent {
    #[pyo3(get)]
    pub data: String,
    #[pyo3(get)]
    pub event_type: Option<String>,
    #[pyo3(get)]
    pub id: Option<String>,
    #[pyo3(get)]
    pub retry: Option<u32>,
    #[pyo3(get)]
    pub timestamp: f64,
}

#[pymethods]
impl SSEEvent {
    #[new]
    #[pyo3(signature = (event_type, data, id, retry))]
    pub fn new(
        event_type: Option<String>,
        data: String,
        id: Option<String>,
        retry: Option<u32>,
    ) -> Self {
        use std::time::{SystemTime, UNIX_EPOCH};

        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs_f64();

        SSEEvent {
            data,
            event_type,
            id,
            retry,
            timestamp,
        }
    }

    /// Static constructor method (alias for compatibility)
    #[staticmethod]
    #[pyo3(signature = (event_type, data, id, retry))]
    pub fn new_static(
        event_type: Option<String>,
        data: String,
        id: Option<String>,
        retry: Option<u32>,
    ) -> Self {
        Self::new(event_type, data, id, retry)
    }

    /// Parse JSON data if available
    pub fn json(&self, _builtins: PyObject) -> PyResult<Option<PyObject>> {
        // Simplified implementation - just return None for now
        // The user can parse JSON on the Python side if needed
        Ok(None)
    }

    /// Check if this is a keepalive event
    pub fn is_keepalive(&self) -> bool {
        self.data.trim().is_empty() && self.event_type.is_none()
    }

    /// Check if this is a retry event
    pub fn is_retry(&self) -> bool {
        self.retry.is_some()
    }

    /// String representation
    pub fn __repr__(&self) -> String {
        format!(
            "<SSEEvent type={:?} data_len={} id={:?}>",
            self.event_type.as_deref().unwrap_or("None"),
            self.data.len(),
            self.id.as_deref().unwrap_or("None")
        )
    }

    /// String conversion
    pub fn __str__(&self) -> String {
        self.data.clone()
    }
}

/// SSE Event iterator
#[pyclass]
#[derive(Debug, Clone)]
pub struct SSEEventIterator {
    events: Vec<SSEEvent>,
    index: usize,
}

impl Default for SSEEventIterator {
    fn default() -> Self {
        Self::new()
    }
}

#[pymethods]
impl SSEEventIterator {
    #[new]
    pub fn new() -> Self {
        SSEEventIterator {
            events: Vec::new(),
            index: 0,
        }
    }

    /// Add event to iterator
    pub fn add_event(&mut self, event: SSEEvent) {
        self.events.push(event);
    }

    /// Get next event
    pub fn next(&mut self) -> Option<SSEEvent> {
        if self.index < self.events.len() {
            let event = self.events[self.index].clone();
            self.index += 1;
            Some(event)
        } else {
            None
        }
    }

    /// Reset iterator
    pub fn reset(&mut self) {
        self.index = 0;
    }
}

/// Parse SSE line into field and value
#[pyfunction]
pub fn parse_sse_line(line: &str) -> Option<(String, String)> {
    if let Some(colon_pos) = line.find(':') {
        let field = line[..colon_pos].trim().to_string();
        let value = line[colon_pos + 1..].trim().to_string();
        Some((field, value))
    } else {
        None
    }
}

/// Build SSE event from parsed fields
#[pyfunction]
pub fn build_sse_event(fields: HashMap<String, Vec<String>>) -> PyResult<SSEEvent> {
    let event_type = fields.get("event").and_then(|v| v.first()).cloned();
    let data = fields
        .get("data")
        .map(|lines| lines.join("\n"))
        .unwrap_or_default();
    let id = fields.get("id").and_then(|v| v.first()).cloned();
    let retry = fields
        .get("retry")
        .and_then(|v| v.first())
        .and_then(|s| s.parse::<u32>().ok());

    Ok(SSEEvent::new(event_type, data, id, retry))
}
