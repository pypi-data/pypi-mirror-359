// Memory profiler module
use pyo3::prelude::*;
use std::collections::HashMap;
use std::time::Instant;

/// Memory profiler for tracking memory usage
#[pyclass]
#[derive(Debug, Clone)]
pub struct MemoryProfiler {
    #[pyo3(get)]
    pub name: String,
    pub is_active: bool,
    pub start_time: Option<Instant>,
    pub measurements: Vec<MemoryMeasurement>,
}

#[derive(Debug, Clone)]
pub struct MemoryMeasurement {
    pub timestamp: Instant,
    pub memory_usage: u64, // In bytes (simulated)
}

#[pymethods]
impl MemoryProfiler {
    #[new]
    #[pyo3(signature = (name="memory_profiler".to_string()))]
    pub fn new(name: String) -> Self {
        MemoryProfiler {
            name,
            is_active: false,
            start_time: None,
            measurements: Vec::new(),
        }
    }

    /// Start profiling
    pub fn start(&mut self) -> PyResult<()> {
        if self.is_active {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Profiler is already active",
            ));
        }

        self.is_active = true;
        self.start_time = Some(Instant::now());
        self.measurements.clear();

        // Take initial measurement
        self.take_measurement();

        Ok(())
    }

    /// Stop profiling
    pub fn stop(&mut self) -> PyResult<HashMap<String, f64>> {
        if !self.is_active {
            return Err(pyo3::exceptions::PyRuntimeError::new_err(
                "Profiler is not active",
            ));
        }

        // Take final measurement
        self.take_measurement();

        self.is_active = false;
        let stats = self.get_stats();
        Ok(stats)
    }

    /// Check if profiler is active
    pub fn is_running(&self) -> bool {
        self.is_active
    }

    /// Take a memory measurement
    pub fn take_measurement(&mut self) {
        if !self.is_active {
            return;
        }

        // Simulate memory measurement (in a real implementation, this would
        // use system calls to get actual memory usage)
        let simulated_memory = 1024 * 1024 * (10 + self.measurements.len() as u64); // Start at 10MB

        let measurement = MemoryMeasurement {
            timestamp: Instant::now(),
            memory_usage: simulated_memory,
        };

        self.measurements.push(measurement);
    }

    /// Get profiling statistics
    pub fn get_stats(&self) -> HashMap<String, f64> {
        let mut stats = HashMap::new();

        if self.measurements.is_empty() {
            return stats;
        }

        let memory_values: Vec<f64> = self
            .measurements
            .iter()
            .map(|m| m.memory_usage as f64)
            .collect();

        if !memory_values.is_empty() {
            let min_memory = memory_values.iter().fold(f64::INFINITY, |a, &b| a.min(b));
            let max_memory = memory_values
                .iter()
                .fold(f64::NEG_INFINITY, |a, &b| a.max(b));
            let avg_memory = memory_values.iter().sum::<f64>() / memory_values.len() as f64;
            let memory_delta = max_memory - min_memory;

            stats.insert("min_memory_mb".to_string(), min_memory / (1024.0 * 1024.0));
            stats.insert("max_memory_mb".to_string(), max_memory / (1024.0 * 1024.0));
            stats.insert("avg_memory_mb".to_string(), avg_memory / (1024.0 * 1024.0));
            stats.insert(
                "memory_delta_mb".to_string(),
                memory_delta / (1024.0 * 1024.0),
            );
            stats.insert(
                "measurements_count".to_string(),
                self.measurements.len() as f64,
            );
        }

        if let Some(start_time) = self.start_time {
            let duration = if self.is_active {
                start_time.elapsed().as_secs_f64()
            } else if let Some(last_measurement) = self.measurements.last() {
                last_measurement
                    .timestamp
                    .duration_since(start_time)
                    .as_secs_f64()
            } else {
                0.0
            };
            stats.insert("duration_seconds".to_string(), duration);
        }

        stats
    }

    /// Reset profiler
    pub fn reset(&mut self) {
        self.is_active = false;
        self.start_time = None;
        self.measurements.clear();
    }

    /// Get measurement count
    pub fn measurement_count(&self) -> usize {
        self.measurements.len()
    }

    /// Context manager support - enter
    pub fn __enter__(mut slf: PyRefMut<Self>) -> PyResult<PyRefMut<Self>> {
        slf.start()?;
        Ok(slf)
    }

    /// Context manager support - exit
    pub fn __exit__(
        &mut self,
        _exc_type: Option<PyObject>,
        _exc_value: Option<PyObject>,
        _traceback: Option<PyObject>,
    ) -> PyResult<bool> {
        if self.is_active {
            let _ = self.stop();
        }
        Ok(false)
    }
}
