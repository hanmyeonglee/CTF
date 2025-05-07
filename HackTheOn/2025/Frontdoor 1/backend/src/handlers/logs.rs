use std::path::PathBuf;

use axum::{extract::Query, http::StatusCode, response::IntoResponse};
use serde::Deserialize;
use tokio::io::{AsyncBufReadExt, BufReader};
use tower_sessions::Session;

use crate::prelude::*;

#[derive(Deserialize, PartialEq, PartialOrd)]
#[serde(rename_all = "lowercase")]
enum LogLevel {
    Error,
    Warn,
    Info,
    Debug,
}

fn extract_log_level(line: &str) -> Option<LogLevel> {
    if line.contains("ERROR") {
        Some(LogLevel::Error)
    } else if line.contains("WARN") {
        Some(LogLevel::Warn)
    } else if line.contains("INFO") {
        Some(LogLevel::Info)
    } else if line.contains("DEBUG") {
        Some(LogLevel::Debug)
    } else {
        None
    }
}

async fn get_logs(session_id: &str, level: LogLevel) -> Result<Vec<String>> {
    let file =
        match tokio::fs::File::open(PathBuf::from(consts::LOG_DIR).join(consts::LOG_FILE)).await {
            Ok(file) => file,
            Err(err) => {
                tracing::error!("Failed to open log file: {}", err);
                return Err(Error::IO("Failed to get logs".to_string()));
            }
        };

    let mut resp = Vec::new();

    let reader = BufReader::new(file);
    let mut lines = reader.lines();

    loop {
        match lines.next_line().await {
            Ok(Some(line)) => {
                if let Some(line_level) = extract_log_level(&line) {
                    if line_level <= level && line.contains(session_id) {
                        resp.push(line);
                    }
                }
            }
            Ok(None) => break,
            Err(err) => {
                tracing::error!("Failed to read line: {}", err);
                return Err(Error::IO("Failed to get logs".to_string()));
            }
        }
    }

    Ok(resp)
}

#[derive(Deserialize)]
pub struct GetLogsQuery {
    level: Option<LogLevel>,
}

pub async fn get_logs_handler(
    session: Session,
    Query(query): Query<GetLogsQuery>,
) -> impl IntoResponse {
    let session_id = session.id().unwrap_or_default().to_string();
    let level = query.level.unwrap_or(LogLevel::Error);

    match get_logs(&session_id, level).await {
        Ok(logs) => (StatusCode::OK, logs.join("\n")).into_response(),
        Err(_) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            "Failed to get logs".to_string(),
        )
            .into_response(),
    }
}
