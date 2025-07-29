// Benchmark tools module
use pyo3::prelude::*;
use std::collections::HashMap;
use std::time::{Duration, Instant};

/// Benchmark tool for performance testing
#[pyclass]
#[derive(Debug, Clone)]
pub struct Benchmark {
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub iterations: u32,
    #[pyo3(get)]
    pub warmup_iterations: u32,
    pub results: Vec<Duration>,
}

#[pymethods]
impl Benchmark {
    #[new]
    #[pyo3(signature = (name="benchmark".to_string(), iterations=100, warmup_iterations=10))]
    pub fn new(name: String, iterations: u32, warmup_iterations: u32) -> Self {
        Benchmark {
            name,
            iterations,
            warmup_iterations,
            results: Vec::new(),
        }
    }

    /// Run benchmark
    pub fn run(&mut self, func: PyObject) -> PyResult<HashMap<String, f64>> {
        Python::with_gil(|py| {
            // Warmup
            for _ in 0..self.warmup_iterations {
                let _ = func.call0(py)?;
            }

            // Actual benchmark
            self.results.clear();
            for _ in 0..self.iterations {
                let start = Instant::now();
                let _ = func.call0(py)?;
                let elapsed = start.elapsed();
                self.results.push(elapsed);
            }

            Ok(self.get_stats())
        })
    }

    /// Get benchmark statistics
    pub fn get_stats(&self) -> HashMap<String, f64> {
        let mut stats = HashMap::new();

        if self.results.is_empty() {
            return stats;
        }

        let durations: Vec<f64> = self.results.iter().map(|d| d.as_secs_f64()).collect();

        // Calculate statistics
        let total: f64 = durations.iter().sum();
        let mean = total / durations.len() as f64;

        let mut sorted = durations.clone();
        sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());

        let min = sorted[0];
        let max = sorted[sorted.len() - 1];
        let median = if sorted.len() % 2 == 0 {
            (sorted[sorted.len() / 2 - 1] + sorted[sorted.len() / 2]) / 2.0
        } else {
            sorted[sorted.len() / 2]
        };

        // Calculate standard deviation
        let variance: f64 =
            durations.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / durations.len() as f64;
        let std_dev = variance.sqrt();

        stats.insert("mean".to_string(), mean);
        stats.insert("median".to_string(), median);
        stats.insert("min".to_string(), min);
        stats.insert("max".to_string(), max);
        stats.insert("std_dev".to_string(), std_dev);
        stats.insert("iterations".to_string(), self.iterations as f64);
        stats.insert("total_time".to_string(), total);

        stats
    }

    /// Reset benchmark results
    pub fn reset(&mut self) {
        self.results.clear();
    }

    /// Get results count
    pub fn results_count(&self) -> usize {
        self.results.len()
    }
}
