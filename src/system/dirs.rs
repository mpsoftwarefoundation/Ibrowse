use pyo3::{PyResult, pyfunction};

// Retrieve the config dir of Ibrowse (.../ibrowse)
#[pyfunction]
pub fn config_dir() -> PyResult<String> {
    let config_dir = dirs::config_dir()
        .unwrap_or_else(|| std::env::temp_dir())
        .join("ibrowse");

    Ok(config_dir.to_string_lossy().into_owned())
}

// Retrieve the cache dir of Ibrowse (.../ibrowse/cache)
#[pyfunction]
pub fn cache_dir() -> PyResult<String> {
    let config_dir = dirs::cache_dir()
        .unwrap_or_else(|| std::env::temp_dir())
        .join("ibrowse")
        .join("cache");

    Ok(config_dir.to_string_lossy().into_owned())
}
