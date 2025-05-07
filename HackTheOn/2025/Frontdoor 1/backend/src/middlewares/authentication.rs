use axum::{
    body::Body,
    http::{Request, StatusCode},
    middleware::Next,
    response::IntoResponse,
};
use tower_sessions::Session;

#[allow(unused)]
pub async fn authenticate(
    session: Session,
    request: Request<Body>,
    next: Next,
) -> impl IntoResponse {
    let is_authed = session.get::<String>("auth").await.ok().flatten().is_some();

    if !is_authed {
        return (StatusCode::UNAUTHORIZED, "Login required").into_response();
    }

    next.run(request).await
}
