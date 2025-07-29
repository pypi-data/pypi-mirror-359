//! Core module - fundamental types and utilities

// Core submodules
pub mod client;
pub mod error;
pub mod response;

// Public re-exports with allow annotation for unused imports
#[allow(unused_imports)]
pub use client::*;
#[allow(unused_imports)]
pub use error::*;
#[allow(unused_imports)]
pub use response::*;
