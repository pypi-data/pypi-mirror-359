use std::{net::SocketAddr, sync::{Arc, Mutex}, collections::HashMap};
use axum::{
    Router,
    routing::{post, get},
    extract::State,
    Json,
    http::StatusCode,
};
use tower::ServiceBuilder;
use tower_http::trace::TraceLayer;
use tower_http::limit::RequestBodyLimitLayer;
use serde::{Deserialize, Serialize};
use core as core_crate;
use core_crate::Vector;
use anyhow::Result;
use super::Service;
use storage::Meta;

// Type alias for our shared service state
type SharedService = Arc<Mutex<Service>>;

#[derive(Deserialize)]
struct AddReq {
    id: usize,
    vector: Vec<f32>,
    /// Optional metadata map
    #[serde(default)]
    metadata: HashMap<String, String>,
}

#[derive(Deserialize)]
struct BulkAddReq {
    vectors: Vec<AddReq>,
}

#[derive(Deserialize)]
struct SearchReq {
    vector: Vec<f32>,
    k: usize,
    /// Optional metadata filter
    #[serde(default)]
    filter: HashMap<String, String>,
}

#[derive(Deserialize)]
struct BulkSearchReq {
    queries: Vec<SearchReq>,
}

#[derive(Serialize)]
struct SearchRes {
    id: usize,
    score: f32,
}

#[derive(Serialize)]
struct BulkSearchRes {
    results: Vec<Vec<SearchRes>>,
}

#[derive(Serialize)]
struct SnapshotRes { 
    success: bool,
    message: String,
}

#[derive(Serialize)]
struct HealthRes {
    status: String,
    version: String,
    uptime_seconds: u64,
    vector_count: usize,
    index_type: String,
    max_request_size_mb: f32,
}

#[derive(Serialize)]
struct MetricsRes {
    total_vectors: usize,
    total_searches: u64,
    total_inserts: u64,
    avg_search_latency_ms: f64,
    memory_usage_mb: f64,
    max_batch_size: usize,
}

#[derive(Serialize)]
struct ErrorRes {
    error: String,
    code: String,
    details: Option<String>,
}

// Global metrics (in real app, use proper metrics library)
static mut SEARCH_COUNT: u64 = 0;
static mut INSERT_COUNT: u64 = 0;
static mut SEARCH_LATENCY_SUM: f64 = 0.0;

// Configuration constants
const MAX_REQUEST_SIZE_MB: usize = 100; // Increased to 100MB
const MAX_BATCH_SIZE: usize = 10000; // Maximum vectors per batch
const MAX_BULK_QUERIES: usize = 1000; // Maximum queries per bulk search

fn validate_vector_dimension(vector: &[f32], expected_dim: usize) -> Result<(), String> {
    if vector.len() != expected_dim {
        return Err(format!(
            "Vector dimension mismatch: expected {}, got {}", 
            expected_dim, vector.len()
        ));
    }
    
    // Check for invalid values
    for (i, &val) in vector.iter().enumerate() {
        if !val.is_finite() {
            return Err(format!("Invalid value at index {}: {}", i, val));
        }
    }
    
    Ok(())
}

async fn add_handler(
    State(svc): State<SharedService>,
    Json(payload): Json<AddReq>,
) -> Result<StatusCode, (StatusCode, Json<ErrorRes>)> {
    // Get dimension from service
    let expected_dim = {
        let svc_guard = svc.lock().unwrap();
        svc_guard.dimension()
    };

    // Validate vector dimension
    if let Err(msg) = validate_vector_dimension(&payload.vector, expected_dim) {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(ErrorRes {
                error: msg,
                code: "INVALID_DIMENSION".to_string(),
                details: Some(format!("Expected {} dimensions", expected_dim)),
            }),
        ));
    }

    let mut svc = svc.lock().unwrap();
    let v = Vector::new(payload.vector);
    
    match svc.add(payload.id, v, Meta::with_data(payload.metadata)) {
        Ok(_) => {
            unsafe { INSERT_COUNT += 1; }
            Ok(StatusCode::CREATED)
        }
        Err(e) => Err((
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorRes {
                error: e.to_string(),
                code: "INSERT_FAILED".to_string(),
                details: None,
            }),
        )),
    }
}

async fn bulk_add_handler(
    State(svc): State<SharedService>,
    Json(payload): Json<BulkAddReq>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<ErrorRes>)> {
    if payload.vectors.is_empty() {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(ErrorRes {
                error: "Empty vector list".to_string(),
                code: "EMPTY_BULK_REQUEST".to_string(),
                details: Some("At least one vector is required".to_string()),
            }),
        ));
    }

    // Check batch size limit
    if payload.vectors.len() > MAX_BATCH_SIZE {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(ErrorRes {
                error: format!("Batch too large: {} vectors", payload.vectors.len()),
                code: "BATCH_TOO_LARGE".to_string(),
                details: Some(format!("Maximum batch size is {} vectors", MAX_BATCH_SIZE)),
            }),
        ));
    }

    // Get dimension from service
    let expected_dim = {
        let svc_guard = svc.lock().unwrap();
        svc_guard.dimension()
    };

    let mut svc = svc.lock().unwrap();
    
    // Convert request data to the format needed for bulk insertion
    let mut ids = Vec::with_capacity(payload.vectors.len());
    let mut vectors = Vec::with_capacity(payload.vectors.len());
    let mut metas = Vec::with_capacity(payload.vectors.len());
    
    for req in &payload.vectors {
        // Validate dimension
        if let Err(msg) = validate_vector_dimension(&req.vector, expected_dim) {
            return Err((
                StatusCode::BAD_REQUEST,
                Json(ErrorRes {
                    error: msg,
                    code: "INVALID_DIMENSION".to_string(),
                    details: Some(format!("Expected {} dimensions", expected_dim)),
                }),
            ));
        }
        
        ids.push(req.id);
        vectors.push(Vector::new(req.vector.clone()));
        metas.push(Meta::with_data(req.metadata.clone()));
    }
    
    // Use bulk insertion for maximum performance
    match svc.bulk_add(&ids, &vectors, &metas) {
        Ok(successful) => {
            unsafe { INSERT_COUNT += successful as u64; }
            Ok(Json(serde_json::json!({
                "successful": successful,
                "failed": 0,
                "errors": [],
                "batch_size": payload.vectors.len(),
                "max_batch_size": MAX_BATCH_SIZE,
                "bulk_insertion": true
            })))
        }
        Err(e) => {
            Err((
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ErrorRes {
                    error: format!("Bulk insertion failed: {}", e),
                    code: "BULK_INSERTION_ERROR".to_string(),
                    details: Some("Failed to perform bulk insertion".to_string()),
                }),
            ))
        }
    }
}

async fn search_handler(
    State(svc): State<SharedService>,
    Json(payload): Json<SearchReq>,
) -> Result<Json<Vec<SearchRes>>, (StatusCode, Json<ErrorRes>)> {
    // Get dimension from service
    let expected_dim = {
        let svc_guard = svc.lock().unwrap();
        svc_guard.dimension()
    };

    // Validate vector dimension
    if let Err(msg) = validate_vector_dimension(&payload.vector, expected_dim) {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(ErrorRes {
                error: msg,
                code: "INVALID_DIMENSION".to_string(),
                details: Some(format!("Expected {} dimensions", expected_dim)),
            }),
        ));
    }

    if payload.k == 0 || payload.k > 1000 {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(ErrorRes {
                error: "k must be between 1 and 1000".to_string(),
                code: "INVALID_K_VALUE".to_string(),
                details: Some(format!("Received k={}", payload.k)),
            }),
        ));
    }

    let start = std::time::Instant::now();
    let svc = svc.lock().unwrap();
    let q = Vector::new(payload.vector);
    let results = svc.search(&q, payload.k, &payload.filter);
    let latency = start.elapsed().as_secs_f64() * 1000.0; // ms

    // Update metrics
    unsafe {
        SEARCH_COUNT += 1;
        SEARCH_LATENCY_SUM += latency;
    }

    let out = results.into_iter()
        .map(|(id, score)| SearchRes { id, score })
        .collect();
    Ok(Json(out))
}

async fn bulk_search_handler(
    State(svc): State<SharedService>,
    Json(payload): Json<BulkSearchReq>,
) -> Result<Json<BulkSearchRes>, (StatusCode, Json<ErrorRes>)> {
    if payload.queries.is_empty() {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(ErrorRes {
                error: "Empty query list".to_string(),
                code: "EMPTY_BULK_REQUEST".to_string(),
                details: Some("At least one query is required".to_string()),
            }),
        ));
    }

    if payload.queries.len() > MAX_BULK_QUERIES {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(ErrorRes {
                error: format!("Too many queries: {}", payload.queries.len()),
                code: "TOO_MANY_QUERIES".to_string(),
                details: Some(format!("Maximum {} queries per request", MAX_BULK_QUERIES)),
            }),
        ));
    }

    // Get dimension from service
    let expected_dim = {
        let svc_guard = svc.lock().unwrap();
        svc_guard.dimension()
    };

    let start = std::time::Instant::now();
    let svc = svc.lock().unwrap();
    let mut all_results = Vec::new();

    for query in payload.queries.iter() {
        // Validate each query
        if let Err(_) = validate_vector_dimension(&query.vector, expected_dim) {
            all_results.push(Vec::new()); // Return empty for invalid queries
            continue;
        }

        if query.k == 0 || query.k > 1000 {
            all_results.push(Vec::new()); // Return empty for invalid k
            continue;
        }

        let q = Vector::new(query.vector.clone());
        let results = svc.search(&q, query.k, &query.filter);
        let search_res = results.into_iter()
            .map(|(id, score)| SearchRes { id, score })
            .collect();
        all_results.push(search_res);
    }

    let latency = start.elapsed().as_secs_f64() * 1000.0;
    unsafe {
        SEARCH_COUNT += payload.queries.len() as u64;
        SEARCH_LATENCY_SUM += latency;
    }

    Ok(Json(BulkSearchRes { results: all_results }))
}

async fn snapshot_handler(
    State(svc): State<SharedService>,
) -> Result<Json<SnapshotRes>, (StatusCode, Json<ErrorRes>)> {
    let svc = svc.lock().unwrap();
    match svc.snapshot() {
        Ok(_) => Ok(Json(SnapshotRes { 
            success: true, 
            message: "Snapshot created successfully".to_string(),
        })),
        Err(e) => Err((
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ErrorRes {
                error: e.to_string(),
                code: "SNAPSHOT_FAILED".to_string(),
                details: None,
            }),
        )),
    }
}

async fn health_handler(
    State(svc): State<SharedService>,
) -> Json<HealthRes> {
    let svc = svc.lock().unwrap();
    let vector_count = svc.list_ids().unwrap_or_default().len();
    
    Json(HealthRes {
        status: "healthy".to_string(),
        version: "0.1.0".to_string(),
        uptime_seconds: 0, // TODO: track actual uptime
        vector_count,
        index_type: svc.index_type().to_string(),
        max_request_size_mb: MAX_REQUEST_SIZE_MB as f32,
    })
}

async fn metrics_handler(
    State(svc): State<SharedService>,
) -> Json<MetricsRes> {
    let svc = svc.lock().unwrap();
    let vector_count = svc.list_ids().unwrap_or_default().len();
    
    let (search_count, insert_count, avg_latency) = unsafe {
        let avg = if SEARCH_COUNT > 0 {
            SEARCH_LATENCY_SUM / SEARCH_COUNT as f64
        } else {
            0.0
        };
        (SEARCH_COUNT, INSERT_COUNT, avg)
    };

    Json(MetricsRes {
        total_vectors: vector_count,
        total_searches: search_count,
        total_inserts: insert_count,
        avg_search_latency_ms: avg_latency,
        memory_usage_mb: 0.0, // TODO: get actual memory usage
        max_batch_size: MAX_BATCH_SIZE,
    })
}

fn create_router(shared_service: SharedService) -> Router {
    Router::new()
        // Core operations
        .route("/vectors", post(add_handler))
        .route("/vectors/bulk", post(bulk_add_handler))
        .route("/search", post(search_handler))
        .route("/search/bulk", post(bulk_search_handler))
        // Management
        .route("/snapshot", post(snapshot_handler))
        .route("/health", get(health_handler))
        .route("/metrics", get(metrics_handler))
        .layer(
            ServiceBuilder::new()
                .layer(RequestBodyLimitLayer::new(MAX_REQUEST_SIZE_MB * 1024 * 1024)) // 100MB limit
                .layer(TraceLayer::new_for_http())
        )
        .with_state(shared_service)
}

pub async fn serve(path: String, dim: usize, use_hnsw: bool, addr: SocketAddr) -> Result<()> {
    // Don't initialize logging here - let the CLI handle it

    // Build service
    let service = Service::new(&path, dim, use_hnsw)?;
    let shared = Arc::new(Mutex::new(service));

    // Build router with state
    let app = create_router(shared);

    // Create listener
    let listener = tokio::net::TcpListener::bind(&addr).await?;
    
    let engine_type = if use_hnsw { "HNSW" } else { "Flat" };
    println!("NusterDB server listening on {} using {} index", addr, engine_type);
    println!("Configuration:");
    println!("  - Max request size: {}MB", MAX_REQUEST_SIZE_MB);
    println!("  - Max batch size: {} vectors", MAX_BATCH_SIZE);
    println!("  - Max bulk queries: {} queries", MAX_BULK_QUERIES);
    println!("Available endpoints:");
    println!("  POST /vectors        - Add single vector");
    println!("  POST /vectors/bulk   - Add multiple vectors (max {})", MAX_BATCH_SIZE);
    println!("  POST /search         - Search single query");
    println!("  POST /search/bulk    - Search multiple queries (max {})", MAX_BULK_QUERIES);
    println!("  POST /snapshot       - Create index snapshot");
    println!("  GET  /health         - Health check");
    println!("  GET  /metrics        - Performance metrics");
    
    // Run server with new axum API
    axum::serve(listener, app).await?;
    
    Ok(())
}

/// Serve with a pre-configured service instance
pub async fn serve_with_service(service: Service, addr: SocketAddr) -> Result<()> {
    // Don't initialize logging here - let the CLI handle it

    let shared = Arc::new(Mutex::new(service));

    // Build router with state
    let app = create_router(shared.clone());

    // Create listener
    let listener = tokio::net::TcpListener::bind(&addr).await?;
    
    // Get service info for logging
    let (engine_type, dimension) = {
        let svc = shared.lock().unwrap();
        (svc.index_type().to_string(), svc.dimension())
    };
    
    println!("NusterDB server listening on {} using {} index ({}D vectors)", addr, engine_type, dimension);
    println!("Configuration:");
    println!("  - Max request size: {}MB", MAX_REQUEST_SIZE_MB);
    println!("  - Max batch size: {} vectors", MAX_BATCH_SIZE);
    println!("  - Max bulk queries: {} queries", MAX_BULK_QUERIES);
    println!("Available endpoints:");
    println!("  POST /vectors        - Add single vector");
    println!("  POST /vectors/bulk   - Add multiple vectors (max {})", MAX_BATCH_SIZE);
    println!("  POST /search         - Search single query");
    println!("  POST /search/bulk    - Search multiple queries (max {})", MAX_BULK_QUERIES);
    println!("  POST /snapshot       - Create index snapshot");
    println!("  GET  /health         - Health check");
    println!("  GET  /metrics        - Performance metrics");
    
    // Run server with new axum API
    axum::serve(listener, app).await?;
    
    Ok(())
}