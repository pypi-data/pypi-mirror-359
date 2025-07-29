//! Middleware module - request/response processing

pub mod auth;
pub mod headers;
pub mod logging;
pub mod manager;
pub mod rate_limit;
pub mod retry;

// Public re-exports
#[allow(unused_imports)]
pub use auth::*;
#[allow(unused_imports)]
pub use headers::*;
#[allow(unused_imports)]
pub use logging::*;
#[allow(unused_imports)]
pub use manager::*;
#[allow(unused_imports)]
pub use rate_limit::*;
#[allow(unused_imports)]
pub use retry::*;

// Backward compatibility re-exports handled above
