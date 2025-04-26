use pyo3::prelude::*;

#[pyfunction]
pub fn clear_caches() -> PyResult<()> {
    let mut cache_dir = dirs::config_dir()
        .unwrap_or_else(|| std::env::temp_dir())
        .join("ibrowse");
    cache_dir.join("cache");

    for entry in std::fs::read_dir(cache_dir.to_str())? {
        let entry = entry?;
        std::fs::remove_file(entry.path())?;
    }

    Ok(())
}