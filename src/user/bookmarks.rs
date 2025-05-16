use pyo3::{pyfunction, PyResult};
use crate::system;

// Append a bookmark object with url and bookmark name to config.json
#[pyfunction]
pub fn add_bookmark(url: &str, name: &str) -> PyResult<()> {
    let mut config = system::file_ops::load_config();
    config.bookmarks.insert(url.to_string(), name.to_string());

    system::file_ops::save_config(&config);
    Ok(())
}

// Remove a bookmark object with the specified bookmark name from config.json
#[pyfunction]
pub fn remove_bookmark(name: &str) -> PyResult<()> {
    let mut config = system::file_ops::load_config();
    config.bookmarks.remove(name);

    system::file_ops::save_config(&config);
    Ok(())
}