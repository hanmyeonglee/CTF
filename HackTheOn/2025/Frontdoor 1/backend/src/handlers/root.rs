use axum::response::{IntoResponse, Redirect};

pub async fn get_root_handler() -> impl IntoResponse {
    Redirect::permanent("/api/health-check")
}
