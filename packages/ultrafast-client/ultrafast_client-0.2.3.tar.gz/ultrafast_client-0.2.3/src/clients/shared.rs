// Shared client utilities and functionality
use crate::config::{AuthConfig, AuthType, OAuth2Token, RetryConfig};
use crate::core::error::{map_reqwest_error, UltraFastError};
use crate::core::response::ClientResponse;
use reqwest::{Client, RequestBuilder};
use std::collections::HashMap;
use std::time::{Duration, Instant};

/// Shared request execution utilities
#[allow(dead_code)]
pub struct RequestExecutor;

#[allow(dead_code)]
impl RequestExecutor {
    /// Apply authentication to a request builder
    pub fn apply_auth(
        request: RequestBuilder,
        auth_config: &AuthConfig,
        oauth2_token: Option<&OAuth2Token>,
    ) -> Result<RequestBuilder, UltraFastError> {
        match auth_config.auth_type {
            AuthType::Basic => {
                if let (Some(username), Some(password)) = (
                    auth_config.get_credential("username"),
                    auth_config.get_credential("password"),
                ) {
                    Ok(request.basic_auth(username, Some(password)))
                } else {
                    Err(UltraFastError::AuthenticationError(
                        "Basic auth requires username and password".to_string(),
                    ))
                }
            }
            AuthType::Bearer => {
                if let Some(token) = auth_config.get_credential("token") {
                    Ok(request.bearer_auth(token))
                } else {
                    Err(UltraFastError::AuthenticationError(
                        "Bearer auth requires token".to_string(),
                    ))
                }
            }
            AuthType::OAuth2 => {
                if let Some(oauth_token) = oauth2_token {
                    Ok(request.bearer_auth(&oauth_token.access_token))
                } else {
                    Err(UltraFastError::AuthenticationError(
                        "OAuth2 token not available".to_string(),
                    ))
                }
            }
            AuthType::ApiKey | AuthType::ApiKeyHeader => {
                if let (Some(key), Some(value)) = (
                    auth_config.get_credential("key"),
                    auth_config
                        .get_credential("value")
                        .or_else(|| auth_config.get_credential("header_name")),
                ) {
                    Ok(request.header(key, value))
                } else {
                    Err(UltraFastError::AuthenticationError(
                        "API key auth requires key and value".to_string(),
                    ))
                }
            }
            AuthType::ApiKeyQuery => {
                // Query parameters should be handled differently, not in headers
                Ok(request)
            }
            AuthType::Custom => {
                // Custom auth implementation can be added here
                Ok(request)
            }
        }
    }

    /// Build request URL with query parameters
    pub fn build_request_url(
        base_url: Option<&str>,
        url: &str,
        params: Option<&HashMap<String, String>>,
    ) -> Result<String, UltraFastError> {
        crate::core::client::utils::build_url(base_url, url, params)
    }

    /// Apply headers to request builder
    pub fn apply_headers(
        mut request: RequestBuilder,
        base_headers: Option<&HashMap<String, String>>,
        request_headers: Option<&HashMap<String, String>>,
    ) -> RequestBuilder {
        let merged_headers =
            crate::core::client::utils::merge_headers(base_headers, request_headers);

        for (key, value) in merged_headers {
            request = request.header(key, value);
        }

        request
    }

    /// Apply request body
    pub fn apply_body(
        request: RequestBuilder,
        body: Option<&[u8]>,
        content_type: Option<&str>,
    ) -> RequestBuilder {
        match (body, content_type) {
            (Some(body), Some(content_type)) => request
                .header("Content-Type", content_type)
                .body(body.to_vec()),
            (Some(body), None) => request.body(body.to_vec()),
            _ => request,
        }
    }

    /// Execute request with retry logic
    pub async fn execute_with_retry<F, Fut>(
        retry_config: Option<&RetryConfig>,
        operation: F,
    ) -> Result<ClientResponse, UltraFastError>
    where
        F: Fn() -> Fut,
        Fut: std::future::Future<Output = Result<ClientResponse, UltraFastError>>,
    {
        let default_retry = RetryConfig::new(3, 1.0, 30.0, 2.0, true, true, None);
        let retry_cfg = retry_config.unwrap_or(&default_retry);
        let mut last_error = None;

        for attempt in 0..=retry_cfg.max_retries {
            match operation().await {
                Ok(response) => return Ok(response),
                Err(err) => {
                    last_error = Some(err.clone());

                    // Don't retry on the last attempt
                    if attempt == retry_cfg.max_retries {
                        break;
                    }

                    // Check if error is retryable
                    if !Self::is_retryable_error(&err) {
                        break;
                    }

                    // Calculate delay with exponential backoff
                    let delay =
                        retry_cfg.initial_delay * (retry_cfg.backoff_factor.powi(attempt as i32));
                    let delay = delay.min(retry_cfg.max_delay);

                    // Add jitter to prevent thundering herd
                    let jitter = rand::random::<f64>() * 0.1; // 10% jitter
                    let final_delay = delay * (1.0 + jitter);

                    tokio::time::sleep(Duration::from_secs_f64(final_delay)).await;
                }
            }
        }

        Err(last_error
            .unwrap_or_else(|| UltraFastError::ClientError("Unknown retry error".to_string())))
    }

    /// Check if an error is retryable
    pub fn is_retryable_error(error: &UltraFastError) -> bool {
        match error {
            UltraFastError::NetworkError(_) => true,
            UltraFastError::TimeoutError(_) => true,
            UltraFastError::HttpError(status, _) => {
                // Retry on server errors (5xx) but not client errors (4xx)
                *status >= 500
            }
            UltraFastError::ConnectionPoolError(_) => true,
            _ => false,
        }
    }

    /// Calculate request statistics
    pub fn calculate_stats(start_time: Instant, response: &ClientResponse) -> HashMap<String, f64> {
        let elapsed = start_time.elapsed();
        let mut stats = HashMap::new();

        stats.insert("response_time_ms".to_string(), elapsed.as_millis() as f64);
        stats.insert("response_time_s".to_string(), elapsed.as_secs_f64());
        stats.insert("status_code".to_string(), response.status_code as f64);

        let headers = &response.headers;
        if let Some(content_length) = headers.get("content-length") {
            if let Ok(length) = content_length.parse::<f64>() {
                stats.insert("content_length".to_string(), length);
            }
        }

        stats
    }
}

/// Shared middleware execution utilities
#[allow(dead_code)]
pub struct MiddlewareExecutor;

#[allow(dead_code)]
impl MiddlewareExecutor {
    /// Apply request middleware
    pub fn apply_request_middleware(
        request: RequestBuilder,
        _middleware_manager: &crate::middleware::MiddlewareManager,
    ) -> Result<RequestBuilder, UltraFastError> {
        // Middleware application logic will be implemented here
        // For now, just return the request as-is
        Ok(request)
    }

    /// Apply response middleware
    pub fn apply_response_middleware(
        #[allow(unused_variables)] response: &mut ClientResponse,
        _middleware_manager: &crate::middleware::MiddlewareManager,
        _elapsed_time: Duration,
    ) -> Result<(), UltraFastError> {
        // Middleware application logic will be implemented here
        // For now, just return success
        Ok(())
    }
}

/// Shared OAuth2 token management
#[allow(dead_code)]
pub struct OAuth2TokenManager;

#[allow(dead_code)]
impl OAuth2TokenManager {
    /// Check if OAuth2 token needs refresh
    pub fn needs_refresh(token: &OAuth2Token) -> bool {
        if let Some(expires_in) = token.expires_in {
            // Refresh if token expires within 5 minutes
            let now = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs();
            let expires_at = token.issued_at + expires_in as f64;
            expires_at <= now as f64 + 300.0
        } else {
            false
        }
    }

    /// Refresh OAuth2 token
    pub async fn refresh_token(
        client: &Client,
        auth_config: &AuthConfig,
        current_token: &OAuth2Token,
    ) -> Result<OAuth2Token, UltraFastError> {
        if let Some(refresh_token) = &current_token.refresh_token {
            let mut params = HashMap::new();
            params.insert("grant_type".to_string(), "refresh_token".to_string());
            params.insert("refresh_token".to_string(), refresh_token.clone());

            if let Some(client_id) = auth_config.get_credential("client_id") {
                params.insert("client_id".to_string(), client_id);
            }

            let token_url = auth_config.get_credential("token_url").ok_or_else(|| {
                UltraFastError::AuthenticationError("Missing token_url".to_string())
            })?;
            let response = client
                .post(&token_url)
                .form(&params)
                .send()
                .await
                .map_err(map_reqwest_error)?;

            if response.status().is_success() {
                let token_data: serde_json::Value =
                    response.json().await.map_err(map_reqwest_error)?;

                let access_token = token_data["access_token"].as_str().ok_or_else(|| {
                    UltraFastError::AuthenticationError("No access token in response".to_string())
                })?;

                let refresh_token = token_data["refresh_token"]
                    .as_str()
                    .map(|s| s.to_string())
                    .or_else(|| current_token.refresh_token.clone());

                let expires_in = token_data["expires_in"].as_u64();
                let _expires_at = expires_in.map(|exp| {
                    std::time::SystemTime::now()
                        .duration_since(std::time::UNIX_EPOCH)
                        .unwrap_or_default()
                        .as_secs()
                        + exp
                });

                Ok(OAuth2Token {
                    access_token: access_token.to_string(),
                    refresh_token,
                    expires_in,
                    token_type: token_data["token_type"]
                        .as_str()
                        .unwrap_or("Bearer")
                        .to_string(),
                    scope: current_token.scope.clone(),
                    issued_at: std::time::SystemTime::now()
                        .duration_since(std::time::UNIX_EPOCH)
                        .unwrap_or_default()
                        .as_secs_f64(),
                })
            } else {
                Err(UltraFastError::AuthenticationError(format!(
                    "Token refresh failed: {}",
                    response.status()
                )))
            }
        } else {
            Err(UltraFastError::AuthenticationError(
                "No refresh token available".to_string(),
            ))
        }
    }

    /// Fetch initial OAuth2 token
    pub async fn fetch_token(
        client: &Client,
        auth_config: &AuthConfig,
    ) -> Result<OAuth2Token, UltraFastError> {
        let mut params = HashMap::new();
        params.insert("grant_type".to_string(), "client_credentials".to_string());

        if let Some(client_id) = auth_config.get_credential("client_id") {
            params.insert("client_id".to_string(), client_id);
        }

        if let Some(client_secret) = auth_config.get_credential("client_secret") {
            params.insert("client_secret".to_string(), client_secret);
        }

        if let Some(scope) = auth_config.get_credential("scope") {
            params.insert("scope".to_string(), scope);
        }

        let token_url = auth_config
            .get_credential("token_url")
            .ok_or_else(|| UltraFastError::AuthenticationError("Missing token_url".to_string()))?;
        let response = client
            .post(&token_url)
            .form(&params)
            .send()
            .await
            .map_err(map_reqwest_error)?;

        if response.status().is_success() {
            let token_data: serde_json::Value = response.json().await.map_err(map_reqwest_error)?;

            let access_token = token_data["access_token"].as_str().ok_or_else(|| {
                UltraFastError::AuthenticationError("No access token in response".to_string())
            })?;

            let refresh_token = token_data["refresh_token"].as_str().map(|s| s.to_string());

            let expires_in = token_data["expires_in"].as_u64();
            let _expires_at = expires_in.map(|exp| {
                std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_secs()
                    + exp
            });

            Ok(OAuth2Token {
                access_token: access_token.to_string(),
                refresh_token,
                expires_in,
                token_type: token_data["token_type"]
                    .as_str()
                    .unwrap_or("Bearer")
                    .to_string(),
                scope: auth_config.get_credential("scope"),
                issued_at: std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_secs_f64(),
            })
        } else {
            Err(UltraFastError::AuthenticationError(format!(
                "Token fetch failed: {}",
                response.status()
            )))
        }
    }
}
