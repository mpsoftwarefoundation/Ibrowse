use crate::system;
use pyo3::{PyResult, pyfunction};
use std::collections::HashMap;

// Get passwords (as a Python dict '{url, [username, password]}')
#[pyfunction]
pub fn passwords() -> PyResult<HashMap<String, [String; 2]>> {
    let config = system::file_ops::load_config();

    Ok(config.passwords)
}

// Get bookmarks (as a Python dict '{url, name}')
#[pyfunction]
pub fn bookmarks() -> PyResult<HashMap<String, String>> {
    let config = system::file_ops::load_config();

    Ok(config.bookmarks)
}

// Get previous tabs (as a Python list '[url]')
#[pyfunction]
pub fn previous_tabs() -> PyResult<Vec<String>> {
    let config = system::file_ops::load_config();

    Ok(config.previous_tabs)
}

// Get preferred browser (as a Python string '[browser_name]')
#[pyfunction]
pub fn preferred_browser() -> PyResult<String> {
    let config = system::file_ops::load_config();

    Ok(config.preferred_browser)
}

// Get smooth scrolling enabled
#[pyfunction]
pub fn smooth_scrolling_enabled() -> PyResult<bool> {
    let config = system::file_ops::load_config();

    Ok(config.smooth_scrolling)
}
