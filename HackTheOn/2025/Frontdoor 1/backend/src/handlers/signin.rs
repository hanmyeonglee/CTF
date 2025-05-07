use std::env;

use axum::{extract::Json, http::StatusCode, response::IntoResponse};
use serde::Deserialize;
use tower_sessions::Session;

use crate::prelude::*;

#[derive(Deserialize)]
pub struct PostSigninBody {
    username: String,
    password: String,
}

pub async fn post_signin_handler(
    session: Session,
    Json(body): Json<PostSigninBody>,
) -> impl IntoResponse {
    let guest_id = env::var("GUEST_ID")
        .ok()
        .unwrap_or(consts::DEFAULT_GUEST_ID.to_string());
    let guest_pwd = env::var("GUEST_PWD")
        .ok()
        .unwrap_or(consts::DEFAULT_GUEST_PW.to_string());

    let is_authed = guest_id == body.username && guest_pwd == body.password;

    if !is_authed {
        return (StatusCode::BAD_REQUEST, "Invalid username or password").into_response();
    }

    if let Err(err) = session.insert("auth", body.username).await {
        tracing::error!("Failed to insert session data: {}", err);
        return (StatusCode::INTERNAL_SERVER_ERROR, "Failed to signin").into_response();
    }

    let session_dir = match tempfile::tempdir() {
        Ok(tempdir) => tempdir.into_path(),
        Err(err) => {
            tracing::error!("Failed to create session directory: {}", err);
            let _ = session.remove::<String>("auth").await;
            return (StatusCode::INTERNAL_SERVER_ERROR, "Failed to signin").into_response();
        }
    };

    let session_dir = match session_dir.canonicalize() {
        Ok(path) => path,
        Err(err) => {
            tracing::error!("Failed to canonicalize session directory: {}", err);
            let _ = session.remove::<String>("auth").await;
            return (StatusCode::INTERNAL_SERVER_ERROR, "Failed to signin").into_response();
        }
    };

    if let Err(err) = session.insert("dir", session_dir).await {
        tracing::error!("Failed to insert session data: {}", err);
        let _ = session.remove::<String>("auth").await;
        return (
            StatusCode::INTERNAL_SERVER_ERROR,
            "Failed to store session data",
        )
            .into_response();
    }

    StatusCode::OK.into_response()
}
