use pyo3::{pyfunction, PyResult};
use crate::system;

// Append a password object with url, username, and password to config.json
#[pyfunction]
pub fn add_password(url: &str, username: &str, password: &str) -> PyResult<()> {
    let mut config = system::file_ops::load_config();
    let array = [username.to_string(), password.to_string()];
    config.passwords.insert(url.to_string(), array);

    system::file_ops::save_config(&config);
    Ok(())
}

// Remove a password object with specified url from config.json
#[pyfunction]
pub fn remove_password(url: &str) -> PyResult<()> {
    let mut config = system::file_ops::load_config();
    config.passwords.remove(url);

    system::file_ops::save_config(&config);
    Ok(())
}