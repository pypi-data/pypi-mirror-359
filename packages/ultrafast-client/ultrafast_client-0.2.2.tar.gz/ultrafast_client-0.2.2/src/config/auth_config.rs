// Authentication configuration module
use base64::{engine::general_purpose, Engine as _};
use pyo3::prelude::*;
use std::collections::HashMap;
use tracing::{debug, info, instrument, warn};

/// Authentication type enumeration
#[pyclass]
#[derive(Clone, Debug, PartialEq)]
pub enum AuthType {
    #[pyo3(name = "Basic")]
    Basic,
    #[pyo3(name = "Bearer")]
    Bearer,
    #[pyo3(name = "OAuth2")]
    OAuth2,
    #[pyo3(name = "ApiKeyHeader")]
    ApiKeyHeader,
    #[pyo3(name = "ApiKeyQuery")]
    ApiKeyQuery,
    #[pyo3(name = "ApiKey")] // Alias for ApiKeyHeader for backward compatibility
    ApiKey,
    Custom,
}

#[pymethods]
impl AuthType {
    /// Uppercase constants for backward compatibility
    #[classattr]
    #[allow(non_snake_case)]
    fn BEARER() -> AuthType {
        AuthType::Bearer
    }

    #[classattr]
    #[allow(non_snake_case)]
    fn BASIC() -> AuthType {
        AuthType::Basic
    }

    #[classattr]
    #[allow(non_snake_case)]
    fn API_KEY_HEADER() -> AuthType {
        AuthType::ApiKeyHeader
    }

    #[classattr]
    #[allow(non_snake_case)]
    fn API_KEY_QUERY() -> AuthType {
        AuthType::ApiKeyQuery
    }

    #[classattr]
    #[allow(non_snake_case)]
    fn OAUTH2() -> AuthType {
        AuthType::OAuth2
    }

    #[classattr]
    #[allow(non_snake_case)]
    fn CUSTOM() -> AuthType {
        AuthType::Custom
    }

    /// Implement Python equality comparison
    fn __eq__(&self, other: &Self) -> bool {
        std::mem::discriminant(self) == std::mem::discriminant(other)
    }

    /// Implement Python hash for use in sets/dicts
    fn __hash__(&self) -> isize {
        match self {
            AuthType::Basic => 0,
            AuthType::Bearer => 1,
            AuthType::OAuth2 => 2,
            AuthType::ApiKeyHeader => 3,
            AuthType::ApiKeyQuery => 4,
            AuthType::ApiKey => 5,
            AuthType::Custom => 6,
        }
    }

    /// String representation
    fn __str__(&self) -> String {
        match self {
            AuthType::Basic => "Basic".to_string(),
            AuthType::Bearer => "Bearer".to_string(),
            AuthType::OAuth2 => "OAuth2".to_string(),
            AuthType::ApiKeyHeader => "ApiKeyHeader".to_string(),
            AuthType::ApiKeyQuery => "ApiKeyQuery".to_string(),
            AuthType::ApiKey => "ApiKey".to_string(),
            AuthType::Custom => "Custom".to_string(),
        }
    }

    /// Python representation
    fn __repr__(&self) -> String {
        format!("AuthType.{}", self.__str__())
    }
}

/// Authentication configuration
#[pyclass]
#[derive(Clone, Debug)]
pub struct AuthConfig {
    #[pyo3(get)]
    pub auth_type: AuthType,
    pub credentials: HashMap<String, String>,
}

#[pymethods]
impl AuthConfig {
    /// Create a new AuthConfig with custom type and credentials
    #[new]
    #[pyo3(signature = (auth_type = AuthType::Custom, credentials = None))]
    pub fn new(auth_type: AuthType, credentials: Option<HashMap<String, String>>) -> Self {
        AuthConfig {
            auth_type,
            credentials: credentials.unwrap_or_default(),
        }
    }

    /// Create Bearer token authentication
    #[staticmethod]
    pub fn bearer(token: String) -> Self {
        let mut credentials = HashMap::new();
        credentials.insert("token".to_string(), token);

        AuthConfig {
            auth_type: AuthType::Bearer,
            credentials,
        }
    }

    /// Create Basic authentication
    #[staticmethod]
    pub fn basic(username: String, password: String) -> Self {
        let mut credentials = HashMap::new();

        // Clone the values before moving them
        let username_clone = username.clone();
        let password_clone = password.clone();

        credentials.insert("username".to_string(), username);
        credentials.insert("password".to_string(), password);

        // Pre-compute the base64 encoded credentials
        let auth_string = format!("{}:{}", username_clone, password_clone);
        let encoded = general_purpose::STANDARD.encode(auth_string.as_bytes());
        credentials.insert("encoded".to_string(), encoded);

        AuthConfig {
            auth_type: AuthType::Basic,
            credentials,
        }
    }

    /// Create API key authentication for headers
    #[staticmethod]
    pub fn api_key_header(key: String, header_name: String) -> Self {
        let mut credentials = HashMap::new();
        credentials.insert("key".to_string(), key);
        credentials.insert("header_name".to_string(), header_name);

        AuthConfig {
            auth_type: AuthType::ApiKeyHeader,
            credentials,
        }
    }

    /// Create API key authentication for query parameters
    #[staticmethod]
    pub fn api_key_query(key: String, param_name: String) -> Self {
        let mut credentials = HashMap::new();
        credentials.insert("key".to_string(), key);
        credentials.insert("param_name".to_string(), param_name);

        AuthConfig {
            auth_type: AuthType::ApiKeyQuery,
            credentials,
        }
    }

    /// Create OAuth2 authentication
    #[staticmethod]
    #[pyo3(signature = (client_id, client_secret, token_url, scope=None, redirect_uri=None, state=None))]
    pub fn oauth2(
        client_id: String,
        client_secret: String,
        token_url: String,
        scope: Option<String>,
        redirect_uri: Option<String>,
        state: Option<String>,
    ) -> Self {
        let mut credentials = HashMap::new();
        credentials.insert("client_id".to_string(), client_id);
        credentials.insert("client_secret".to_string(), client_secret);
        credentials.insert("token_url".to_string(), token_url);

        if let Some(scope) = scope {
            credentials.insert("scope".to_string(), scope);
        }

        if let Some(redirect_uri) = redirect_uri {
            credentials.insert("redirect_uri".to_string(), redirect_uri);
        }

        if let Some(state) = state {
            credentials.insert("state".to_string(), state);
        }

        AuthConfig {
            auth_type: AuthType::OAuth2,
            credentials,
        }
    }

    /// Create custom authentication
    #[staticmethod]
    pub fn custom(auth_type: String, credentials: HashMap<String, String>) -> Self {
        let mut creds = credentials;
        creds.insert("custom_type".to_string(), auth_type);

        AuthConfig {
            auth_type: AuthType::Custom,
            credentials: creds,
        }
    }

    /// Create API key authentication (header-based)
    #[staticmethod]
    pub fn api_key(key: String, value: String) -> Self {
        let mut credentials = HashMap::new();
        credentials.insert("key".to_string(), key);
        credentials.insert("value".to_string(), value);

        AuthConfig {
            auth_type: AuthType::ApiKey,
            credentials,
        }
    }

    /// Get a credential value
    pub fn get_credential(&self, key: &str) -> Option<String> {
        self.credentials.get(key).cloned()
    }

    /// Check if authentication is OAuth2
    pub fn is_oauth2(&self) -> bool {
        matches!(self.auth_type, AuthType::OAuth2)
    }

    /// Validate the authentication configuration
    #[instrument(skip(self), fields(auth_type = ?self.auth_type))]
    pub fn validate(&self) -> PyResult<()> {
        debug!("Validating authentication configuration");

        match self.auth_type {
            AuthType::Bearer => {
                if self.get_credential("token").is_none() {
                    warn!("Bearer token validation failed: token not set");
                    return Err(pyo3::exceptions::PyValueError::new_err(
                        "Bearer token not set",
                    ));
                }
                debug!("Bearer token validation successful");
            }
            AuthType::Basic => {
                if self.get_credential("username").is_none()
                    || self.get_credential("password").is_none()
                {
                    warn!("Basic auth validation failed: missing username or password");
                    return Err(pyo3::exceptions::PyValueError::new_err(
                        "Basic auth requires username and password",
                    ));
                }
                debug!("Basic auth validation successful");
            }
            AuthType::ApiKeyHeader => {
                if self.get_credential("key").is_none()
                    || self.get_credential("header_name").is_none()
                {
                    warn!("API key header validation failed: missing key or header_name");
                    return Err(pyo3::exceptions::PyValueError::new_err(
                        "API key header auth requires key and header_name",
                    ));
                }
                debug!("API key header validation successful");
            }
            AuthType::ApiKeyQuery => {
                if self.get_credential("key").is_none()
                    || self.get_credential("param_name").is_none()
                {
                    warn!("API key query validation failed: missing key or param_name");
                    return Err(pyo3::exceptions::PyValueError::new_err(
                        "API key query auth requires key and param_name",
                    ));
                }
                debug!("API key query validation successful");
            }
            AuthType::ApiKey => {
                // Alias for ApiKeyHeader - same validation
                if self.get_credential("key").is_none() || self.get_credential("value").is_none() {
                    warn!("API key validation failed: missing key or value");
                    return Err(pyo3::exceptions::PyValueError::new_err(
                        "API key auth requires key and value",
                    ));
                }
                debug!("API key validation successful");
            }
            AuthType::OAuth2 => {
                if self.get_credential("client_id").is_none()
                    || self.get_credential("token_url").is_none()
                {
                    warn!("OAuth2 validation failed: missing client_id or token_url");
                    return Err(pyo3::exceptions::PyValueError::new_err(
                        "OAuth2 requires client_id and token_url",
                    ));
                }
                debug!("OAuth2 validation successful");
            }
            AuthType::Custom => {
                debug!("Custom auth validation successful (no specific validation)");
            }
        }

        info!("Authentication configuration validation completed successfully");
        Ok(())
    }

    /// Generate headers for the authentication
    pub fn generate_headers(&self) -> PyResult<HashMap<String, String>> {
        let mut headers = HashMap::new();

        match self.auth_type {
            AuthType::Bearer => {
                if let Some(token) = self.get_credential("token") {
                    headers.insert("Authorization".to_string(), format!("Bearer {}", token));
                }
            }
            AuthType::Basic => {
                if let Some(encoded) = self.get_credential("encoded") {
                    headers.insert("Authorization".to_string(), format!("Basic {}", encoded));
                }
            }
            AuthType::ApiKeyHeader => {
                if let (Some(key), Some(header_name)) = (
                    self.get_credential("key"),
                    self.get_credential("header_name"),
                ) {
                    headers.insert(header_name, key);
                }
            }
            AuthType::ApiKeyQuery => {
                // Query parameters are not headers, so we don't add anything here
            }
            AuthType::ApiKey => {
                // Alias for ApiKeyHeader - same behavior
                if let (Some(key), Some(value)) =
                    (self.get_credential("key"), self.get_credential("value"))
                {
                    headers.insert(key, value);
                }
            }
            AuthType::OAuth2 => {
                // OAuth2 headers are generated dynamically after token fetch
            }
            AuthType::Custom => {
                // Custom auth - could be extended
            }
        }

        Ok(headers)
    }

    /// Check if authentication is Basic
    pub fn is_basic(&self) -> bool {
        matches!(self.auth_type, AuthType::Basic)
    }

    /// Check if authentication is Bearer
    pub fn is_bearer(&self) -> bool {
        matches!(self.auth_type, AuthType::Bearer)
    }

    /// Check if authentication is API Key
    pub fn is_api_key(&self) -> bool {
        matches!(
            self.auth_type,
            AuthType::ApiKeyHeader | AuthType::ApiKeyQuery
        )
    }
}

impl AuthConfig {
    /// Fetch OAuth2 token asynchronously
    #[instrument(skip(self), fields(token_url = %self.get_credential("token_url").unwrap_or_else(|| "unknown".to_string())))]
    pub async fn fetch_oauth2_token(&self) -> Result<OAuth2Token, String> {
        if self.auth_type != AuthType::OAuth2 {
            warn!("Attempted to fetch OAuth2 token for non-OAuth2 auth type");
            return Err("Not an OAuth2 auth configuration".to_string());
        }

        debug!("Starting OAuth2 token fetch");

        let client_id = self
            .get_credential("client_id")
            .ok_or_else(|| "Missing client_id in credentials".to_string())?;
        let token_url = self
            .get_credential("token_url")
            .ok_or_else(|| "Missing token_url in credentials".to_string())?;
        let client_secret = self.get_credential("client_secret");
        let scopes = self.get_credential("scopes");

        let mut params = vec![
            ("grant_type", "client_credentials"),
            ("client_id", &client_id),
        ];
        if let Some(ref secret) = client_secret {
            params.push(("client_secret", secret));
            debug!("Using client secret for OAuth2 token request");
        }
        if let Some(ref scopes) = scopes {
            params.push(("scope", scopes));
            debug!(scopes = %scopes, "Using scopes for OAuth2 token request");
        }

        debug!("Sending OAuth2 token request");
        let client = reqwest::Client::new();
        let response = client
            .post(&token_url)
            .form(&params)
            .send()
            .await
            .map_err(|e| {
                warn!(error = %e, "Failed to send OAuth2 token request");
                format!("Failed to send token request: {}", e)
            })?;

        let status = response.status();
        if !status.is_success() {
            warn!(status = %status, "OAuth2 token request failed");
            return Err(format!("Token request failed with status: {}", status));
        }

        debug!(status = %status, "OAuth2 token request successful, parsing response");

        #[derive(serde::Deserialize)]
        struct TokenResponse {
            access_token: String,
            token_type: Option<String>,
            expires_in: Option<u64>,
            refresh_token: Option<String>,
            scope: Option<String>,
        }

        let token_response: TokenResponse = response.json().await.map_err(|e| {
            warn!(error = %e, "Failed to parse OAuth2 token response");
            format!("Failed to parse token response: {}", e)
        })?;

        let issued_at = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs_f64();

        info!(
            token_type = %token_response.token_type.as_ref().unwrap_or(&"Bearer".to_string()),
            expires_in = ?token_response.expires_in,
            has_refresh_token = token_response.refresh_token.is_some(),
            "OAuth2 token fetched successfully"
        );

        Ok(OAuth2Token {
            access_token: token_response.access_token,
            token_type: token_response
                .token_type
                .unwrap_or_else(|| "Bearer".to_string()),
            expires_in: token_response.expires_in,
            refresh_token: token_response.refresh_token,
            scope: token_response.scope,
            issued_at,
        })
    }
}

/// OAuth2 token structure
#[pyclass]
#[derive(Clone, Debug)]
pub struct OAuth2Token {
    #[pyo3(get)]
    pub access_token: String,
    #[pyo3(get)]
    pub token_type: String,
    #[pyo3(get)]
    pub expires_in: Option<u64>,
    #[pyo3(get)]
    pub refresh_token: Option<String>,
    #[pyo3(get)]
    pub scope: Option<String>,
    #[pyo3(get)]
    pub issued_at: f64,
}

#[pymethods]
impl OAuth2Token {
    #[new]
    #[pyo3(signature = (access_token, token_type="Bearer".to_string(), expires_in=None, refresh_token=None, scope=None))]
    pub fn new(
        access_token: String,
        token_type: String,
        expires_in: Option<u64>,
        refresh_token: Option<String>,
        scope: Option<String>,
    ) -> Self {
        let issued_at = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs_f64();

        OAuth2Token {
            access_token,
            token_type,
            expires_in,
            refresh_token,
            scope,
            issued_at,
        }
    }

    /// Check if the token is expired
    pub fn is_expired(&self) -> bool {
        if let Some(expires_in) = self.expires_in {
            let now = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs_f64();

            now >= self.issued_at + expires_in as f64
        } else {
            false // No expiry time means it doesn't expire
        }
    }

    /// Get remaining lifetime in seconds
    pub fn remaining_lifetime(&self) -> Option<f64> {
        if let Some(expires_in) = self.expires_in {
            let now = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs_f64();

            let remaining = (self.issued_at + expires_in as f64) - now;
            if remaining > 0.0 {
                Some(remaining)
            } else {
                Some(0.0)
            }
        } else {
            None
        }
    }
}
