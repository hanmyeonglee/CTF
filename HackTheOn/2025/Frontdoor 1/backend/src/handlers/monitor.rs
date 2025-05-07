use std::{
    collections::HashMap,
    ffi::OsStr,
    path::{Component, PathBuf},
    process,
};

use axum::{extract::Path, http::StatusCode, response::IntoResponse};
use tokio::fs;

fn alias(info: &str) -> Option<String> {
    match info {
        "cpu" => Some("stat".to_string()),
        "mem" => Some("meminfo".to_string()),
        "idle-time" => Some("uptime".to_string()),
        _ => None,
    }
}

fn parse_uptime(content: &str) -> String {
    let uptime = content.split_whitespace().next();

    let parse_res = match uptime {
        Some(time) => time.parse::<f64>(),
        None => {
            tracing::error!("Invalid uptime format");
            return String::new();
        }
    };

    let uptime_secs = match parse_res {
        Ok(secs) => secs,
        Err(err) => {
            tracing::error!("Failed to parse uptime: {}", err);
            return String::new();
        }
    };

    let days = (uptime_secs / 86400.0).floor();
    let hours = ((uptime_secs % 86400.0) / 3600.0).floor();
    let minutes = ((uptime_secs % 3600.0) / 60.0).floor();
    let seconds = (uptime_secs % 60.0).floor();

    format!("{}+{:02}:{:02}:{:02}", days, hours, minutes, seconds)
}

fn parse_idle_time(content: &str) -> String {
    let idle_time = content.split_whitespace().nth(1);

    let parse_res = match idle_time {
        Some(time) => time.parse::<f64>(),
        None => {
            tracing::error!("Invalid idle time format");
            return String::new();
        }
    };

    let idle_time_secs = match parse_res {
        Ok(secs) => secs,
        Err(err) => {
            tracing::error!("Failed to parse idle time: {}", err);
            return String::new();
        }
    };

    let days = (idle_time_secs / 86400.0).floor();
    let hours = ((idle_time_secs % 86400.0) / 3600.0).floor();
    let minutes = ((idle_time_secs % 3600.0) / 60.0).floor();
    let seconds = (idle_time_secs % 60.0).floor();

    format!("{}+{:02}:{:02}:{:02}", days, hours, minutes, seconds)
}

fn parse_cpu(content: &str) -> String {
    let cpu_line = match content.lines().next() {
        Some(line) => line,
        None => {
            tracing::error!("Failed to parse cpu");
            return String::new();
        }
    };

    let values: Vec<_> = cpu_line.split_whitespace().collect();
    if values.len() < 8 || values[0] != "cpu" {
        tracing::error!("Failed to parse cpu");
        return String::new();
    }

    let (user, nice, system, idle, iowait, irq, softirq) = match (
        values[1].parse::<u64>(),
        values[2].parse::<u64>(),
        values[3].parse::<u64>(),
        values[4].parse::<u64>(),
        values[5].parse::<u64>(),
        values[6].parse::<u64>(),
        values[7].parse::<u64>(),
    ) {
        (Ok(val1), Ok(val2), Ok(val3), Ok(val4), Ok(val5), Ok(val6), Ok(val7)) => {
            (val1, val2, val3, val4, val5, val6, val7)
        }
        _ => {
            tracing::error!("Failed to parse cpu");
            return String::new();
        }
    };

    let total_time = user + nice + system + idle + iowait + irq + softirq;
    let idle_time = idle + iowait;

    let cpu_usage = 100.0 - (idle_time as f64 / total_time as f64 * 100.0);

    cpu_usage.to_string()
}

fn parse_mem(content: &str) -> String {
    let mut mem_info = HashMap::new();

    for line in content.lines() {
        let parts: Vec<_> = line.split_whitespace().collect();
        if parts.len() >= 2 {
            let key = parts[0].trim_end_matches(":");
            let value = parts[1].parse().unwrap_or(0);
            mem_info.insert(key.to_string(), value);
        }
    }

    let (mem_total, mem_free, buffers, cached, slab) = match (
        mem_info.get("MemTotal"),
        mem_info.get("MemFree"),
        mem_info.get("Buffers"),
        mem_info.get("Cached"),
        mem_info.get("Slab"),
    ) {
        (Some(val1), Some(val2), Some(val3), Some(val4), Some(val5)) => {
            (val1, val2, val3, val4, val5)
        }
        _ => {
            tracing::error!("Failed to parse mem");
            return String::new();
        }
    };

    let used_memory = mem_total - mem_free - buffers - cached - slab;
    let mem_usage = (used_memory as f64 / *mem_total as f64) * 100.0;

    mem_usage.to_string()
}

async fn parse_content(info: &str, content: &str) -> String {
    match info {
        "uptime" => parse_uptime(content),
        "idle-time" => parse_idle_time(content),
        "cpu" => parse_cpu(content),
        "mem" => parse_mem(content),
        _ => {
            tracing::warn!("Unknown info type: '{}', content '{}'", info, content);
            String::new()
        }
    }
}

pub async fn get_monitor_handler(Path(info): Path<String>) -> impl IntoResponse {
    let file_path = match PathBuf::from("/proc")
        .join(alias(&info).unwrap_or(info.clone()))
        .canonicalize()
    {
        Ok(path) => path,
        Err(e) => {
            tracing::error!("Error canonicalizing path: {}", e);
            return (StatusCode::BAD_REQUEST, "Invalid parameter").into_response();
        }
    };

    let is_in_proc = file_path.starts_with("/proc");
    let is_file = file_path.is_file();

    if !is_in_proc || !is_file {
        return (StatusCode::BAD_REQUEST, "Invalid argument").into_response();
    }

    let comps: Vec<_> = file_path.components().collect();
    if comps.len() > 4 {
        return (StatusCode::BAD_REQUEST, "Invalid argument").into_response();
    }

    if comps.len() == 4
        && comps.get(2) != Some(&Component::Normal(OsStr::new(&process::id().to_string())))
    {
        return (StatusCode::BAD_REQUEST, "Invalid argument").into_response();
    }

    let msg = match fs::read_to_string(&file_path).await {
        Ok(content) => parse_content(&info, &content).await,
        Err(err) => {
            tracing::error!("Failed to read file '{}': {}", file_path.display(), err);
            return (StatusCode::BAD_REQUEST, "Invalid argument").into_response();
        }
    };

    (StatusCode::OK, msg).into_response()
}
