use pyo3::{pyfunction, PyResult};
use crate::system::file_ops;

// Set the previous tabs array to a Python list ('[url]')
#[pyfunction]
pub fn set_previous_tabs(tabs: Vec<String>) -> PyResult<()> {
    let mut config = file_ops::load_config();
    config.previous_tabs = tabs;

    file_ops::save_config(&config);
    Ok(())
}

// Set the preferred browser to a Python string ('[browser_name]')
#[pyfunction]
pub fn set_preferred_browser(browser: String) -> PyResult<()> {
    let mut config = file_ops::load_config();
    config.preferred_browser = browser;

    file_ops::save_config(&config);
    Ok(())
}

// Set smooth scrolling enabled
#[pyfunction]
pub fn set_smooth_scrolling(enabled: bool) -> PyResult<()> {
    let mut config = file_ops::load_config();
    config.smooth_scrolling = enabled;

    file_ops::save_config(&config);
    Ok(())
}