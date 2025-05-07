use axum::{http::StatusCode, response::IntoResponse};

pub async fn get_health_check_handler() -> impl IntoResponse {
    tracing::error!("Logging check!");
    (StatusCode::OK).into_response()
}
