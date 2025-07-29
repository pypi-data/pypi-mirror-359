// Advanced connection pool implementation with health checks and statistics
use pyo3::prelude::*;
use std::collections::{HashMap, VecDeque};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};
use tracing::debug;

/// Connection state
#[derive(Debug, Clone, PartialEq)]
pub enum ConnectionState {
    Idle,
    Active,
    #[allow(dead_code)]
    Connecting,
    Unhealthy,
}

/// Connection pool statistics
#[pyclass]
#[derive(Debug, Clone, Default)]
pub struct PoolStats {
    #[pyo3(get)]
    pub total_connections_created: u64,
    #[pyo3(get)]
    pub total_connections_closed: u64,
    #[pyo3(get)]
    pub connections_reused: u64,
    #[pyo3(get)]
    pub failed_connections: u64,
    #[pyo3(get)]
    pub health_check_failures: u64,
    #[pyo3(get)]
    pub average_connection_age_ms: f64,
}

#[pymethods]
impl PoolStats {
    /// Get connection reuse rate
    pub fn reuse_rate(&self) -> f64 {
        let total_requests = self.connections_reused + self.total_connections_created;
        if total_requests == 0 {
            0.0
        } else {
            (self.connections_reused as f64 / total_requests as f64) * 100.0
        }
    }

    /// Get failure rate
    pub fn failure_rate(&self) -> f64 {
        let total_attempts = self.total_connections_created + self.failed_connections;
        if total_attempts == 0 {
            0.0
        } else {
            (self.failed_connections as f64 / total_attempts as f64) * 100.0
        }
    }

    /// Reset statistics
    pub fn reset(&mut self) {
        *self = PoolStats::default();
    }
}

/// Connection entry with enhanced tracking
#[derive(Debug, Clone)]
struct ConnectionEntry {
    connection_id: u64,
    created_at: Instant,
    last_used: Instant,
    last_health_check: Instant,
    state: ConnectionState,
    use_count: u64,
    host: String,
    port: u16,
    protocol: String,
}

impl ConnectionEntry {
    pub fn new(connection_id: u64, host: String, port: u16, protocol: String) -> Self {
        let now = Instant::now();
        ConnectionEntry {
            connection_id,
            created_at: now,
            last_used: now,
            last_health_check: now,
            state: ConnectionState::Active,
            use_count: 0,
            host,
            port,
            protocol,
        }
    }

    pub fn age(&self) -> Duration {
        Instant::now().duration_since(self.created_at)
    }

    pub fn idle_time(&self) -> Duration {
        Instant::now().duration_since(self.last_used)
    }

    pub fn mark_used(&mut self) {
        self.last_used = Instant::now();
        self.use_count += 1;
        if self.state == ConnectionState::Idle {
            self.state = ConnectionState::Active;
        }
    }

    pub fn mark_idle(&mut self) {
        self.state = ConnectionState::Idle;
    }

    pub fn needs_health_check(&self, interval: Duration) -> bool {
        Instant::now().duration_since(self.last_health_check) > interval
    }
}

/// Advanced connection pool implementation
#[pyclass]
#[derive(Debug)]
pub struct ConnectionPoolImpl {
    pub max_connections: usize,
    pub idle_timeout: Duration,
    pub health_check_interval: Duration,
    pub max_connection_age: Duration,
    connections: HashMap<String, Vec<ConnectionEntry>>,
    connection_queue: VecDeque<String>,
    stats: PoolStats,
    next_connection_id: u64,
}

#[pymethods]
impl ConnectionPoolImpl {
    #[new]
    #[pyo3(signature = (max_connections=100, idle_timeout=60.0, health_check_interval=30.0, max_connection_age=300.0))]
    pub fn new(
        max_connections: usize,
        idle_timeout: f64,
        health_check_interval: f64,
        max_connection_age: f64,
    ) -> Self {
        ConnectionPoolImpl {
            max_connections,
            idle_timeout: Duration::from_secs_f64(idle_timeout),
            health_check_interval: Duration::from_secs_f64(health_check_interval),
            max_connection_age: Duration::from_secs_f64(max_connection_age),
            connections: HashMap::new(),
            connection_queue: VecDeque::new(),
            stats: PoolStats::default(),
            next_connection_id: 1,
        }
    }

    /// Get number of active connections
    pub fn active_connections(&self) -> usize {
        self.connections
            .values()
            .flat_map(|conns| conns.iter())
            .filter(|conn| conn.state == ConnectionState::Active)
            .count()
    }

    /// Get number of idle connections
    pub fn idle_connections(&self) -> usize {
        self.connections
            .values()
            .flat_map(|conns| conns.iter())
            .filter(|conn| conn.state == ConnectionState::Idle)
            .count()
    }

    /// Get total number of connections
    pub fn total_connections(&self) -> usize {
        self.connections.values().map(|conns| conns.len()).sum()
    }

    /// Get pool utilization as percentage
    pub fn utilization(&self) -> f64 {
        if self.max_connections == 0 {
            0.0
        } else {
            (self.total_connections() as f64 / self.max_connections as f64) * 100.0
        }
    }

    /// Add connection to pool
    pub fn add_connection(&mut self, host: String, port: u16, protocol: String) -> PyResult<u64> {
        if self.total_connections() >= self.max_connections {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Connection pool is full",
            ));
        }

        let connection_id = self.next_connection_id;
        self.next_connection_id += 1;

        let key = format!("{}:{}:{}", protocol, host, port);
        let connection = ConnectionEntry::new(connection_id, host, port, protocol);

        self.connections
            .entry(key.clone())
            .or_insert_with(Vec::new)
            .push(connection);

        self.connection_queue.push_back(key);
        self.stats.total_connections_created += 1;

        Ok(connection_id)
    }

    /// Get connection from pool (reuse existing idle connection if available)
    pub fn get_connection(&mut self, host: String, port: u16, protocol: String) -> PyResult<u64> {
        let key = format!("{}:{}:{}", protocol, host, port);

        // Try to reuse existing idle connection
        if let Some(connections) = self.connections.get_mut(&key) {
            for conn in connections.iter_mut() {
                if conn.state == ConnectionState::Idle
                    && conn.idle_time() < self.idle_timeout
                    && conn.age() < self.max_connection_age
                {
                    conn.mark_used();
                    self.stats.connections_reused += 1;
                    return Ok(conn.connection_id);
                }
            }
        }

        // Create new connection if pool not full
        self.add_connection(host, port, protocol)
    }

    /// Release connection back to pool
    pub fn release_connection(&mut self, connection_id: u64) -> bool {
        for connections in self.connections.values_mut() {
            for conn in connections.iter_mut() {
                if conn.connection_id == connection_id {
                    conn.mark_idle();
                    return true;
                }
            }
        }
        false
    }

    /// Remove connection from pool
    pub fn remove_connection(&mut self, connection_id: u64) -> bool {
        let mut key_to_remove = None;
        let mut found = false;

        for (key, connections) in self.connections.iter_mut() {
            if let Some(pos) = connections
                .iter()
                .position(|conn| conn.connection_id == connection_id)
            {
                connections.remove(pos);
                found = true;

                // Mark key for removal if empty
                if connections.is_empty() {
                    key_to_remove = Some(key.clone());
                }
                break;
            }
        }

        // Remove empty entries after iteration
        if let Some(key) = key_to_remove {
            self.connections.remove(&key);
            // Remove from queue
            if let Some(queue_pos) = self.connection_queue.iter().position(|k| k == &key) {
                self.connection_queue.remove(queue_pos);
            }
        }

        if found {
            self.stats.total_connections_closed += 1;
        }

        found
    }

    /// Clean up unhealthy and expired connections
    pub fn cleanup(&mut self) {
        let _now = Instant::now();

        // In a real implementation, we would remove unhealthy/expired connections
        // For now, this is a placeholder for future implementation
        debug!("Connection pool cleanup completed");
    }

    /// Perform health checks on connections
    pub fn health_check(&mut self) -> usize {
        let mut checked_count = 0;

        for connections in self.connections.values_mut() {
            for conn in connections.iter_mut() {
                if conn.needs_health_check(self.health_check_interval) {
                    // Simulate health check (in real implementation, this would ping the server)
                    let is_healthy = conn.idle_time() < Duration::from_secs(120); // Simple heuristic

                    if is_healthy {
                        conn.last_health_check = Instant::now();
                    } else {
                        conn.state = ConnectionState::Unhealthy;
                        self.stats.health_check_failures += 1;
                    }

                    checked_count += 1;
                }
            }
        }

        checked_count
    }

    /// Get detailed connection information
    pub fn get_connection_info(&self, connection_id: u64) -> Option<HashMap<String, String>> {
        for connections in self.connections.values() {
            for conn in connections.iter() {
                if conn.connection_id == connection_id {
                    let mut info = HashMap::new();
                    info.insert("connection_id".to_string(), connection_id.to_string());
                    info.insert("host".to_string(), conn.host.clone());
                    info.insert("port".to_string(), conn.port.to_string());
                    info.insert("protocol".to_string(), conn.protocol.clone());
                    info.insert("state".to_string(), format!("{:?}", conn.state));
                    info.insert("age_ms".to_string(), conn.age().as_millis().to_string());
                    info.insert(
                        "idle_time_ms".to_string(),
                        conn.idle_time().as_millis().to_string(),
                    );
                    info.insert("use_count".to_string(), conn.use_count.to_string());
                    return Some(info);
                }
            }
        }
        None
    }

    /// Get pool statistics
    pub fn get_stats(&mut self) -> PoolStats {
        // Update average connection age
        let mut total_age_ms = 0u64;
        let mut total_connections = 0;

        for connections in self.connections.values() {
            for conn in connections.iter() {
                total_age_ms += conn.age().as_millis() as u64;
                total_connections += 1;
            }
        }

        if total_connections > 0 {
            self.stats.average_connection_age_ms = total_age_ms as f64 / total_connections as f64;
        }

        self.stats.clone()
    }

    /// Reset pool statistics
    pub fn reset_stats(&mut self) {
        self.stats.reset();
    }

    /// Get connections by host
    pub fn get_connections_for_host(&self, host: &str) -> Vec<u64> {
        let mut connection_ids = Vec::new();

        for connections in self.connections.values() {
            for conn in connections.iter() {
                if conn.host == host {
                    connection_ids.push(conn.connection_id);
                }
            }
        }

        connection_ids
    }
}

impl Default for ConnectionPoolImpl {
    fn default() -> Self {
        Self::new(100, 60.0, 30.0, 300.0)
    }
}

/// Thread-safe connection pool wrapper
#[pyclass]
#[derive(Debug, Clone)]
pub struct ThreadSafeConnectionPool {
    pool: Arc<Mutex<ConnectionPoolImpl>>,
}

#[pymethods]
impl ThreadSafeConnectionPool {
    #[new]
    #[pyo3(signature = (max_connections=100, idle_timeout=60.0, health_check_interval=30.0, max_connection_age=300.0))]
    pub fn new(
        max_connections: usize,
        idle_timeout: f64,
        health_check_interval: f64,
        max_connection_age: f64,
    ) -> Self {
        ThreadSafeConnectionPool {
            pool: Arc::new(Mutex::new(ConnectionPoolImpl::new(
                max_connections,
                idle_timeout,
                health_check_interval,
                max_connection_age,
            ))),
        }
    }

    /// Get connection (thread-safe)
    pub fn get_connection(&self, host: String, port: u16, protocol: String) -> PyResult<u64> {
        match self.pool.lock() {
            Ok(mut pool) => pool.get_connection(host, port, protocol),
            Err(_) => Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Pool lock failed",
            )),
        }
    }

    /// Release connection (thread-safe)
    pub fn release_connection(&self, connection_id: u64) -> PyResult<bool> {
        match self.pool.lock() {
            Ok(mut pool) => Ok(pool.release_connection(connection_id)),
            Err(_) => Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Pool lock failed",
            )),
        }
    }

    /// Cleanup connections in thread-safe wrapper
    pub fn cleanup_connections(&self) -> PyResult<usize> {
        match self.pool.lock() {
            Ok(mut pool) => {
                pool.cleanup();
                Ok(0) // Return 0 for now as cleanup doesn't return count
            }
            Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!(
                "Failed to lock connection pool: {}",
                e
            ))),
        }
    }

    /// Get pool statistics (thread-safe)
    pub fn get_stats(&self) -> PyResult<PoolStats> {
        match self.pool.lock() {
            Ok(mut pool) => Ok(pool.get_stats()),
            Err(_) => Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Pool lock failed",
            )),
        }
    }
}
