// Performance statistics
use pyo3::prelude::*;
use std::collections::HashMap;
use std::time::{Duration, Instant};

/// Performance statistics collector
#[pyclass]
#[derive(Debug)]
pub struct PerformanceStats {
    request_count: u64,
    total_response_time: Duration,
    min_response_time: Option<Duration>,
    max_response_time: Option<Duration>,
    error_count: u64,
    bytes_sent: u64,
    bytes_received: u64,
    start_time: Instant,
    host_stats: HashMap<String, HostStats>,
}

#[derive(Debug, Clone)]
struct HostStats {
    request_count: u64,
    total_response_time: Duration,
    error_count: u64,
}

#[pymethods]
impl PerformanceStats {
    #[new]
    pub fn new() -> Self {
        PerformanceStats {
            request_count: 0,
            total_response_time: Duration::ZERO,
            min_response_time: None,
            max_response_time: None,
            error_count: 0,
            bytes_sent: 0,
            bytes_received: 0,
            start_time: Instant::now(),
            host_stats: HashMap::new(),
        }
    }

    /// Record a request
    #[pyo3(signature = (host, response_time, success, bytes_sent, bytes_received))]
    pub fn record_request(
        &mut self,
        host: Option<String>,
        response_time: f64,
        success: bool,
        bytes_sent: u64,
        bytes_received: u64,
    ) {
        let response_time = Duration::from_secs_f64(response_time);

        self.request_count += 1;
        self.total_response_time += response_time;
        self.bytes_sent += bytes_sent;
        self.bytes_received += bytes_received;

        // Update min/max response times
        if let Some(min) = self.min_response_time {
            if response_time < min {
                self.min_response_time = Some(response_time);
            }
        } else {
            self.min_response_time = Some(response_time);
        }

        if let Some(max) = self.max_response_time {
            if response_time > max {
                self.max_response_time = Some(response_time);
            }
        } else {
            self.max_response_time = Some(response_time);
        }

        if !success {
            self.error_count += 1;
        }

        // Update host-specific stats
        if let Some(host) = host {
            let host_stat = self.host_stats.entry(host).or_insert(HostStats {
                request_count: 0,
                total_response_time: Duration::ZERO,
                error_count: 0,
            });

            host_stat.request_count += 1;
            host_stat.total_response_time += response_time;
            if !success {
                host_stat.error_count += 1;
            }
        }
    }

    /// Get total request count
    pub fn total_requests(&self) -> u64 {
        self.request_count
    }

    /// Get average response time in seconds
    pub fn average_response_time(&self) -> f64 {
        if self.request_count > 0 {
            self.total_response_time.as_secs_f64() / self.request_count as f64
        } else {
            0.0
        }
    }

    /// Get minimum response time in seconds
    pub fn min_response_time(&self) -> Option<f64> {
        self.min_response_time.map(|d| d.as_secs_f64())
    }

    /// Get maximum response time in seconds
    pub fn max_response_time(&self) -> Option<f64> {
        self.max_response_time.map(|d| d.as_secs_f64())
    }

    /// Get error rate (0.0 to 1.0)
    pub fn error_rate(&self) -> f64 {
        if self.request_count > 0 {
            self.error_count as f64 / self.request_count as f64
        } else {
            0.0
        }
    }

    /// Get total bytes sent
    pub fn total_bytes_sent(&self) -> u64 {
        self.bytes_sent
    }

    /// Get total bytes received
    pub fn total_bytes_received(&self) -> u64 {
        self.bytes_received
    }

    /// Get requests per second
    pub fn requests_per_second(&self) -> f64 {
        let elapsed = self.start_time.elapsed().as_secs_f64();
        if elapsed > 0.0 {
            self.request_count as f64 / elapsed
        } else {
            0.0
        }
    }

    /// Get summary as dictionary
    pub fn summary(&self) -> HashMap<String, f64> {
        let mut summary = HashMap::new();
        summary.insert("total_requests".to_string(), self.request_count as f64);
        summary.insert(
            "average_response_time".to_string(),
            self.average_response_time(),
        );
        summary.insert("error_rate".to_string(), self.error_rate());
        summary.insert("bytes_sent".to_string(), self.bytes_sent as f64);
        summary.insert("bytes_received".to_string(), self.bytes_received as f64);
        summary.insert(
            "requests_per_second".to_string(),
            self.requests_per_second(),
        );

        if let Some(min) = self.min_response_time() {
            summary.insert("min_response_time".to_string(), min);
        }

        if let Some(max) = self.max_response_time() {
            summary.insert("max_response_time".to_string(), max);
        }

        summary
    }

    /// Reset all statistics
    pub fn reset(&mut self) {
        *self = Self::new();
    }
}

impl Default for PerformanceStats {
    fn default() -> Self {
        Self::new()
    }
}
