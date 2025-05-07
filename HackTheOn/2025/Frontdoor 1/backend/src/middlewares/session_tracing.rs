use axum::{
    body::Body,
    http::{Request, StatusCode},
    middleware::Next,
    response::IntoResponse,
};
use tower_sessions::Session;
use tracing::Instrument;

pub async fn tracing_session_id(
    session: Session,
    request: Request<Body>,
    next: Next,
) -> impl IntoResponse {
    let session_id = match session.id() {
        Some(id) => id.to_string(),
        None => {
            if let Err(err) = session.insert("_", true).await {
                tracing::error!("Failed to insert session data: {}", err);
                return (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    "Failed to generate session ID",
                )
                    .into_response();
            }

            if let Err(err) = session.save().await {
                tracing::error!("Failed to save session: {}", err);
                return (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    "Failed to generate session ID",
                )
                    .into_response();
            }

            match session.id() {
                Some(id) => id.to_string(),
                None => {
                    tracing::error!("Session ID still not available after save...");
                    return (
                        StatusCode::INTERNAL_SERVER_ERROR,
                        "Failed to generate session ID",
                    )
                        .into_response();
                }
            }
        }
    };

    let span = tracing::debug_span!("session", id = %session_id);
    next.run(request).instrument(span).await
}
