use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::exceptions::{PyValueError, PyRuntimeError};
use std::collections::HashMap;

/// Simple Python wrapper for a vector
#[pyclass]
#[derive(Clone)]
pub struct Vector {
    data: Vec<f32>,
}

#[pymethods]
impl Vector {
    #[new]
    fn new(data: Vec<f32>) -> PyResult<Self> {
        if data.is_empty() {
            return Err(PyValueError::new_err("Vector must have at least one dimension"));
        }
        Ok(Vector { data })
    }
    
    fn __repr__(&self) -> String {
        format!("Vector({})", 
            self.data.iter()
                .map(|x| format!("{:.3}", x))
                .collect::<Vec<_>>()
                .join(", ")
        )
    }
    
    #[getter]
    fn data(&self) -> Vec<f32> {
        self.data.clone()
    }
    
    fn len(&self) -> usize {
        self.data.len()
    }
}

/// Simple database configuration
#[pyclass]
#[derive(Clone)]
pub struct DatabaseConfig {
    #[pyo3(get, set)]
    pub dim: usize,
    #[pyo3(get, set)]
    pub path: String,
}

#[pymethods]
impl DatabaseConfig {
    #[new]
    fn new(dim: usize, path: String) -> Self {
        DatabaseConfig { dim, path }
    }
}

/// Simple NusterDB implementation
#[pyclass]
pub struct NusterDB {
    config: DatabaseConfig,
    vectors: HashMap<usize, Vector>,
    next_id: usize,
}

#[pymethods]
impl NusterDB {
    #[new]
    fn new(config: DatabaseConfig) -> PyResult<Self> {
        Ok(NusterDB {
            config,
            vectors: HashMap::new(),
            next_id: 0,
        })
    }
    
    /// Insert a vector
    fn insert(&mut self, vector: Vector) -> PyResult<usize> {
        if vector.data.len() != self.config.dim {
            return Err(PyValueError::new_err(
                format!("Vector dimension {} doesn't match config dimension {}", 
                    vector.data.len(), self.config.dim)
            ));
        }
        
        let id = self.next_id;
        self.vectors.insert(id, vector);
        self.next_id += 1;
        Ok(id)
    }
    
    /// Get a vector by ID
    fn get(&self, id: usize) -> PyResult<Option<Vector>> {
        Ok(self.vectors.get(&id).cloned())
    }
    
    /// Search for k nearest neighbors (simple brute force)
    fn search(&self, query: &Vector, k: usize) -> PyResult<Vec<(usize, f32)>> {
        if query.data.len() != self.config.dim {
            return Err(PyValueError::new_err("Query vector dimension mismatch"));
        }
        
        let mut distances = Vec::new();
        
        for (id, vector) in &self.vectors {
            let dist = euclidean_distance(&query.data, &vector.data);
            distances.push((*id, dist));
        }
        
        distances.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
        distances.truncate(k);
        
        Ok(distances)
    }
    
    /// Delete a vector
    fn delete(&mut self, id: usize) -> PyResult<bool> {
        Ok(self.vectors.remove(&id).is_some())
    }
    
    /// Get total count
    fn count(&self) -> usize {
        self.vectors.len()
    }
    
    fn __repr__(&self) -> String {
        format!("NusterDB(dim={}, vectors={})", 
            self.config.dim, 
            self.vectors.len()
        )
    }
}

/// Simple euclidean distance calculation
fn euclidean_distance(a: &[f32], b: &[f32]) -> f32 {
    a.iter()
        .zip(b.iter())
        .map(|(x, y)| (x - y).powi(2))
        .sum::<f32>()
        .sqrt()
}

/// Python module definition
#[pymodule]
fn nusterdb(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Vector>()?;
    m.add_class::<DatabaseConfig>()?;
    m.add_class::<NusterDB>()?;
    
    // Add version
    m.add("__version__", "0.1.0")?;
    
    Ok(())
}
