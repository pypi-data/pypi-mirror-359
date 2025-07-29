//! Performance module - benchmarking and optimization tools

pub mod benchmark_tools;
pub mod benchmarks;
pub mod caching;
pub mod connection_pool;
pub mod memory_profiler;
pub mod stats;

// Public re-exports
#[allow(unused_imports)]
pub use benchmark_tools::*;
#[allow(unused_imports)]
pub use benchmarks::*;
#[allow(unused_imports)]
pub use caching::*;
#[allow(unused_imports)]
pub use connection_pool::*;
#[allow(unused_imports)]
pub use memory_profiler::*;
#[allow(unused_imports)]
pub use stats::*;

// Re-export for backward compatibility where needed
