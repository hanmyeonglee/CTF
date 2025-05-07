use axum::{body::Body, http::Request, middleware::Next, response::IntoResponse};
use time::{Duration, OffsetDateTime};
use tower_sessions::{Expiry, Session};

pub async fn set_session_expiry(
    session: Session,
    request: Request<Body>,
    next: Next,
) -> impl IntoResponse {
    match session.get::<bool>("expiry").await {
        Ok(Some(true)) => (),
        _ => {
            let expiry = Some(Expiry::AtDateTime(
                OffsetDateTime::now_utc() + Duration::minutes(10),
            ));
            session.set_expiry(expiry);
            let _ = session.insert("expiry", true).await;
            let _ = session.save().await;
        }
    }

    next.run(request).await
}
