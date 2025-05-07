use axum::{
    body::Body,
    http::{Request, StatusCode},
    middleware::Next,
    response::IntoResponse,
};
use tower_sessions::Session;

pub async fn authorize(session: Session, request: Request<Body>, next: Next) -> impl IntoResponse {
    let is_admin = session
        .get::<String>("auth")
        .await
        .ok()
        .flatten()
        .map(|id| (id.as_str() == "Administrator").then_some(()))
        .is_some();

    if !is_admin {
        return (StatusCode::UNAUTHORIZED, "Administrator only").into_response();
    }

    next.run(request).await
}
