pub mod consts;
mod error;
mod handlers;
mod middlewares;

mod prelude {
    pub use super::consts;
    pub use super::error::*;
}

use std::{
    env,
    net::{Ipv4Addr, SocketAddr},
    path::PathBuf,
};

use axum::{
    Router, middleware,
    routing::{get, post},
};
use tower_sessions::{MemoryStore, SessionManagerLayer};
use tracing_appender::rolling::{RollingFileAppender, Rotation};
use tracing_subscriber::EnvFilter;

fn get_host_port() -> (Ipv4Addr, u16) {
    let backend_host: Ipv4Addr = match env::var("BACKEND_HOST").ok() {
        Some(h) => h
            .parse::<Ipv4Addr>()
            .inspect_err(|e| {
                tracing::warn!(
                    "Failed to parse BACKEND_HOST: {}, using default host {}",
                    e,
                    consts::DEFAULT_HOST
                )
            })
            .ok(),
        None => {
            tracing::info!("Using default host {}", consts::DEFAULT_HOST);
            None
        }
    }
    .unwrap_or(consts::DEFAULT_HOST.parse().unwrap());

    let backend_port: u16 = match env::var("BACKEND_PORT").ok() {
        Some(p) => p
            .parse::<u16>()
            .inspect_err(|e| {
                tracing::warn!(
                    "Failed to parse BACKEND_PORT: {}, using default port {}",
                    e,
                    consts::DEFAULT_PORT
                )
            })
            .ok(),
        None => {
            tracing::info!("Using default port {}", consts::DEFAULT_PORT);
            None
        }
    }
    .unwrap_or(consts::DEFAULT_PORT);

    (backend_host, backend_port)
}

#[tokio::main]
async fn main() -> std::result::Result<(), anyhow::Error> {
    let (backend_host, backend_port) = get_host_port();

    let log_path = PathBuf::from(consts::LOG_DIR).join(consts::LOG_FILE);
    if log_path.exists() {
        if let Err(err) = tokio::fs::remove_file(log_path).await {
            tracing::error!("Failed to remove log file: {}", err);
        }
    }

    let file_appender =
        RollingFileAppender::new(Rotation::NEVER, consts::LOG_DIR, consts::LOG_FILE);
    let (non_blocking, _guard) = tracing_appender::non_blocking(file_appender);
    tracing_subscriber::fmt()
        .with_writer(non_blocking)
        .with_ansi(false)
        .with_env_filter(EnvFilter::new("backend=DEBUG"))
        .init();

    let session_store = MemoryStore::default();
    let session_layer = SessionManagerLayer::new(session_store)
        .with_secure(false)
        .with_http_only(false);

    let app = Router::new()
        .route("/api", get(handlers::get_root_handler))
        .route("/api/health-check", get(handlers::get_health_check_handler))
        .route("/api/logs", get(handlers::get_logs_handler))
        .route("/api/monitor/{info}", get(handlers::get_monitor_handler))
        .route("/api/signin", post(handlers::post_signin_handler))
        .route(
            "/api/flag",
            get(handlers::get_flag_handler).layer(middleware::from_fn(middlewares::authorize)),
        )
        .layer(middleware::from_fn(middlewares::tracing_session_id))
        .layer(middleware::from_fn(middlewares::set_session_expiry))
        .layer(session_layer);

    let addr = SocketAddr::from((backend_host, backend_port));
    tracing::info!("Backend running on {:?}", addr);

    let listener = tokio::net::TcpListener::bind(&addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}
