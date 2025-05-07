use axum::{http::StatusCode, response::IntoResponse};
use tokio::fs;

pub async fn get_flag_handler() -> impl IntoResponse {
    match fs::read_to_string("flag").await {
        Ok(content) => (StatusCode::OK, content).into_response(),
        Err(err) => {
            tracing::error!("Failed to read flag file: {}", err);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                "Failed to retrieve flag".to_string(),
            )
                .into_response()
        }
    }
}
