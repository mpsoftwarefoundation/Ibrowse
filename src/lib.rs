use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
mod system;
mod user;

// Test function to test if the bindings are correct
#[pyfunction]
fn test() -> PyResult<()> {
    println!("Hello from Rust!");

    Ok(())
}

// Define the module and wrap functions
#[pymodule]
fn ibrowse(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(test, m)?)?;
    m.add_function(wrap_pyfunction!(user::data::passwords, m)?)?;
    m.add_function(wrap_pyfunction!(user::data::bookmarks, m)?)?;
    m.add_function(wrap_pyfunction!(user::data::previous_tabs, m)?)?;
    m.add_function(wrap_pyfunction!(user::data::preferred_browser, m)?)?;
    m.add_function(wrap_pyfunction!(user::data::smooth_scrolling_enabled, m)?)?;
    m.add_function(wrap_pyfunction!(user::passwords::add_password, m)?)?;
    m.add_function(wrap_pyfunction!(user::passwords::remove_password, m)?)?;
    m.add_function(wrap_pyfunction!(user::bookmarks::add_bookmark, m)?)?;
    m.add_function(wrap_pyfunction!(user::bookmarks::remove_bookmark, m)?)?;
    m.add_function(wrap_pyfunction!(user::settings::set_previous_tabs, m)?)?;
    m.add_function(wrap_pyfunction!(user::settings::set_preferred_browser, m)?)?;
    m.add_function(wrap_pyfunction!(user::settings::set_smooth_scrolling, m)?)?;
    m.add_function(wrap_pyfunction!(system::dirs::config_dir, m)?)?;
    m.add_function(wrap_pyfunction!(system::dirs::cache_dir, m)?)?;
    m.add_function(wrap_pyfunction!(system::file_ops::read_html, m)?)?;
    m.add_function(wrap_pyfunction!(system::file_ops::write_html, m)?)?;
    m.add_function(wrap_pyfunction!(system::file_ops::write_bytes, m)?)?;

    Ok(())
}
