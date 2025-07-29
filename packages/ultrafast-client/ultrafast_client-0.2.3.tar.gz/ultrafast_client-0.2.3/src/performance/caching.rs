// Advanced caching implementation with LRU and statistics
use pyo3::prelude::*;
use std::collections::{HashMap, VecDeque};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

/// Cache entry with expiration and access tracking
#[derive(Debug, Clone)]
struct CacheEntry<T> {
    value: T,
    #[allow(dead_code)]
    created_at: Instant,
    expires_at: Option<Instant>,
    last_accessed: Instant,
    access_count: u64,
}

/// Cache statistics
#[pyclass]
#[derive(Debug, Clone, Default)]
pub struct CacheStats {
    #[pyo3(get)]
    pub hits: u64,
    #[pyo3(get)]
    pub misses: u64,
    #[pyo3(get)]
    pub evictions: u64,
    #[pyo3(get)]
    pub expired_removals: u64,
}

#[pymethods]
impl CacheStats {
    /// Get hit rate as percentage
    pub fn hit_rate(&self) -> f64 {
        let total = self.hits + self.misses;
        if total == 0 {
            0.0
        } else {
            (self.hits as f64 / total as f64) * 100.0
        }
    }

    /// Get miss rate as percentage
    pub fn miss_rate(&self) -> f64 {
        100.0 - self.hit_rate()
    }

    /// Reset statistics
    pub fn reset(&mut self) {
        self.hits = 0;
        self.misses = 0;
        self.evictions = 0;
        self.expired_removals = 0;
    }
}

/// Advanced cache implementation with LRU eviction
#[pyclass]
#[derive(Debug)]
pub struct Cache {
    entries: HashMap<String, CacheEntry<Vec<u8>>>,
    access_order: VecDeque<String>,
    default_ttl: Duration,
    max_size: usize,
    max_memory_mb: usize,
    current_memory_bytes: usize,
    stats: CacheStats,
}

#[pymethods]
impl Cache {
    #[new]
    #[pyo3(signature = (max_size=1000, default_ttl=300.0, max_memory_mb=100))]
    pub fn new(max_size: usize, default_ttl: f64, max_memory_mb: usize) -> Self {
        Cache {
            entries: HashMap::new(),
            access_order: VecDeque::new(),
            default_ttl: Duration::from_secs_f64(default_ttl),
            max_size,
            max_memory_mb,
            current_memory_bytes: 0,
            stats: CacheStats::default(),
        }
    }

    /// Set cache entry with automatic eviction
    pub fn set(&mut self, key: String, value: Vec<u8>, ttl: Option<f64>) -> bool {
        let value_size = value.len();
        let max_memory_bytes = self.max_memory_mb * 1024 * 1024;

        // Check if single entry would exceed memory limit
        if value_size > max_memory_bytes {
            return false;
        }

        // Remove existing entry if updating
        if self.entries.contains_key(&key) {
            self.remove(&key);
        }

        // Evict entries if necessary
        while (self.entries.len() >= self.max_size)
            || (self.current_memory_bytes + value_size > max_memory_bytes)
        {
            if !self.evict_lru() {
                break; // No more entries to evict
            }
        }

        let now = Instant::now();
        let ttl_duration = ttl.map(Duration::from_secs_f64).unwrap_or(self.default_ttl);

        let entry = CacheEntry {
            value,
            created_at: now,
            expires_at: Some(now + ttl_duration),
            last_accessed: now,
            access_count: 0,
        };

        self.current_memory_bytes += value_size;
        self.entries.insert(key.clone(), entry);
        self.access_order.push_back(key);

        true
    }

    /// Get cache entry with LRU tracking
    pub fn get(&mut self, key: &str) -> Option<Vec<u8>> {
        // Check if entry exists and is not expired
        let (should_return, value) = {
            if let Some(entry) = self.entries.get_mut(key) {
                // Check if expired
                if let Some(expires_at) = entry.expires_at {
                    if Instant::now() > expires_at {
                        (false, None) // Will remove after this block
                    } else {
                        // Update access tracking
                        entry.last_accessed = Instant::now();
                        entry.access_count += 1;
                        (true, Some(entry.value.clone()))
                    }
                } else {
                    // No expiration, update access tracking
                    entry.last_accessed = Instant::now();
                    entry.access_count += 1;
                    (true, Some(entry.value.clone()))
                }
            } else {
                (false, None)
            }
        };

        match should_return {
            true => {
                // Move to end of access order (most recently used)
                self.move_to_end(key);
                self.stats.hits += 1;
                value
            }
            false => {
                self.stats.misses += 1;
                if value.is_none() {
                    // Entry was expired, remove it
                    self.remove(key);
                }
                None
            }
        }
    }

    /// Remove cache entry
    pub fn remove(&mut self, key: &str) -> bool {
        if let Some(entry) = self.entries.remove(key) {
            self.current_memory_bytes = self.current_memory_bytes.saturating_sub(entry.value.len());

            // Remove from access order
            if let Some(pos) = self.access_order.iter().position(|k| k == key) {
                self.access_order.remove(pos);
            }

            true
        } else {
            false
        }
    }

    /// Clear all cache entries
    pub fn clear(&mut self) {
        self.entries.clear();
        self.access_order.clear();
        self.current_memory_bytes = 0;
    }

    /// Get cache size (number of entries)
    pub fn size(&self) -> usize {
        self.entries.len()
    }

    /// Get memory usage in MB
    pub fn memory_usage_mb(&self) -> f64 {
        self.current_memory_bytes as f64 / (1024.0 * 1024.0)
    }

    /// Get memory usage in bytes
    pub fn memory_usage_bytes(&self) -> usize {
        self.current_memory_bytes
    }

    /// Clean up expired entries
    pub fn cleanup_expired(&mut self) -> usize {
        let now = Instant::now();
        let initial_count = self.entries.len();

        let expired_keys: Vec<String> = self
            .entries
            .iter()
            .filter_map(|(key, entry)| {
                if let Some(expires_at) = entry.expires_at {
                    if now > expires_at {
                        Some(key.clone())
                    } else {
                        None
                    }
                } else {
                    None
                }
            })
            .collect();

        for key in expired_keys {
            self.remove(&key);
            self.stats.expired_removals += 1;
        }

        initial_count - self.entries.len()
    }

    /// Get cache statistics
    pub fn get_stats(&self) -> CacheStats {
        self.stats.clone()
    }

    /// Reset cache statistics
    pub fn reset_stats(&mut self) {
        self.stats.reset();
    }

    /// Get most accessed keys
    pub fn get_hot_keys(&self, limit: usize) -> Vec<(String, u64)> {
        let mut key_access: Vec<(String, u64)> = self
            .entries
            .iter()
            .map(|(key, entry)| (key.clone(), entry.access_count))
            .collect();

        key_access.sort_by(|a, b| b.1.cmp(&a.1));
        key_access.truncate(limit);
        key_access
    }

    /// Evict least recently used entry
    fn evict_lru(&mut self) -> bool {
        if let Some(key) = self.access_order.front().cloned() {
            self.remove(&key);
            self.stats.evictions += 1;
            true
        } else {
            false
        }
    }

    /// Move key to end of access order (most recently used)
    fn move_to_end(&mut self, key: &str) {
        if let Some(pos) = self.access_order.iter().position(|k| k == key) {
            let key = self.access_order.remove(pos).unwrap();
            self.access_order.push_back(key);
        }
    }
}

impl Default for Cache {
    fn default() -> Self {
        Self::new(1000, 300.0, 100)
    }
}

/// Thread-safe cache wrapper
#[pyclass]
#[derive(Debug, Clone)]
pub struct ThreadSafeCache {
    cache: Arc<Mutex<Cache>>,
}

#[pymethods]
impl ThreadSafeCache {
    #[new]
    #[pyo3(signature = (max_size=1000, default_ttl=300.0, max_memory_mb=100))]
    pub fn new(max_size: usize, default_ttl: f64, max_memory_mb: usize) -> Self {
        ThreadSafeCache {
            cache: Arc::new(Mutex::new(Cache::new(max_size, default_ttl, max_memory_mb))),
        }
    }

    /// Set cache entry (thread-safe)
    pub fn set(&self, key: String, value: Vec<u8>, ttl: Option<f64>) -> PyResult<bool> {
        match self.cache.lock() {
            Ok(mut cache) => Ok(cache.set(key, value, ttl)),
            Err(_) => Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Cache lock failed",
            )),
        }
    }

    /// Get cache entry (thread-safe)
    pub fn get(&self, key: &str) -> PyResult<Option<Vec<u8>>> {
        match self.cache.lock() {
            Ok(mut cache) => Ok(cache.get(key)),
            Err(_) => Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Cache lock failed",
            )),
        }
    }

    /// Remove cache entry (thread-safe)
    pub fn remove(&self, key: &str) -> PyResult<bool> {
        match self.cache.lock() {
            Ok(mut cache) => Ok(cache.remove(key)),
            Err(_) => Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Cache lock failed",
            )),
        }
    }

    /// Get cache statistics (thread-safe)
    pub fn get_stats(&self) -> PyResult<CacheStats> {
        match self.cache.lock() {
            Ok(cache) => Ok(cache.get_stats()),
            Err(_) => Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Cache lock failed",
            )),
        }
    }

    /// Cleanup expired entries (thread-safe)
    pub fn cleanup_expired(&self) -> PyResult<usize> {
        match self.cache.lock() {
            Ok(mut cache) => Ok(cache.cleanup_expired()),
            Err(_) => Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Cache lock failed",
            )),
        }
    }
}
