// Configuration module - all configuration types and utilities
// This module contains configuration classes for various aspects of the HTTP client

pub mod auth_config;
pub mod client_config;
pub mod protocol_config;
pub mod validation;

// Public re-exports
#[allow(unused_imports)]
pub use auth_config::*;
#[allow(unused_imports)]
pub use client_config::*;
#[allow(unused_imports)]
pub use protocol_config::*;
#[allow(unused_imports)]
pub use validation::*;
